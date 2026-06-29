# Demo — Turn in place

The hexapod spins on the spot to face a new direction without walking
anywhere. It reuses the whole alternating-tripod scaffold from the
straight walk — swing and stance, tripod A and B, the phase logic —
and changes only **the path each foot follows**: in stance the foot
sweeps along an *arc* about the body centre instead of sliding back in
a straight line. Every stance foot rotates by `-d`, so the body
rotates by `+d`; do it each step and the turns add up.

## Run it

```
pip install mujoco
python demo_turn_in_place.py          # opens the 3D viewer
python demo_turn_in_place.py --check  # headless self-test (no display)
python demo_turn_in_place.py --cw     # spin clockwise instead
```

`--check` must print `ALL CHECKS PASSED`. It confirms every step of the
gait is reachable and that after 8 s the robot **turned** (~178° in
simulation) while its `(x, y)` barely moved (~0.1 cm drift) and it
stayed upright — it spun, it did not walk away.

## What's in this folder

| file                    | what it is                                  |
|-------------------------|----------------------------------------------|
| `demo_turn_in_place.py` | the demo — **the part you own** (the turn).  |
| `config.py`             | the robot geometry (shared, do not edit).    |
| `hexapod_ik.py`         | the inverse-kinematics solver (shared).      |
| `hexapod_model.py`      | builds the MuJoCo robot (shared).            |

`turn_targets()` is the whole gait. Read it first: each leg has a
stance half (foot down, sweep the arc that turns the body) and a swing
half (lift the foot and rotate it back to reset for the next push).

## Turn vs walk — the one-line comparison

The straight walk moves a stance foot **backward in a straight line**
(body goes forward); the turn moves a stance foot **along an arc about
the body centre** (body rotates in place). Same scaffold, different
foot path — that is the central idea of gaits: the body's motion is
decided entirely by the path each foot traces on the ground.

## The two tripods

- Tripod A — front-left, back-left, mid-right
- Tripod B — mid-left, back-right, front-right

The two groups run the same cycle, half a period apart, so one tripod
is always on the ground holding the robot up while it turns.

## What to show in your demo

1. Run `python demo_turn_in_place.py` and watch it spin.
2. Orbit the camera to a top-down angle so the rotation is obvious.
3. Record a short clip (15–20 s) and add it to your write-up.
4. Be ready to explain why rotating every stance foot by `-d` turns
   the body by `+d`, and why the alternating tripod keeps it stable.

## Make it yours

- Turn faster: raise `TURN_ANGLE` in `demo_turn_in_place.py`. Find the
  largest angle that still works — past a point a leg cannot reach and
  `solve_all` raises. That angle is the robot's turn-rate limit.
- Turn the other way: `--cw`, or flip `TURN_DIR`.
- Harder: blend the turn with the straight walk so the robot follows a
  **curved path**; or turn to a **target heading** and stop.

This folder is self-contained — push it to the team GitHub as your demo
once your `--check` passes.
