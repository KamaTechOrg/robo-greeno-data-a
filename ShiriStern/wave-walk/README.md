# Demo 2 — Tripod walk

The hexapod walks forward with an alternating tripod gait. Three legs
push the body forward while the other three lift and swing ahead —
then the groups swap. It is the classic six-legged walk.

## Run it

```
pip install mujoco
python demo_tripod_walk.py          # opens the 3D viewer
python demo_tripod_walk.py --check  # headless self-test (no display)
```

`--check` must print `ALL CHECKS PASSED` — it confirms every step of
the gait is reachable and the robot walks forward without falling
(it travels roughly 85 cm in 10 seconds in simulation).

## What's in this folder

| file                  | what it is                                   |
|-----------------------|-----------------------------------------------|
| `demo_tripod_walk.py` | the demo — **the part you own** (the gait).   |
| `config.py`           | the robot geometry (shared, do not edit).     |
| `hexapod_ik.py`       | the inverse-kinematics solver (shared).       |
| `hexapod_model.py`    | builds the MuJoCo robot (shared).             |

`walk_targets()` is the whole gait. Read it first: each leg follows a
swing half (lift and carry the foot forward) and a stance half (keep
the foot down and push the body).

## The two tripods

- Tripod A — front-left, back-left, mid-right
- Tripod B — mid-left, back-right, front-right

The two groups run the same cycle, half a period apart, so one
tripod is always on the ground holding the robot up.

## What to show in your demo

1. Run `python demo_tripod_walk.py` and watch it walk.
2. Orbit the camera to a low angle so the leg lift is visible.
3. Record a short clip (15–20 s) and add it to your write-up.
4. Be ready to explain swing vs stance, and why the alternating
   tripod keeps the robot stable at every instant.

## Make it yours

- Walk faster or slower: edit `GAIT_PERIOD` in `config.py`.
- Longer or shorter steps: edit `GAIT_STRIDE`.
- Higher foot lift: edit `GAIT_LIFT`.
- Harder: make it walk backward, or steer by giving the left and
  right legs different stride lengths.

This folder is self-contained — push it to the team GitHub as your
demo once your `--check` passes.
