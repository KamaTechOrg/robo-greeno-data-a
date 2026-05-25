# Demo 1 — Pose & wave

The hexapod stands, crouches low, rises up tall, then lifts its
front-left leg and waves it side to side. No walking — every pose is
just six foot targets handed to the inverse kinematics.

A good first demo: simple, visual, and it shows that one solver
drives the whole robot.

## Run it

```
pip install mujoco
python demo_pose_wave.py          # opens the 3D viewer
python demo_pose_wave.py --check  # headless self-test (no display)
```

`--check` must print `ALL CHECKS PASSED` — it confirms every pose in
the routine is reachable and the robot stays upright the whole time.

## What's in this folder

| file                 | what it is                                  |
|----------------------|---------------------------------------------|
| `demo_pose_wave.py`  | the demo — **the part you own** (the poses). |
| `config.py`          | the robot geometry (shared, do not edit).    |
| `hexapod_ik.py`      | the inverse-kinematics solver (shared).      |
| `hexapod_model.py`   | builds the MuJoCo robot (shared).            |

The whole demo lives in one readable file. `pose_at()` is the routine;
`wave_pose()` is the wave. Read those two functions first.

## What to show in your demo

1. Run `python demo_pose_wave.py` and let the routine play.
2. Orbit the camera so the wave is clearly visible.
3. Record a short clip (15–20 s) and add it to your write-up.
4. Be ready to explain: each pose is six foot targets, and
   `leg_ik()` turns each target into three joint angles.

## Make it yours

- Change which leg waves: edit `WAVE_LEG` (0–5).
- Add a pose: a new `if` branch in `pose_at()` with its own
  `default_stance(...)` settings, or your own six foot targets.
- Make two legs wave at once.
- Change the wave speed or how high the leg lifts in `wave_pose()`.

This folder is self-contained — push it to the team GitHub as your
demo once your `--check` passes.
