"""Data A pose_stamped publisher — reference stub for cross-team integration.

Lets Data B (and Cloud) develop against Data A's pose stream **today**, with no
real robot and no running locomotion stack. It synthesizes a plausible hexapod
odometry trajectory (slow forward tripod walk with a gentle turn) and emits
`pose_stamped` messages (see pose_stamped.schema.json).

Two modes:

  # 1) Record a deterministic sample file Data B can replay:
  python interfaces/pose_publisher.py --record 200 --start-ms 1781000000000 \
         --out interfaces/sample_pose_stream.jsonl

  # 2) Live-publish to MQTT at 50 Hz (needs `pip install paho-mqtt`):
  python interfaces/pose_publisher.py --mqtt --host localhost \
         --topic robogreeno/data-a/spider-01/pose

Conventions: epoch-ms timestamps, body frame +X fwd/+Y left/+Z up, metres,
radians, quaternion [w,x,y,z]. Trajectory params are read from the single
source-of-truth geometry in ShiriStern/wave-walk/config.py.
"""
import argparse
import json
import math
import os
import sys
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


def main():
    ap = argparse.ArgumentParser(description="Data A pose_stamped publisher stub")
    ap.add_argument("--record", type=int, metavar="N", help="write N messages to --out and exit")
    ap.add_argument("--out", default="interfaces/sample_pose_stream.jsonl")
    ap.add_argument("--start-ms", type=int, default=None, help="epoch-ms of first message (default: now)")
    ap.add_argument("--mqtt", action="store_true", help="live-publish to MQTT at 50 Hz")
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
