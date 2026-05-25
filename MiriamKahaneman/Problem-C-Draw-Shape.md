# Problem C — Draw a shape in the air

**Assigned to:** Miriam Kahaneman
**Builds on:** [`../PhantomX/demos/pose-wave/`](../PhantomX/demos/pose-wave/)
**Companion problems (for reference):**
[Problem A — Body-pose control](../HadasSigaron/Problem-A-Body-Pose.md) · Hadas Sigaron
[Problem B — Turn in place](../ShiraMarzel/Problem-B-Turn-In-Place.md) · Shira Marzel
[Problem D — Wave gait](../ShiriStern/Problem-D-Wave-Gait.md) · Shiri Stern

---

This is your assignment for Stage A of the kinematics track. The two
demos in `PhantomX/demos/` — `pose-wave/` and `tripod-walk/` — are
worked examples: they already run. They are **not** the assignment.
They are the starting point you copy, read, and then change into
something new that is yours.

Your problem is **Problem C — Draw a shape in the air**, one of four
matched-difficulty problems posted in
[`../PhantomX/assignments/`](../PhantomX/assignments/) (two **posing**
problems, two **locomotion** problems; this is a posing problem,
peer to Hadas's). All four problems end in a runnable demo you can
record and show at the checkpoint.

## The goal

The robot stands stably on five legs while the sixth lifts off the
ground and **traces shapes in the air** — a circle, a square, and a
figure-eight — at a chosen size and speed, then sets the foot back
down. The body stays still throughout.

## Why this problem

The pose-wave demo moved a single foot through a one-dimensional sine
sweep. Drawing a real shape is the next step: you design a
**parametric foot trajectory** — a function `foot(t)` that returns
a 3-D point — and feed it through the existing IK. Doing this brings
you face to face with the leg's **reachable workspace**: not every
point in space is achievable, and you have to discover where the
edges are. This is the same idea later used for placing feet on
uneven terrain or for any task where the foot has to follow a
prescribed path.

## Start from

Copy the [`../PhantomX/demos/pose-wave/`](../PhantomX/demos/pose-wave/)
folder, rename it `draw-shape/`, and work in a new file
`demo_draw_shape.py`. Keep `config.py`, `hexapod_ik.py` and
`hexapod_model.py` unchanged — those are shared and fixed.

## The key idea

Pick one leg (say, the front-right leg, index 0). The five other feet
hold their stance positions; the chosen foot follows a parametric
path centred on a point in front of the leg, in the leg's local
frame, at some clearance height above the ground.

Each shape is just a function `(u, v)` of a phase variable
`s ∈ [0, 1]` that loops as `t` advances:

```
Circle:        u = R · cos(2π s),         v = R · sin(2π s)
Square:        side-by-side linear segments — 4 pieces of length s
Figure-eight:  u = R · sin(2π s),         v = R · sin(4π s) / 2
               (a Lissajous; alternative: lemniscate r² = a² cos 2θ)
```

The 3-D target for the chosen leg's foot is then:

```
target = leg_anchor + (centre_u + u, centre_v + v, clearance_z)
```

The other five feet stay at their planted positions — same as the
default stance pose used in pose-wave.

## Step by step

1. Read `demo_pose_wave.py` until the swing/render loop is clear.
   Note which leg moves and how a single target gets passed to
   `solve_all`.
2. Choose the swung leg index and the shape centre — pick a point
   in front of and slightly outside the leg anchor, at a clearance
   height (e.g. 4–6 cm above ground).
3. Write three trajectory functions: `circle(s, R)`, `square(s, L)`,
   `figure8(s, R)`. Each returns the `(u, v)` offset for a given
   phase `s ∈ [0, 1]`.
4. Write `foot_at(t)`: pick which shape is active right now (cycle
   through them), compute the offset, add it to the shape centre,
   and return the 3-D target.
5. In the main loop: build the six-foot target list with five feet
   at stance and the chosen foot at `foot_at(t)`; call `solve_all`
   as usual.
6. Use the demo's viewer to watch the foot trace each shape, then
   add a short "rest" between shapes for clarity.

## Watch out for

- **Reachable workspace.** A circle that's too big or centred too
  far out will push the foot past where the leg can reach, and
  `solve_all` raises `ValueError`. Start small (R ≈ 3 cm) and grow
  until something cannot reach. **Note the limit.** That envelope
  is a real fact about this leg.
- The foot must **leave the ground** before tracing and **come back
  down** after. Lift it cleanly to the clearance height before the
  shape starts; lower it cleanly after.
- The other five feet must stay planted. If the body wobbles in the
  viewer, one of the stance targets has drifted — check the target
  list at each step.
- Keep `t` and `s` separate. `t` is real time; `s` is the phase
  within the current shape and loops 0→1.

## Deliver

The `draw-shape/` folder, `demo_draw_shape.py`, a `--check`, a short
`README.md`, and a screen recording showing all three shapes.

## Success check (put this in `--check`)

For ~120 trajectory points across all three shapes, `solve_all`
succeeds with no `ValueError`; the swung foot stays within the chosen
clearance height (so it never dips below ground); the five stance
feet do not drift; and the chosen shape is recognisable on screen.

## If there is time (stretch)

Add a fourth shape of your own choosing (a heart, a star, your
initials) — anything that closes on itself. Or sweep the same shape
at three different sizes back-to-back, and report the largest size
that still fits inside the leg's reach.

---

**Where this leads:** parametric foot trajectories are the building
block for both stepping over an obstacle and placing a foot on
uneven terrain — both are Stage B and later work. A student who
finishes this has built a real piece of the robot.
