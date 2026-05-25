# Problem D — The wave gait

**Assigned to:** Shiri Stern
**Builds on:** [`../PhantomX/demos/tripod-walk/`](../PhantomX/demos/tripod-walk/)
**Companion problems (for reference):**
[Problem A — Body-pose control](../HadasSigaron/Problem-A-Body-Pose.md) · Hadas Sigaron
[Problem B — Turn in place](../ShiraMarzel/Problem-B-Turn-In-Place.md) · Shira Marzel
[Problem C — Draw a shape in the air](../MiriamKahaneman/Problem-C-Draw-Shape.md) · Miriam Kahaneman

---

This is your assignment for Stage A of the kinematics track. The two
demos in `PhantomX/demos/` — `pose-wave/` and `tripod-walk/` — are
worked examples: they already run. They are **not** the assignment.
They are the starting point you copy, read, and then change into
something new that is yours.

Your problem is **Problem D — The wave gait**, one of four
matched-difficulty problems posted in
[`../PhantomX/assignments/`](../PhantomX/assignments/) (two **posing**
problems, two **locomotion** problems; this is a locomotion problem,
peer to Shira's). All four problems end in a runnable demo you can
record and show at the checkpoint.

## The goal

The robot walks straight ahead using the **wave gait**: legs step
**one at a time** instead of three at once. The result is a slower,
steadier walk — five legs are always on the ground supporting the
body while a single sixth leg is in the air.

## Why this problem

The tripod-walk demo runs the fastest gait there is — three legs in
the air at once. The wave gait is the opposite extreme: only one leg
in the air at a time. The mechanics underneath are identical — same
swing path, same stance push, same straight-line motion. The only
thing that changes is **when** each leg swings. That is the central
lesson: a "gait" is a choice about timing. Once you have seen this,
every other hexapod gait (ripple, metachronal, two-by-two) is just a
different timing schedule of the same parts.

You will end with two demos side by side — tripod and wave — and a
short note comparing them.

## Start from

Copy the [`../PhantomX/demos/tripod-walk/`](../PhantomX/demos/tripod-walk/)
folder, rename it `wave-walk/`, and work in a new file
`demo_wave_walk.py`. Keep `config.py`, `hexapod_ik.py` and
`hexapod_model.py` unchanged — those are shared and fixed.

## The key idea

In the tripod-walk demo, the six legs are split into two groups of
three (tripod A: legs 0, 2, 4; tripod B: legs 1, 3, 5). Group A's
swing phase is the same as group B's stance phase, and vice versa.
You can write this as a **per-leg phase offset**:

```
tripod offsets (in cycles): leg 0 → 0,   leg 1 → 0.5, leg 2 → 0,
                            leg 3 → 0.5, leg 4 → 0,   leg 5 → 0.5
```

The wave gait keeps the same swing/stance shape but uses **six**
evenly-spaced offsets — one leg swings, the others all push:

```
wave offsets (in cycles):   leg 0 → 0,   leg 1 → 1/6, leg 2 → 2/6,
                            leg 3 → 3/6, leg 4 → 4/6, leg 5 → 5/6
```

For the gait to be stable the **swing duration** also has to shrink:
in tripod each leg is in the air for half the cycle (duty factor
1/2); in wave each leg is in the air for one-sixth (duty factor
5/6). One leg in the air at a time means the swing has to be quick.

So the recipe is: take `walk_targets` from the tripod demo, replace
the two-group phase offsets with six-group offsets, and shrink the
swing window of each leg's phase from 0.5 to 1/6.

## Step by step

1. Open `walk_targets` in the tripod-walk demo and read it until you
   can name, for any leg `i` and time `t`: which phase is it in
   (swing or stance), how far along it is, and what the foot target
   is.
2. Replace the per-leg phase offset with a list of six offsets:
   `OFFSETS = [i / 6 for i in range(6)]`.
3. Change the swing window from `0.5` of the cycle to `1.0 / 6.0`.
   A leg is in swing when its local phase is in `[0, 1/6)` and in
   stance for the rest.
4. The swing's vertical lift `dz` and the stance's backward push
   `dx` stay the same shape; only their **timing** changes.
5. Run it in the viewer. The body should creep forward smoothly with
   only one foot visibly off the ground at a time.
6. Run the original tripod walk for the same `WALK_DISTANCE` and
   note how long each takes; record the comparison.

## Watch out for

- **Duty factor matters.** If you change the offsets to six-spaced
  but leave the swing window at 0.5, two or three legs end up in
  the air at once and the robot falls. Shrink the swing window to
  match.
- **Cycle period.** The wave gait is slower per cycle for the same
  comfortable swing speed. Bumping the cycle period up by ~2×
  usually keeps each leg's swing reachable.
- The robot should walk straight, not crab sideways. If the body
  drifts off-axis, check that the swing exactly returns the foot to
  its home position (the swing must undo the stance).
- Keep the tripod demo runnable. You're adding a sibling, not
  replacing.

## Deliver

The `wave-walk/` folder, `demo_wave_walk.py`, a `--check`, a short
`README.md`, and a screen recording. The README should include one
or two sentences comparing tripod vs wave — which is faster, which
felt steadier, anything else you noticed.

## Success check (put this in `--check`)

Every step of the gait is reachable (no `ValueError`); over an 8 s
run only one foot leaves the ground at a time (you can verify this
by counting feet above the clearance threshold in each frame); and
the trunk has moved forward by a clear amount with no sideways
drift.

## If there is time (stretch)

Implement the **ripple gait** as a third demo — two legs swinging at
a time, with offsets `[0, 2/6, 4/6, 1/6, 3/6, 5/6]` and a swing
window of `2/6`. Compare all three (tripod, ripple, wave) in a
short table: speed, stability, smoothness.

---

**Where this leads:** changing only the timing to get a different
gait is exactly the foundation for the Stage B gait work and for
later RL gait discovery. A student who finishes this has built a
real piece of the robot.
