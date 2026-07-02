# Problem B — Turn in place

**Assigned to:** Shira Marzel
**Builds on:** [`../PhantomX/demos/tripod-walk/`](../project/PhantomX/demos/tripod-walk/)
**Companion problem (for reference):** [Problem A — Body-pose control](../HadasSigaron/Problem-A-Body-Pose.md) (assigned to Hadas Sigaron)

---

This is your assignment for Stage A of the kinematics track. The two
demos in `PhantomX/demos/` — `pose-wave/` and `tripod-walk/` — are
worked examples: they already run. They are **not** the assignment.
They are the starting point you copy, read, and then change into
something new that is yours.

Your problem is **Problem B — Turn in place**, explicitly drawn from
the two-problem set posted in
[`../PhantomX/assignments/`](../project/PhantomX/assignments/) (the other,
Problem A — Body-pose control, goes to Hadas). The two problems are
matched in difficulty: it does not matter which student takes which.
Both end in a runnable demo you can record and show at the
checkpoint.

## The goal

The robot rotates on the spot — it spins to face a new direction
without walking anywhere. Same alternating tripod rhythm as the
straight walk, but the body turns instead of moving forward.

## Why this problem

The straight-walk demo only goes forward; a robot that cannot turn
cannot really go anywhere. Turn-in-place reuses the whole tripod
scaffold you have already seen run — swing and stance, tripod A and
B, the phase logic — so the structure is familiar. The one thing
that changes is the path each foot follows: a straight line becomes
an arc. That single change teaches the central idea of gaits — the
body's motion is decided entirely by the path each foot traces on
the ground.

## Start from

Copy the [`../PhantomX/demos/tripod-walk/`](../project/PhantomX/demos/tripod-walk/)
folder, rename it `turn-in-place/`, and work in a new file
`demo_turn_in_place.py`. Keep the three shared files unchanged.

## The key idea

In the straight walk, a stance foot moves **backward in a straight
line**, which pushes the body forward. To turn instead, a stance foot
must move **along an arc** around the body centre. If every stance
foot rotates by a small angle `−Δ` about the body's Z axis, the body
rotates by `+Δ`.

So in the stance phase, instead of shifting the foot along X, rotate
the foot's home position about the body centre by an angle that
sweeps from `+φ` to `−φ`. In the swing phase, lift the foot and
rotate it back.

A home position `(hx, hy)` rotated about the body centre by angle
`a`:

```
x' = hx·cos a − hy·sin a
y' = hx·sin a + hy·cos a
```

— the same 2-D rotation used everywhere else. The vertical lift `dz`
is unchanged from the walk demo.

## Step by step

1. Open `walk_targets` in the tripod-walk demo and read it until the
   swing/stance split is completely clear.
2. Keep the phase logic, the tripod A/B split and the swing lift
   exactly as they are.
3. Replace the linear `dx` shift with a rotation. Pick a turn
   amplitude `TURN_ANGLE` (start around 8°). In stance the rotation
   sweeps `+TURN_ANGLE → −TURN_ANGLE`; in swing it sweeps back
   `−TURN_ANGLE → +TURN_ANGLE`, with the foot lifted.
4. Apply that rotation to each foot's home `(hx, hy)`; keep `bz` plus
   the swing lift `dz`.
5. Run it in the viewer and watch it spin.

## Watch out for

- A large `TURN_ANGLE` sweeps the feet too far and a leg cannot reach
  — `solve_all` raises. Find the largest angle that still works;
  that is the robot's turn-rate limit.
- The robot should rotate but not drift. If it also creeps forward
  or sideways, the stance and swing arcs are not symmetric — check
  that the swing exactly undoes the stance.
- Make both directions work: `+angle` turns one way, `−angle` the
  other. Once one works the other is almost free.

## Deliver

The `turn-in-place/` folder, `demo_turn_in_place.py`, a `--check`, a
short `README.md`, and a screen recording.

## Success check (put this in `--check`)

Every step of the gait is reachable (no `ValueError`); after ~8 s the
trunk's heading has turned by a clear amount while its `(x, y)`
position has barely moved — it turned, it did not walk away; and the
body stayed upright.

## If there is time (stretch)

Blend turning with the straight walk so the robot follows a curved
path; or have it turn to a target heading and stop.

---

**Where this leads:** turning is exactly what the Stage B gait work
and the later uneven-terrain work are built on. A student who
finishes this has built a real piece of the robot.
