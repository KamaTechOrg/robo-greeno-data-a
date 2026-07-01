"""
main.py  --  run the hexapod in SIMULATION or on REAL hardware.

One control loop, one 18-channel interface, two interchangeable backends:

    sim   -> sim_mujoco.MujocoBackend     (physics in MuJoCo)
    real  -> real_pca9685.Pca9685Backend  (servos over I2C; dry-run off-Pi)

The gait (gait.py) and kinematics (kinematics.py) never know which backend
they are driving -- that is the whole point of the consolidation.

Usage
-----
  python hexapod/main.py --backend sim  --gait wave --seconds 6
  python hexapod/main.py --backend real --gait stand --seconds 2   # dry-run off-Pi
  python hexapod/main.py --camera                                   # add frame grabber
  python hexapod/main.py --check                                    # headless self-test
"""

import argparse
import sys
import time

import robot_config as cfg
import kinematics as ik
import gait as gaits


def make_backend(kind, **kw):
    if kind == "sim":
        import sim_mujoco
        return sim_mujoco.make()
    if kind == "real":
        import real_pca9685
        return real_pca9685.make(**kw)
    raise ValueError(f"unknown backend '{kind}'")


def run(backend, gait_fn, seconds, camera=None, realtime=False):
    """Drive `backend` with `gait_fn` for `seconds`. In sim we step physics;
    on real hardware we pace the loop to the configured control rate."""
    dt = getattr(backend, "dt", 1.0 / cfg.CONTROL_HZ)
    n_steps = int(seconds / dt)
    frames = 0
    start = time.time()
    for k in range(n_steps):
        t = k * dt
        backend.set_joint_targets(ik.solve_channels(gait_fn(t)))
        backend.step()
        if camera is not None and k % max(1, int(cfg.CONTROL_HZ / 10)) == 0:
            camera.capture_tagged(pose_provider=getattr(backend, "pose", None))
            frames += 1
        if realtime:
            slack = (k + 1) * dt - (time.time() - start)
            if slack > 0:
                time.sleep(slack)
    return frames


# --------------------------------------------------------------------
# Headless self-test -- exercises every backend and the camera, no hardware
# --------------------------------------------------------------------
def check():
    print("hexapod integration -- self-test\n")
    ok = True

    print("[1] sim backend (MuJoCo) walks with the wave gait")
    try:
        import sim_mujoco
        be = sim_mujoco.make()
        print(f"    backend: {be.name}, {be.model.nu} servos, dt={be.dt*1000:.0f} ms")
        for k in range(int(6.0 / be.dt)):          # 6 s of wave walk
            be.set_joint_targets(ik.solve_channels(gaits.wave(k * be.dt)))
            be.step()
        h, fwd = be.ride_height(), be.pose()["position_m"][0]
        walked = h > 0.045 and fwd > 0.05
        print(f"    after 6 s: ride height {h*100:.1f} cm, forward {fwd*100:+.1f} cm"
              f"  -> {'PASS' if walked else 'FAIL'}")
        ok = ok and walked
    except Exception as exc:
        print(f"    sim backend FAILED: {type(exc).__name__}: {exc}")
        ok = False

    print("[2] gaits are reachable through the IK (stand / tripod / wave)")
    bad = {}
    for gname, gfn in gaits.GAITS.items():
        n_bad = 0
        for k in range(120):
            try:
                ik.solve_channels(gfn(k * 0.05))
            except ValueError:
                n_bad += 1
        bad[gname] = n_bad
    gaits_ok = all(v == 0 for v in bad.values())
    print(f"    unreachable steps: {bad}  -> {'PASS' if gaits_ok else 'FAIL'}")
    ok = ok and gaits_ok

    print("[3] real (PCA9685) backend converts the stance in dry-run")
    try:
        import real_pca9685
        rb = real_pca9685.make(dry_run=True, verbose=False)
        degs = rb.set_joint_targets(ik.solve_channels(gaits.stand(0.0)))
        in_range = len(degs) == cfg.n_channels() and all(0 <= d <= 180 for d in degs)
        n_warn = len(real_pca9685.range_warnings())
        print(f"    18 channels -> servo deg in [0,180]: {'PASS' if in_range else 'FAIL'}"
              f"  ({n_warn} range warnings: femur/tibia > 180 deg)")
        ok = ok and in_range
    except Exception as exc:
        print(f"    real backend FAILED: {type(exc).__name__}: {exc}")
        ok = False

    print("[4] camera grabs a pose-tagged frame (synthetic off-Pi)")
    try:
        import camera as cam_mod
        cam = cam_mod.make(verbose=False)
        tagged = cam.capture_tagged(pose_provider=lambda: {
            "position_m": [0, 0, cfg.STANCE_HEIGHT],
            "orientation_quat": [1, 0, 0, 0]})
        good = (tagged["frame"].shape == (cam_mod.FRAME_H, cam_mod.FRAME_W, 3)
                and tagged["stamp_ms"] > 0 and tagged["pose"] is not None)
        print(f"    tagged frame {tagged['frame'].shape}, stamp_ms set, pose attached"
              f"  -> {'PASS' if good else 'FAIL'}")
        cam.close()
        ok = ok and good
    except Exception as exc:
        print(f"    camera FAILED: {type(exc).__name__}: {exc}")
        ok = False

    print(f"\n{'ALL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="Robo-Greeno hexapod: sim or real")
    ap.add_argument("--backend", choices=("sim", "real"), default="sim")
    ap.add_argument("--gait", choices=tuple(gaits.GAITS), default="wave")
    ap.add_argument("--seconds", type=float, default=6.0)
    ap.add_argument("--camera", action="store_true",
                    help="also run the CSI frame grabber (pose-tagged)")
    ap.add_argument("--channels", type=int, default=None,
                    help="real: number of wired servos for incremental bring-up")
    ap.add_argument("--check", action="store_true", help="headless self-test")
    args = ap.parse_args()

    if args.check:
        return check()

    print(f"hexapod: backend={args.backend} gait={args.gait} "
          f"seconds={args.seconds}")
    kw = {}
    if args.backend == "real" and args.channels is not None:
        kw["channels"] = args.channels
    try:
        backend = make_backend(args.backend, **kw)
    except ImportError as exc:
        print(f"backend '{args.backend}' unavailable: {exc}")
        print("sim needs `pip install mujoco`; real needs adafruit-servokit on a Pi.")
        return 1
    print(f"  backend ready: {backend.name}")

    cam = None
    if args.camera:
        import camera as cam_mod
        cam = cam_mod.make()
        print(f"  camera ready:  {cam.name}")

    # real hardware runs in wall-clock (rate-limited); sim runs as fast as it can
    frames = run(backend, gaits.GAITS[args.gait], args.seconds,
                 camera=cam, realtime=(args.backend == "real"))
    if hasattr(backend, "pose") and backend.pose() is not None:
        p = backend.pose()["position_m"]
        print(f"  done. trunk at x={p[0]*100:+.1f} cm y={p[1]*100:+.1f} cm "
              f"z={p[2]*100:.1f} cm")
    if cam is not None:
        print(f"  grabbed {frames} pose-tagged frames")
        cam.close()
    backend.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
