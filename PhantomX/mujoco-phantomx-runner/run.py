"""
run.py  --  the Robo-Greeno hexapod runner.

Loads the generated MuJoCo model, solves all six legs with the
closed-form inverse kinematics, and drives the robot so it stands
and walks on command.

Usage
-----
  python run.py            open the viewer: stand, crouch, tall, walk
  python run.py --walk     open the viewer straight into a tripod walk
  python run.py --check    headless self-test (no display) -- for CI
  python run.py --xml      write hexapod.xml and exit

Install once:  pip install mujoco numpy
"""

import argparse
import math
import sys
import time

import config as cfg
import hexapod_ik as ik
import hexapod_model as model


# --------------------------------------------------------------------
# Build the simulation
# --------------------------------------------------------------------
def make_sim():
    import mujoco
    m = mujoco.MjModel.from_xml_string(model.build_mjcf())
    d = mujoco.MjData(m)
    return mujoco, m, d


def _jid(mujoco, m, name):
    return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, name)


def _aid(mujoco, m, name):
    return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, name)


def _sid(mujoco, m, name):
    return mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, name)


def init_stance(mujoco, m, d):
    """Place the robot already in its standing pose, feet on the ground.

    This avoids a violent snap from the spawn pose: the trunk is parked
    at ride height and every joint is pre-set to its IK solution."""
    mujoco.mj_resetData(m, d)
    tadr = m.jnt_qposadr[_jid(mujoco, m, "trunk")]
    d.qpos[tadr:tadr + 7] = [0, 0, cfg.STANCE_HEIGHT, 1, 0, 0, 0]
    for (name, mount), tgt in zip(cfg.LEGS, ik.default_stance()):
        coxa, femur, tibia = ik.leg_ik(*ik.body_target_to_leg(tgt, mount))
        for joint, val in (("coxa", coxa), ("femur", femur), ("tibia", tibia)):
            d.qpos[m.jnt_qposadr[_jid(mujoco, m, f"{name}_{joint}")]] = val
    mujoco.mj_forward(m, d)


# --------------------------------------------------------------------
# Commanding the robot: 6 foot targets -> IK -> 18 servo set-points
# --------------------------------------------------------------------
def command_pose(mujoco, m, d, foot_targets):
    """Solve IK for the body-frame foot targets and write the servos."""
    angles = ik.solve_all(foot_targets)
    for (name, _), (coxa, femur, tibia) in zip(cfg.LEGS, angles):
        d.ctrl[_aid(mujoco, m, f"{name}_coxa")] = coxa
        d.ctrl[_aid(mujoco, m, f"{name}_femur")] = femur
        d.ctrl[_aid(mujoco, m, f"{name}_tibia")] = tibia


# --------------------------------------------------------------------
# Gait: an open-loop alternating tripod walk
# --------------------------------------------------------------------
def walk_targets(t):
    """Foot targets (body frame) for the tripod walk at time t seconds."""
    base = ik.default_stance()
    half = cfg.GAIT_STRIDE / 2.0
    targets = []
    for i, (name, mount) in enumerate(cfg.LEGS):
        bx, by, bz = base[i]
        phase = (t / cfg.GAIT_PERIOD) % 1.0
        # tripod A leads; tripod B is half a cycle behind
        local = phase if i in cfg.TRIPOD_A else (phase + 0.5) % 1.0
        if local < 0.5:                       # swing: lift and carry forward
            s = local / 0.5
            dx = -half + s * cfg.GAIT_STRIDE
            dz = cfg.GAIT_LIFT * math.sin(math.pi * s)
        else:                                 # stance: push the body forward
            s = (local - 0.5) / 0.5
            dx = half - s * cfg.GAIT_STRIDE
            dz = 0.0
        targets.append((bx + dx, by, bz + dz))
    return targets


def demo_targets(t):
    """A scripted sequence so the default run shows the robot off."""
    if t < 3.0:
        return ik.default_stance(), "standing"
    if t < 6.0:
        return ik.default_stance(stance_height=cfg.STANCE_HEIGHT * 0.70), "crouching low"
    if t < 9.0:
        return (ik.default_stance(stance_height=cfg.STANCE_HEIGHT * 1.12,
                                  stance_radius=cfg.STANCE_RADIUS * 0.94),
                "standing tall")
    return walk_targets(t - 9.0), "tripod walk"


# --------------------------------------------------------------------
# Headless self-test  --  no display needed
# --------------------------------------------------------------------
def check():
    print("Robo-Greeno hexapod  --  headless self-test\n")
    cfg.describe()

    print("\n[1] build + load the MuJoCo model")
    mujoco, m, d = make_sim()
    print(f"    ok: {m.njnt} joints, {m.nu} actuators, {m.nbody} bodies")

    print("\n[2] inverse kinematics round-trip (FK . IK == identity)")
    worst = 0.0
    for (name, mount), tgt in zip(cfg.LEGS, ik.default_stance()):
        leg_xyz = ik.body_target_to_leg(tgt, mount)
        sol = ik.leg_ik(*leg_xyz)
        err = math.dist(leg_xyz, ik.leg_fk(*sol))
        worst = max(worst, err)
    print(f"    worst error: {worst:.2e} m  -> {'PASS' if worst < 1e-9 else 'FAIL'}")

    print("\n[3] model agrees with the IK (feet land on their targets)")
    init_stance(mujoco, m, d)
    foot_err = 0.0
    for name, mount in cfg.LEGS:
        got = d.site_xpos[_sid(mujoco, m, f"{name}_foot")]
        want = (cfg.STANCE_RADIUS * math.cos(mount),
                cfg.STANCE_RADIUS * math.sin(mount),
                cfg.FOOT_RADIUS)
        foot_err = max(foot_err, math.dist(got, want))
    feet_ok = foot_err < 1e-5
    print(f"    worst foot placement error: {foot_err:.2e} m  "
          f"-> {'PASS' if feet_ok else 'FAIL'}")

    print("\n[4] the robot stands up under gravity")
    init_stance(mujoco, m, d)
    command_pose(mujoco, m, d, ik.default_stance())
    for _ in range(2000):
        mujoco.mj_step(m, d)
    tz = m.jnt_qposadr[_jid(mujoco, m, "trunk")] + 2
    height = float(d.qpos[tz])
    upright = not math.isnan(height) and 0.060 < height < 0.090
    print(f"    trunk ride height after 4 s: {height*100:.1f} cm  "
          f"(target {cfg.STANCE_HEIGHT*100:.1f} cm)  "
          f"-> {'PASS (standing)' if upright else 'FAIL'}")

    print("\n[5] the robot walks without falling over")
    init_stance(mujoco, m, d)
    for _ in range(4000):
        command_pose(mujoco, m, d, walk_targets(d.time))
        mujoco.mj_step(m, d)
    tadr = m.jnt_qposadr[_jid(mujoco, m, "trunk")]
    height = float(d.qpos[tadr + 2])
    fwd = float(d.qpos[tadr + 0])
    walked = not math.isnan(height) and height > 0.045
    print(f"    after 8 s walk: ride height {height*100:.1f} cm, "
          f"travelled {fwd*100:+.1f} cm  -> {'PASS' if walked else 'FAIL'}")

    ok = worst < 1e-9 and feet_ok and upright and walked
    print(f"\n{'ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'}")
    return 0 if ok else 1


# --------------------------------------------------------------------
# Viewer  --  interactive, runs on the user's desktop
# --------------------------------------------------------------------
def view(walk_only=False):
    import mujoco
    import mujoco.viewer

    mujoco, m, d = make_sim()
    init_stance(mujoco, m, d)
    command_pose(mujoco, m, d, ik.default_stance())

    print("hexapod viewer  --  drag to orbit, close the window to quit")
    print("  legs:   coxa = grey   femur = green   tibia = blue   foot = orange")
    print("  mode:   tripod walk" if walk_only
          else "  mode:   stand -> crouch -> tall -> walk")

    label = ""
    with mujoco.viewer.launch_passive(m, d) as viewer:
        start = time.time()
        while viewer.is_running():
            t = time.time() - start
            if walk_only:
                targets, name = walk_targets(t), "tripod walk"
            else:
                targets, name = demo_targets(t)
            if name != label:
                print(f"  [{t:5.1f}s]  {name}")
                label = name
            command_pose(mujoco, m, d, targets)
            mujoco.mj_step(m, d)
            viewer.sync()
            dt = m.opt.timestep - (time.time() - start - t)
            if dt > 0:
                time.sleep(dt)


# --------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Robo-Greeno hexapod runner")
    ap.add_argument("--check", action="store_true",
                    help="headless self-test, no display")
    ap.add_argument("--walk", action="store_true",
                    help="open the viewer straight into a tripod walk")
    ap.add_argument("--xml", action="store_true",
                    help="write hexapod.xml and exit")
    args = ap.parse_args()

    if args.xml:
        print("wrote", model.save())
        return 0
    if args.check:
        return check()
    try:
        view(walk_only=args.walk)
    except ImportError:
        print("MuJoCo is not installed.  Run:  pip install mujoco numpy")
        return 1
    except Exception as exc:
        print(f"could not open the viewer ({exc}).")
        print("Try the headless self-test instead:  python run.py --check")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
