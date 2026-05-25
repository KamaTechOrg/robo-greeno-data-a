"""
demo_tripod_walk.py  --  Robo-Greeno hexapod demo: walk forward.

The robot walks forward with an alternating tripod gait. Three legs
(tripod A) push the body forward while the other three (tripod B)
lift and swing ahead -- then the two groups swap. Each foot follows
a simple path; the inverse kinematics turns that path into joint
angles, six legs at a time.

Run it
------
  pip install mujoco
  python demo_tripod_walk.py          # open the 3D viewer
  python demo_tripod_walk.py --check  # headless self-test, no display
"""

import argparse
import math
import sys
import time

import config as cfg
import hexapod_ik as ik
import hexapod_model as model


# --------------------------------------------------------------------
# MuJoCo plumbing -- builds the robot and lets us drive it
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
# The demo  --  this is the part you own: the gait
# --------------------------------------------------------------------
def walk_targets(t):
    """Foot targets (body frame) for the tripod walk at time t seconds.

    Each leg repeats a cycle of length GAIT_PERIOD:
      swing  (first half)  -- lift the foot and carry it forward
      stance (second half) -- keep the foot down and push the body
    Tripod A and tripod B run the same cycle, half a period apart, so
    one tripod is always pushing while the other is swinging."""
    base = ik.default_stance()
    half = cfg.GAIT_STRIDE / 2.0
    out = []
    for i, (name, mount) in enumerate(cfg.LEGS):
        bx, by, bz = base[i]
        phase = (t / cfg.GAIT_PERIOD) % 1.0
        local = phase if i in cfg.TRIPOD_A else (phase + 0.5) % 1.0
        if local < 0.5:                       # swing
            s = local / 0.5
            dx = -half + s * cfg.GAIT_STRIDE
            dz = cfg.GAIT_LIFT * math.sin(math.pi * s)
        else:                                 # stance
            s = (local - 0.5) / 0.5
            dx = half - s * cfg.GAIT_STRIDE
            dz = 0.0
        out.append((bx + dx, by, bz + dz))
    return out


# --------------------------------------------------------------------
# Viewer
# --------------------------------------------------------------------
def view():
    import mujoco
    import mujoco.viewer
    mj, m, d = make_sim()
    init_stance(mj, m, d)
    print("tripod walk demo  --  drag to orbit, close the window to quit")
    print("  tripod A: front-left, back-left, mid-right")
    print("  tripod B: mid-left, back-right, front-right")
    with mujoco.viewer.launch_passive(m, d) as v:
        start = time.time()
        while v.is_running():
            t = time.time() - start
            command(mj, m, d, walk_targets(t))
            mj.mj_step(m, d)
            v.sync()
            wait = m.opt.timestep - (time.time() - start - t)
            if wait > 0:
                time.sleep(wait)


# --------------------------------------------------------------------
# Headless self-test
# --------------------------------------------------------------------
def check():
    print("tripod walk demo  --  self-test\n")
    mj, m, d = make_sim()
    print(f"[1] model loaded: {m.nu} servos, {m.nbody} bodies")

    print("[2] every step of the gait is reachable")
    bad = 0
    for k in range(140):                      # 7 s of gait, every 0.05 s
        try:
            ik.solve_all(walk_targets(k * 0.05))
        except ValueError:
            bad += 1
    steps_ok = bad == 0
    print(f"    unreachable steps: {bad}  -> {'PASS' if steps_ok else 'FAIL'}")

    print("[3] the robot walks forward and stays on its feet")
    init_stance(mj, m, d)
    for _ in range(5000):                     # 10 s
        command(mj, m, d, walk_targets(d.time))
        mj.mj_step(m, d)
    tadr = _jadr(mj, m, "trunk")
    height = float(d.qpos[tadr + 2])
    fwd = float(d.qpos[tadr + 0])
    walked = not math.isnan(height) and height > 0.045 and fwd > 0.10
    print(f"    after 10 s: ride height {height*100:.1f} cm, "
          f"forward {fwd*100:+.1f} cm  -> {'PASS' if walked else 'FAIL'}")

    ok = steps_ok and walked
    print(f"\n{'ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="hexapod tripod walk demo")
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
        print("Try the self-test instead:  python demo_tripod_walk.py --check")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
