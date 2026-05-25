# Problem A — Body-pose control

**Assigned to:** Hadas Sigaron ([`HadasSigaron/`](../../HadasSigaron/))
**Builds on:** [`demos/pose-wave/`](../demos/pose-wave/)

## The goal

All six feet stay planted on the ground. The body moves: it rises and
lowers, leans forward and back (pitch), and tilts side to side (roll),
in a smooth routine. Think of a person standing still with their feet
fixed, shifting their weight and looking around.

## Why this problem

The pose-wave demo moved a foot while the body stayed still. This is
the mirror image: move the body while the feet stay still. To do it,
the student has to think clearly about two reference frames — the
world (where the feet really are) and the body frame (where the
inverse kinematics does its work). It is also a real capability:
keeping the body level while the feet sit on uneven ground is exactly
this maths.

## Start from

Copy the `pose-wave/` folder, rename it `body-pose/`, and work in a
new file `demo_body_pose.py`. Keep `config.py`, `hexapod_ik.py` and
`hexapod_model.py` unchanged — those are shared and fixed.

## The key idea

The six feet are planted at fixed world positions. The IK (`leg_ik`,
`solve_all`) works in the **body frame**, with the body at the origin
and level. When the body moves to a new pose, each foot's position
in the body frame changes — even though the foot has not moved in the
world.

So the recipe is: for a chosen body pose, transform each fixed world
foot position into the body frame, then call `solve_all` as usual.

For a body at height `h` rotated by `pitch` (about Y) and `roll`
(about X), a foot at world point `p` has body-frame coordinates:

```
body_frame_foot = R_bodyᵀ · (p − body_centre)
```

where `body_centre = (0, 0, h)` and `R_body` is the body's rotation.

## Step by step

1. Build the list of fixed world foot positions. At the level pose,
   foot `i` sits on the ground at `(R·cos θ, R·sin θ, 0)` for that
   leg's mount angle `θ` and `R = STANCE_RADIUS`.
2. Write the rotation. You only need pitch (about Y) and roll (about
   X) — the same `math.sin` / `math.cos` used all through the IK.
3. Write `body_pose_targets(h, pitch, roll)`: for each world foot,
   subtract the body centre, apply the inverse body rotation, and
   collect the six body-frame targets.
4. Write a `pose_at(t)` routine that sweeps the body through:
   neutral → up → down → pitch forward → pitch back → roll left →
   roll right → neutral.
5. Reuse `render_demo` / the viewer from the demo to watch it.

## Watch out for

- Large tilts make a leg unreachable and `solve_all` raises
  `ValueError`. Start small (height ±2 cm, pitch/roll ±8°) and push
  outward until something cannot reach. That limit is a real fact
  about the robot — note it down.
- Pick a sign convention for "positive pitch" and stay consistent;
  check it by eye in the viewer.
- Rotate about the body centre, and apply the steps in a fixed order.

## Deliver

The `body-pose/` folder, `demo_body_pose.py`, a `--check`, a short
`README.md`, and a screen recording of the routine.

## Success check (put this in `--check`)

For ~40 body poses across the routine, `solve_all` succeeds with no
`ValueError`; and in simulation the robot holds each pose without a
foot leaving the ground or the body falling.

## If there is time (stretch)

Tilt the body to keep "looking" toward a point that moves; or add a
gentle body sway on a rhythm with the feet still planted.
