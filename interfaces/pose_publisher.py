"""Data A pose_stamped publisher — reference stub for cross-team integration.

Lets Data B (and Cloud) develop against Data A's pose stream **today**, with no
real robot and no running locomotion stack. It synthesizes a plausible hexapod
odometry trajectory (slow forward tripod walk with a gentle turn) and emits
`pose_stamped` messages (see pose_stamped.schema.json).

Three modes (pub/sub is NOT the only access pattern):

  # 1) Record a deterministic sample file Data B can replay:
  python interfaces/pose_publisher.py --record 200 --start-ms 1781000000000 \
         --out interfaces/sample_pose_stream.jsonl

  # 2) Live-publish to MQTT at 50 Hz (needs `pip install paho-mqtt`):
  python interfaces/pose_publisher.py --mqtt --host localhost \
         --topic robogreeno/data-a/spider-01/pose

  # 3) Serve synchronous "freshest pose now" over MQTT request/reply, so Data B
  #    pulls pose only for the frames it processes — no 50 Hz subscription:
  python interfaces/pose_publisher.py --serve --host localhost

  # 4) Data B side: pull ONE freshest pose (run against a broker where --serve runs):
  python interfaces/pose_publisher.py --get --host localhost

For a co-located caller (e.g. Embedded stamping a frame at capture), import
`get_latest_pose()` for the same freshest-pose snapshot with no broker at all.
Data B's MQTT client is `request_latest_pose()`. These cover INTEGRATION.md §2
delivery option (c): "synchronous freshest-pose pull".

Conventions: epoch-ms timestamps, body frame +X fwd/+Y left/+Z up, metres,
radians, quaternion [w,x,y,z]. Trajectory params are read from the single
source-of-truth geometry in ShiriStern/wave-walk/config.py.
"""
import argparse
import itertools
import json
import math
import os
import sys
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ShiriStern", "wave-walk"))
import config as C  # noqa: E402

ROBOT_ID = "spider-01"
DT_S = 0.020                      # 50 Hz control loop
V_FWD = C.GAIT_STRIDE / C.GAIT_PERIOD   # forward speed from gait (~0.043 m/s)
YAW_RATE = 0.05                  # rad/s gentle left turn, for an interesting path
# tripod groups -> which of the 6 legs (FL,ML,BL,BR,MR,FR order) are down
TRIPOD_A = set(C.TRIPOD_A)       # [0,2,4]
TRIPOD_B = set(C.TRIPOD_B)       # [1,3,5]


def yaw_to_quat(theta):
    return [math.cos(theta / 2.0), 0.0, 0.0, math.sin(theta / 2.0)]


def stability(contacts, ang_z):
    """Static-stability summary for the `stability` block (Data B's IQA).

    `stable` = at least 3 feet down, low body angular rate, and the CoM
    (body centre, here the origin) inside the support polygon. `margin_deg`
    is the tip-over margin: the angle the body could tilt about the nearest
    support-polygon edge before the CoM projection leaves it -- larger is
    safer, ~0 is on the verge. Derived from the same signals every consumer
    already has, so Data B does not have to know the gait internals."""
    n = sum(contacts)
    feet = [(C.STANCE_RADIUS * math.cos(C.LEGS[i][1]),
             C.STANCE_RADIUS * math.sin(C.LEGS[i][1]))
            for i, c in enumerate(contacts) if c]
    margin_m = _support_margin(0.0, 0.0, feet) if n >= 3 else 0.0
    margin_deg = math.degrees(math.atan2(margin_m, C.STANCE_HEIGHT))
    stable = bool(n >= 3 and abs(ang_z) < 0.5 and margin_m > 0.0)
    return {"stable": stable, "support_feet": n, "margin_deg": round(margin_deg, 2)}


def _support_margin(px, py, feet):
    """Signed distance from (px,py) to the support polygon of `feet`.

    Positive = inside, and equal to the perpendicular distance to the nearest
    edge (the static-stability margin). Zero or negative = on/outside the
    polygon (unstable). Feet are ordered CCW about their centroid first."""
    cx = sum(f[0] for f in feet) / len(feet)
    cy = sum(f[1] for f in feet) / len(feet)
    poly = sorted(feet, key=lambda f: math.atan2(f[1] - cy, f[0] - cx))
    best, inside = float("inf"), True
    for i in range(len(poly)):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % len(poly)]
        ex, ey = bx - ax, by - ay
        cross = ex * (py - ay) - ey * (px - ax)          # >0 = left of edge (inside, CCW)
        if cross < 0:
            inside = False
        best = min(best, abs(cross) / math.hypot(ex, ey))
    return best if inside else 0.0


def make_message(seq, stamp_ms, x, y, theta, phase):
    a_down = phase < 0.5
    down = TRIPOD_A if a_down else TRIPOD_B
    contacts = [i in down for i in range(6)]
    z = C.STANCE_HEIGHT + 0.003 * math.sin(2 * math.pi * phase)   # slight body bob
    quat = yaw_to_quat(theta)
    msg = {
        "schema": "robo-greeno/data-a/pose_stamped",
        "version": 1,
        "robot_id": ROBOT_ID,
        "stamp_ms": int(stamp_ms),
        "seq": seq,
        "frame": "body",
        "odom_frame": "odom",
        "pose": {
            "position_m": [round(x, 4), round(y, 4), round(z, 4)],
            "orientation_quat": [round(q, 5) for q in quat],
        },
        "twist": {
            "linear_mps": [round(V_FWD, 4), 0.0, 0.0],
            "angular_rps": [0.0, 0.0, YAW_RATE],
        },
        "imu": {
            "accel_mps2": [round(0.02 * math.sin(seq * 0.3), 4), 0.0, 9.79],
            "gyro_rps": [0.0, 0.0, YAW_RATE],
            "orientation_quat": [round(q, 5) for q in quat],
        },
        "gait": {"name": "tripod", "phase": round(phase, 3)},
        "foot_contacts": contacts,
        "stability": stability(contacts, YAW_RATE),
        "node_id": f"n{int(x / 0.5):d}",   # coarse 0.5 m grid -> Cloud graph node
    }
    return msg


def stream(n, start_ms):
    """Yield n messages of a forward tripod walk with a gentle turn."""
    x = y = theta = 0.0
    for seq in range(n):
        t = seq * DT_S
        phase = (t / C.GAIT_PERIOD) % 1.0
        stamp_ms = start_ms + int(t * 1000)
        yield make_message(seq, stamp_ms, x, y, theta, phase)
        # integrate odometry for next step
        theta += YAW_RATE * DT_S
        x += V_FWD * math.cos(theta) * DT_S
        y += V_FWD * math.sin(theta) * DT_S


class PoseSource:
    """Holds the freshest pose, exactly like the real locomotion stack.

    The 50 Hz control loop keeps one current pose in process; a synchronous
    ``latest()`` call returns it with no queue and no subscription. This is the
    in-process side of INTEGRATION.md §2 delivery option (c): "freshest pose now".
    Here a background thread synthesizes the walk so callers can develop with no
    robot; in the real stack ``latest()`` just reads the controller's state.
    """

    def __init__(self):
        self._seq = 0
        self._x = self._y = self._theta = 0.0
        self._lock = threading.Lock()

    def step(self):
        """Advance the odometry one 50 Hz tick (driven by the control loop)."""
        with self._lock:
            self._theta += YAW_RATE * DT_S
            self._x += V_FWD * math.cos(self._theta) * DT_S
            self._y += V_FWD * math.sin(self._theta) * DT_S
            self._seq += 1

    def run(self, stop=None):
        """Tick the odometry at 50 Hz until ``stop`` (a threading.Event) is set."""
        while stop is None or not stop.is_set():
            self.step()
            time.sleep(DT_S)

    def latest(self):
        """Freshest ``pose_stamped`` now — synchronous, no subscribe.

        Returns a pure, schema-valid ``pose_stamped`` whose ``stamp_ms`` is when
        this pose was produced. The caller binds it to a frame's capture instant
        and rejects the pair if ``|frame_stamp_ms - stamp_ms|`` exceeds its skew
        budget (e.g. 50 ms) — the pose is bound to capture, not to inference time.
        """
        with self._lock:
            t = self._seq * DT_S
            phase = (t / C.GAIT_PERIOD) % 1.0
            return make_message(self._seq, int(time.time() * 1000),
                                self._x, self._y, self._theta, phase)


_DEFAULT_SOURCE = None


def get_latest_pose():
    """In-process synchronous "freshest pose now" — INTEGRATION.md §2 option (c).

    A co-located caller (e.g. Embedded stamping a frame at capture) gets the
    current pose with zero queue/subscription/broker. Backed by a lazily-started
    50 Hz simulation here; in the real stack this reads the locomotion controller.
    """
    global _DEFAULT_SOURCE
    if _DEFAULT_SOURCE is None:
        _DEFAULT_SOURCE = PoseSource()
        threading.Thread(target=_DEFAULT_SOURCE.run, daemon=True).start()
    return _DEFAULT_SOURCE.latest()


def serve(host, port, topic):
    """MQTT request/reply: reply with the freshest pose on each request.

    Request topic:  ``<topic>/get``   payload (optional JSON):
        {"reply_topic": "..."}
    Reply  topic:  the request's ``reply_topic``, else ``<topic>/latest``.
    The reply is a pure ``pose_stamped``; for correlation, request a per-frame
    ``reply_topic`` (e.g. ``.../pose/latest/<frame_id>``). Data B publishes one
    request per frame it processes — no 50 Hz subscription.
    """
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        sys.exit("paho-mqtt not installed:  pip install paho-mqtt")

    src = PoseSource()
    threading.Thread(target=src.run, daemon=True).start()
    req_topic = f"{topic}/get"
    default_reply = f"{topic}/latest"

    def on_message(client, _userdata, m):
        reply_topic = default_reply
        if m.payload:
            try:
                reply_topic = json.loads(m.payload).get("reply_topic", default_reply)
            except (ValueError, AttributeError):
                pass
        msg = src.latest()
        client.publish(reply_topic, json.dumps(msg, separators=(",", ":")), qos=0)

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(host, port, 60)
    client.subscribe(req_topic, qos=0)
    print(f"serving freshest pose: reply to requests on mqtt://{host}:{port}/{req_topic} "
          f"(reply -> {default_reply}; Ctrl-C to stop)")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nstopped")


_REQ_SEQ = itertools.count()


def request_latest_pose(host="localhost", port=1883, topic=None,
                        timeout_ms=100, reply_topic=None):
    """Data B side of option (c): pull the freshest pose over MQTT request/reply.

    Publishes one request to ``<topic>/get`` and blocks until Data A's ``serve()``
    replies, or ``timeout_ms`` elapses. Returns the ``pose_stamped`` dict, or
    ``None`` on timeout. Call this **at frame-capture time** and bind the result
    to the frame's own ``stamp_ms``: reject the pair if
    ``abs(frame_stamp_ms - pose['stamp_ms'])`` exceeds your skew budget (e.g.
    50 ms), so the pose is bound to capture, not to inference time. One request
    per frame Data B processes — no 50 Hz subscription.
    """
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        sys.exit("paho-mqtt not installed:  pip install paho-mqtt")

    topic = topic or f"robogreeno/data-a/{ROBOT_ID}/pose"
    # unique reply topic per call so concurrent callers never cross-talk
    reply_topic = reply_topic or f"{topic}/latest/{os.getpid()}-{next(_REQ_SEQ)}"
    box = {}
    done = threading.Event()

    def on_message(_client, _userdata, m):
        try:
            box["pose"] = json.loads(m.payload)
        except ValueError:
            box["pose"] = None
        done.set()

    client = mqtt.Client()
    client.on_message = on_message
    client.connect(host, port, 60)
    client.subscribe(reply_topic, qos=0)        # register before we ask, same ordered conn
    client.loop_start()
    client.publish(f"{topic}/get", json.dumps({"reply_topic": reply_topic}), qos=0)
    got = done.wait(timeout_ms / 1000.0)
    client.loop_stop()
    client.disconnect()
    return box.get("pose") if got else None


def main():
    ap = argparse.ArgumentParser(description="Data A pose_stamped publisher stub")
    ap.add_argument("--record", type=int, metavar="N", help="write N messages to --out and exit")
    ap.add_argument("--out", default="interfaces/sample_pose_stream.jsonl")
    ap.add_argument("--start-ms", type=int, default=None, help="epoch-ms of first message (default: now)")
    ap.add_argument("--mqtt", action="store_true", help="live-publish to MQTT at 50 Hz")
    ap.add_argument("--serve", action="store_true",
                    help="serve synchronous 'freshest pose now' over MQTT request/reply")
    ap.add_argument("--get", action="store_true",
                    help="Data B demo: pull ONE freshest pose via request/reply and print it")
    ap.add_argument("--timeout-ms", type=int, default=100, help="--get reply timeout")
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=1883)
    ap.add_argument("--topic", default=f"robogreeno/data-a/{ROBOT_ID}/pose")
    args = ap.parse_args()

    start_ms = args.start_ms if args.start_ms is not None else int(time.time() * 1000)

    if args.record:
        with open(args.out, "w") as f:
            for msg in stream(args.record, start_ms):
                f.write(json.dumps(msg, separators=(",", ":")) + "\n")
        print(f"wrote {args.record} messages to {args.out}")
        return

    if args.serve:
        serve(args.host, args.port, args.topic)
        return

    if args.get:
        pose = request_latest_pose(args.host, args.port, args.topic, args.timeout_ms)
        if pose is None:
            sys.exit(f"no reply within {args.timeout_ms} ms (is `--serve` running on this broker?)")
        print(json.dumps(pose))
        return

    if args.mqtt:
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            sys.exit("paho-mqtt not installed:  pip install paho-mqtt")
        client = mqtt.Client()
        client.connect(args.host, args.port, 60)
        client.loop_start()
        print(f"publishing 50 Hz to mqtt://{args.host}:{args.port}/{args.topic} (Ctrl-C to stop)")
        seq = 0
        x = y = theta = 0.0
        try:
            while True:
                t = seq * DT_S
                phase = (t / C.GAIT_PERIOD) % 1.0
                msg = make_message(seq, int(time.time() * 1000), x, y, theta, phase)
                client.publish(args.topic, json.dumps(msg, separators=(",", ":")), qos=0)
                theta += YAW_RATE * DT_S
                x += V_FWD * math.cos(theta) * DT_S
                y += V_FWD * math.sin(theta) * DT_S
                seq += 1
                time.sleep(DT_S)
        except KeyboardInterrupt:
            client.loop_stop()
            print(f"\nstopped after {seq} messages")
        return

    # default: print 5 sample messages to stdout
    for msg in stream(5, start_ms):
        print(json.dumps(msg))


if __name__ == "__main__":
    main()
