"""
demo_turn_in_place.py  --  Robo-Greeno hexapod demo: turn in place.

The robot spins on the spot to face a new direction without walking
anywhere. It uses the exact same alternating tripod rhythm as the
straight walk -- swing and stance, tripod A and B, the phase logic --
the one thing that changes is the path each foot follows: a straight
line becomes an arc.

The idea
--------
In the straight walk a stance foot slides backward in a straight line,
which pushes the body forward. To turn instead, a stance foot sweeps
along an *arc* around the body centre. If every stance foot rotates by
a small angle -d about the body's Z axis, the body rotates by +d. Do
that every step and the rotations add up: the robot spins in place.

So we keep each foot's home (hx, hy) and rotate it about the body
centre by an angle a(t):

    x' = hx * cos a  -  hy * sin a
    y' = hx * sin a  +  hy * cos a

In stance the angle sweeps +TURN_ANGLE -> -TURN_ANGLE (foot down,
turning the body); in swing the foot lifts and the angle sweeps back
-TURN_ANGLE -> +TURN_ANGLE to reset for the next push. The vertical
lift dz is exactly the swing lift from the walk demo.

Run it
------
  pip install mujoco
  python demo_turn_in_place.py            # open the 3D viewer
  python demo_turn_in_place.py --check    # headless self-test, no display
  python demo_turn_in_place.py --cw       # turn the other way (clockwise)
"""

import argparse
import math
import sys
import time

import config as cfg
import hexapod_ik as ik
import hexapod_model as model


# --------------------------------------------------------------------
# Turn parameters  --  this is the part you own
# --------------------------------------------------------------------
TURN_ANGLE = math.radians(8.0)   # foot-sweep amplitude per step (try bigger!)
TURN_DIR   = +1.0                # +1 = counter-clockwise (+Z), -1 = clockwise


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


def _yaw(d, tadr):
    """Trunk heading (rotation about +Z), radians, from its quaternion."""
    qw, qx, qy, qz = (float(d.qpos[tadr + 3]), float(d.qpos[tadr + 4]),
                      float(d.qpos[tadr + 5]), float(d.qpos[tadr + 6]))
    return math.atan2(2.0 * (qw * qz + qx * qy),
                      1.0 - 2.0 * (qy * qy + qz * qz))


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
# The demo  --  this is the part you own: the turn gait
# --------------------------------------------------------------------
def turn_targets(t):
    """Foot targets (body frame) for the turn-in-place gait at time t.

    Same tripod scaffold as the straight walk -- only the foot path is
    different: instead of a backward straight line in stance, the foot
    sweeps along an arc about the body centre. The two tripods run the
    same cycle half a period apart, so one tripod is always pushing the
    turn while the other resets, and the robot stays on three feet."""
    base = ik.default_stance()
    out = []
    for i, (name, mount) in enumerate(cfg.LEGS):
        hx, hy, bz = base[i]
        phase = (t / cfg.GAIT_PERIOD) % 1.0
        local = phase if i in cfg.TRIPOD_A else (phase + 0.5) % 1.0
        if local < 0.5:                                   # swing -- reset the foot
            s = local / 0.5
            a = -TURN_ANGLE + s * (2.0 * TURN_ANGLE)
            dz = cfg.GAIT_LIFT * math.sin(math.pi * s)
        else:                                             # stance -- turn the body
            s = (local - 0.5) / 0.5
            a = TURN_ANGLE - s * (2.0 * TURN_ANGLE)
            dz = 0.0
        a *= TURN_DIR
        ca, sa = math.cos(a), math.sin(a)                 # rotate home about +Z
        rx = hx * ca - hy * sa
        ry = hx * sa + hy * ca
        out.append((rx, ry, bz + dz))
    return out


# --------------------------------------------------------------------
# Viewer
# --------------------------------------------------------------------
def view():
    import mujoco
    import mujoco.viewer
    mj, m, d = make_sim()
    init_stance(mj, m, d)
    way = "counter-clockwise" if TURN_DIR > 0 else "clockwise"
    print(f"turn-in-place demo  --  spinning {way}; drag to orbit, close to quit")
    print("  tripod A: front-left, back-left, mid-right")
    print("  tripod B: mid-left, back-right, front-right")
    with mujoco.viewer.launch_passive(m, d) as v:
        start = time.time()
        while v.is_running():
            t = time.time() - start
            command(mj, m, d, turn_targets(t))
            mj.mj_step(m, d)
            v.sync()
            wait = m.opt.timestep - (time.time() - start - t)
            if wait > 0:
                time.sleep(wait)


# --------------------------------------------------------------------
# Headless self-test
# --------------------------------------------------------------------
def check():
    print("turn-in-place demo  --  self-test\n")
    mj, m, d = make_sim()
    print(f"[1] model loaded: {m.nu} servos, {m.nbody} bodies")

    print("[2] every step of the gait is reachable")
    bad = 0
    for k in range(160):                      # 8 s of gait, every 0.05 s
        try:
            ik.solve_all(turn_targets(k * 0.05))
        except ValueError:
            bad += 1
    steps_ok = bad == 0
    print(f"    unreachable steps: {bad}  -> {'PASS' if steps_ok else 'FAIL'}")

    print("[3] the robot turns in place -- it spins but does not walk away")
    init_stance(mj, m, d)
    tadr = _jadr(mj, m, "trunk")
    yaw0 = _yaw(d, tadr)
    for _ in range(4000):                      # 8 s
        command(mj, m, d, turn_targets(d.time))
        mj.mj_step(m, d)
    height = float(d.qpos[tadr + 2])
    x, y = float(d.qpos[tadr + 0]), float(d.qpos[tadr + 1])
    drift = math.hypot(x, y)
    turned = abs((_yaw(d, tadr) - yaw0 + math.pi) % (2 * math.pi) - math.pi)
    upright = not math.isnan(height) and height > 0.045
    spun = math.degrees(turned) > 8.0         # a clear, visible turn
    in_place = drift < 0.05                    # barely moved (< 5 cm)
    print(f"    after 8 s: turned {math.degrees(turned):+.1f} deg, "
          f"drift {drift*100:.1f} cm, ride height {height*100:.1f} cm")
    print(f"    spun {'PASS' if spun else 'FAIL'} | "
          f"in-place {'PASS' if in_place else 'FAIL'} | "
          f"upright {'PASS' if upright else 'FAIL'}")

    ok = steps_ok and spun and in_place and upright
    print(f"\n{'ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="hexapod turn-in-place demo")
    ap.add_argument("--check", action="store_true", help="headless self-test")
    ap.add_argument("--cw", action="store_true", help="turn clockwise instead")
    args = ap.parse_args()
    global TURN_DIR
    if args.cw:
        TURN_DIR = -1.0
    if args.check:
        return check()
    try:
        view()
    except ImportError:
        print("MuJoCo is not installed.  Run:  pip install mujoco")
        return 1
    except Exception as exc:
        print(f"could not open the viewer ({exc}).")
        print("Try the self-test instead:  python demo_turn_in_place.py --check")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
