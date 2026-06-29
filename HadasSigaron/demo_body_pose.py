"""
demo_pose_wave.py  --  Robo-Greeno hexapod demo: stand, pose, and wave.

The robot stands, crouches low, rises up tall, then lifts its
front-left leg high and waves it side to side. Every pose is just
six foot targets fed through the inverse kinematics -- there is no
gait and no walking here, only posing.

This is a good first demo: it is simple, it is visual, and it makes
the point that one solver drives the whole robot.

Run it
------
  pip install mujoco
  python demo_pose_wave.py          # open the 3D viewer
  python demo_pose_wave.py --check  # headless self-test, no display
"""

import argparse
import math
import sys
import time
import numpy as np

import config as cfg
import hexapod_ik as ik
import hexapod_model as model


# --------------------------------------------------------------------
# MuJoCo plumbing -- builds the robot and lets us pose it
# --------------------------------------------------------------------
def make_sim():
    import mujoco
    m = mujoco.MjModel.from_xml_string(model.build_mjcf())
    return mujoco, m, mujoco.MjData(m)


def _aid(mj, m, name):
    return mj.mj_name2id(m, mj.mjtObj.mjOBJ_ACTUATOR, name)


def _jadr(mj, m, name):
    return m.jnt_qposadr[mj.mj_name2id(m, mj.mjtObj.mjOBJ_JOINT, name)]


def init_stance(mj, m, d):
    """Start the robot already standing so it does not snap on spawn."""
    mj.mj_resetData(m, d)
    t = _jadr(mj, m, "trunk")
    d.qpos[t:t + 7] = [0, 0, cfg.STANCE_HEIGHT, 1, 0, 0, 0]
    for (name, mount), tgt in zip(cfg.LEGS, ik.default_stance()):
        coxa, femur, tibia = ik.leg_ik(*ik.body_target_to_leg(tgt, mount))
        for joint, val in (("coxa", coxa), ("femur", femur), ("tibia", tibia)):
            d.qpos[_jadr(mj, m, f"{name}_{joint}")] = val
    mj.mj_forward(m, d)


def command(mj, m, d, foot_targets):
    """Solve the IK for six foot targets and write the eighteen servos."""
    for (name, _), (coxa, femur, tibia) in zip(cfg.LEGS, ik.solve_all(foot_targets)):
        d.ctrl[_aid(mj, m, f"{name}_coxa")] = coxa
        d.ctrl[_aid(mj, m, f"{name}_femur")] = femur
        d.ctrl[_aid(mj, m, f"{name}_tibia")] = tibia

def world_feet():
    """The six feet, fixed on the ground in WORLD coordinates.

    These never move -- only the body does. The IK solves for each
    foot SITE (the tibia tip / sphere centre), and a resting foot's
    centre sits one FOOT_RADIUS above the ground, so its z is
    FOOT_RADIUS, not 0. Using 0 here would command every foot one
    radius too low and make the body lurch off its standing stance."""
    R = cfg.STANCE_RADIUS
    return [
        (R * math.cos(mount),
         R * math.sin(mount),
         cfg.FOOT_RADIUS)
        for name, mount in cfg.LEGS
    ]

def body_pose_targets(height, pitch, roll):
    """Fixed feet in the world, moving body."""

    cp = math.cos(pitch)
    sp = -math.sin(pitch)

    cr = math.cos(roll)
    sr = math.sin(roll)

    targets = []

    for px, py, pz in world_feet():

        # p - body_centre
        x = px
        y = py
        z = pz - height 

        # R_body^T = R_pitch^T * R_roll^T

        # inverse roll (about X)
        x1 = x
        y1 = y * cr + z * sr
        z1 = -y * sr + z * cr

        # inverse pitch (about Y)
        x2 = x1 * cp - z1 * sp
        y2 = y1
        z2 = x1 * sp + z1 * cp

        targets.append((x2, y2, z2))

    return targets


# --------------------------------------------------------------------
# The demo  --  this is the part you own
# --------------------------------------------------------------------

_KEYS = [
    (0.0,  cfg.STANCE_HEIGHT,        0.0,               0.0,              "neutral"),
    (3.0,  cfg.STANCE_HEIGHT + 0.02, 0.0,               0.0,              "up"),
    (6.0,  cfg.STANCE_HEIGHT - 0.02, 0.0,               0.0,              "down"),
    (9.0,  cfg.STANCE_HEIGHT,        math.radians(4),   0.0,              "pitch forward"),
    (12.0, cfg.STANCE_HEIGHT,        math.radians(-8),  0.0,              "pitch back"),
    (15.0, cfg.STANCE_HEIGHT,        0.0,               math.radians(8),  "roll right"),
    (18.0, cfg.STANCE_HEIGHT,        0.0,               0.0,              "neutral"),
]


def smoothstep(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)


def lerp(a, b, s):
    return a + (b - a) * s

def pose_at(t):
    t = t % 18.0

    for i in range(len(_KEYS) - 1):
        t0, h0, p0, r0, _ = _KEYS[i]
        t1, h1, p1, r1, name = _KEYS[i + 1]

        if t0 <= t <= t1:
            s = smoothstep((t - t0) / (t1 - t0))

            height = lerp(h0, h1, s)
            pitch = lerp(p0, p1, s)
            roll = lerp(r0, r1, s)

            return height, pitch, roll, name

    return cfg.STANCE_HEIGHT, 0.0, 0.0, "neutral"

# --------------------------------------------------------------------
# Viewer
# --------------------------------------------------------------------
def view():
    import mujoco
    import mujoco.viewer
    mj, m, d = make_sim()
    init_stance(mj, m, d)
    print("pose & wave demo  --  drag to orbit, close the window to quit")
    label = ""
    with mujoco.viewer.launch_passive(m, d) as v:
        start = time.time()
        while v.is_running():
            t = time.time() - start
            h, pitch, roll, name = pose_at(t)
            targets = body_pose_targets(h, pitch, roll)
            if name != label:
                print(f"  [{t:5.1f}s]  {name}")
                label = name
            command(mj, m, d, targets)
            mj.mj_step(m, d)
            v.sync()
            wait = m.opt.timestep - (time.time() - start - t)
            if wait > 0:
                time.sleep(wait)


# --------------------------------------------------------------------
# Headless self-test
# --------------------------------------------------------------------
def check():
    print("body-pose demo  --  self-test\n")
    mj, m, d = make_sim()
    print(f"[1] model loaded: {m.nu} servos, {m.nbody} bodies")

    print("[2] feet stay planted: the neutral body pose matches the standing stance")
    neutral = body_pose_targets(cfg.STANCE_HEIGHT, 0.0, 0.0)
    drift = max(math.dist(a, b) for a, b in zip(neutral, ik.default_stance()))
    planted_ok = drift < 1e-9
    print(f"    stance vs neutral drift: {drift:.2e} m  "
          f"-> {'PASS' if planted_ok else 'FAIL'}")

    print("[3] every pose in the routine is reachable")
    bad = 0
    for k in range(72):                       # 18 s, every 0.25 s
        h, pitch, roll, _ = pose_at(k * 0.25)
        try:
            ik.solve_all(body_pose_targets(h, pitch, roll))
        except ValueError:
            bad += 1
    poses_ok = bad == 0
    print(f"    unreachable poses: {bad}  -> {'PASS' if poses_ok else 'FAIL'}")

    print("[4] the robot holds itself up through the whole routine")
    init_stance(mj, m, d)
    low = 1.0
    for _ in range(9000):                     # 18 s
        h, pitch, roll, _ = pose_at(d.time)
        command(mj, m, d, body_pose_targets(h, pitch, roll))
        mj.mj_step(m, d)
        low = min(low, float(d.qpos[_jadr(mj, m, "trunk") + 2]))
    upright = low > 0.035
    print(f"    lowest ride height: {low*100:.1f} cm  "
          f"-> {'PASS' if upright else 'FAIL'}")

    ok = planted_ok and poses_ok and upright
    print(f"\n{'ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="hexapod body-pose demo")
    ap.add_argument("--check", action="store_true", help="headless self-test")
    args = ap.parse_args()
    if args.check:
        return check()
    try:
        view()
    except ImportError:
        print("MuJoCo is not installed.  Run:  pip install mujoco")
        return 1
    except Exception as exc:
        print(f"could not open the viewer ({exc}).")
        print("Try the self-test instead:  python demo_body_pose.py --check")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
