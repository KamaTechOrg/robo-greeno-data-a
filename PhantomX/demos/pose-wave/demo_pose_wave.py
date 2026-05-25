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


# --------------------------------------------------------------------
# The demo  --  this is the part you own
# --------------------------------------------------------------------
WAVE_LEG = 0          # index into cfg.LEGS  ->  "front_left"


def wave_pose(t):
    """Five legs hold a stand; the front-left leg lifts and waves."""
    targets = ik.default_stance()                 # all six on the ground
    name, mount = cfg.LEGS[WAVE_LEG]
    sweep = 0.060 * math.sin(2.0 * math.pi * t / 1.4)   # side to side
    targets[WAVE_LEG] = (0.21 * math.cos(mount),
                         0.21 * math.sin(mount) + sweep,
                         -0.048)                  # lifted off the ground
    return targets


def pose_at(t):
    """The scripted routine. Loops every 18 seconds."""
    t = t % 18.0
    if t < 4.0:
        return ik.default_stance(), "stand"
    if t < 8.0:
        return ik.default_stance(stance_height=cfg.STANCE_HEIGHT * 0.70), "crouch low"
    if t < 12.0:
        return (ik.default_stance(stance_height=cfg.STANCE_HEIGHT * 1.12,
                                  stance_radius=cfg.STANCE_RADIUS * 0.94),
                "stand tall")
    return wave_pose(t - 12.0), "wave hello"


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
            targets, name = pose_at(t)
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
    print("pose & wave demo  --  self-test\n")
    mj, m, d = make_sim()
    print(f"[1] model loaded: {m.nu} servos, {m.nbody} bodies")

    print("[2] every pose in the routine is reachable")
    bad = 0
    for k in range(72):                       # 18 s, every 0.25 s
        targets, _ = pose_at(k * 0.25)
        try:
            ik.solve_all(targets)
        except ValueError:
            bad += 1
    poses_ok = bad == 0
    print(f"    unreachable poses: {bad}  -> {'PASS' if poses_ok else 'FAIL'}")

    print("[3] the robot holds itself up through the whole routine")
    init_stance(mj, m, d)
    low = 1.0
    for _ in range(9000):                     # 18 s
        targets, _ = pose_at(d.time)
        command(mj, m, d, targets)
        mj.mj_step(m, d)
        low = min(low, float(d.qpos[_jadr(mj, m, "trunk") + 2]))
    upright = low > 0.035
    print(f"    lowest ride height: {low*100:.1f} cm  "
          f"-> {'PASS' if upright else 'FAIL'}")

    ok = poses_ok and upright
    print(f"\n{'ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="hexapod pose & wave demo")
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
        print("Try the self-test instead:  python demo_pose_wave.py --check")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
