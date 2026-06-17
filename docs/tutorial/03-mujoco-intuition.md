---
description: >-
  MuJoCo tutorial for beginners: what a physics engine actually does,
  bodies, joints, actuators, timesteps, and contact forces — explained
  intuitively with a hexapod robot example.
---

> **📖 Physical AI Tutorial** &nbsp;·&nbsp; [🏠 Overview](index.md) &nbsp;·&nbsp; [◀ Ch 2](02-legs-and-fingers.md) &nbsp;·&nbsp; **Ch 3 — MuJoCo Without Tears** &nbsp;·&nbsp; [Ch 4 ▶](04-rl-intuition.md)

# Chapter 3 — MuJoCo Without Tears

## What does a physics engine actually do?

Strip away the mystique and a physics simulator is:

> **Newton's laws, in a for-loop.**

```python
while True:
    forces = gravity + motors + contacts   # what pushes on everything?
    acceleration = forces / mass           # F = ma, solved for a
    velocity += acceleration * dt          # integrate once
    position += velocity * dt              # integrate twice
```

That's it. [MuJoCo](https://github.com/google-deepmind/mujoco)
(**Mu**lti-**Jo**int dynamics with **Co**ntact, open-sourced by Google
DeepMind) is this loop made fast, accurate, and able to handle the one
genuinely hard part — contact — which we'll get to.

## The three nouns: bodies, joints, actuators

Every MuJoCo robot is built from three kinds of things. For our
hexapod:

- **Bodies** — the rigid pieces: one torso, and per leg a hip segment,
  femur, and tibia. Each has mass and inertia, like Lego bricks that
  weigh something.
- **Joints** — the permissions to move. A hinge joint says "these two
  bodies may rotate relative to each other around this axis." Our
  spider: 3 hinges per leg × 6 legs = **18 joints**.
- **Actuators** — the motors that push on joints. One servo per joint,
  18 total. In simulation, an actuator is just "a force applied at a
  joint, on command."

A robot description is a tree: torso at the root, legs branching off,
exactly like a skeleton.

```xml
<body name="torso">
  <geom type="box" size=".12 .09 .03" mass="0.5"/>
  <body name="leg1_hip">
    <joint name="leg1_coxa" type="hinge" axis="0 0 1" range="-45 45"/>
    <geom type="capsule" fromto="0 0 0  .05 0 0" size=".008"/>
    <!-- femur body, then tibia body, nest inside... -->
  </body>
  <!-- five more legs... -->
</body>
```

Read it like nesting dolls: a `<body>` inside a `<body>` is attached to
its parent; the `<joint>` says *how* it's allowed to move; the
`<geom>` gives it shape and mass.

## What is a timestep?

Reality is continuous; simulation is a flipbook. MuJoCo advances the
world in tiny frames called **timesteps** — typically **0.002 s**
(2 ms, 500 frames per second of simulated time). Each frame runs the
for-loop above once.

Why so small? Because between frames, physics is *frozen* — forces are
assumed constant. Big steps mean a foot can travel *through* the floor
before anyone notices. Small steps catch the contact in time. The
trade-off is pure speed-vs-accuracy, and 2 ms is the sweet spot for
walking robots.

## Contact: the genuinely hard part

Gravity is one line of code. **Touching** is the hard part, and for a
walking robot, touching *is* the job — six feet hitting dirt is the
entire game.

Why is contact hard? Because it's instantaneous and discontinuous: the
moment a foot meets the ground, an enormous force appears from nowhere
(it was zero a microsecond before), pointed exactly where needed to
stop penetration, plus friction sideways. The simulator has to solve a
little optimization problem *every timestep* to find a consistent set
of contact forces across all feet at once. MuJoCo's claim to fame is
solving this fast and stably — that's the "Co" in its name.

You'll feel this practically: simulation parameters for friction and
contact softness matter more for gait realism than almost anything
else.

## MJX: thousands of robots at once

Classic MuJoCo runs one world on a CPU. **MuJoCo MJX** reimplements
the same physics in JAX so it runs on a GPU — and a GPU's superpower is
doing the same thing thousands of times in parallel. So instead of one
spider learning to walk, you simulate **4,096 spiders at once** on a
free Colab T4. That firehose of experience is exactly what
reinforcement learning drinks — next chapter.

> [!NOTE]
> **Key takeaways**
> - A physics engine is Newton's laws integrated in tiny timesteps (~2 ms).
> - Robots are trees of bodies, connected by joints, driven by actuators — 18 of each for our hexapod's legs.
> - Contact forces are the hard, discontinuous part; MuJoCo's contact solver is why it's the standard for legged robots.
> - MJX = MuJoCo on GPU = thousands of parallel simulations = free training data.

## FAQ

**Is MuJoCo hard to learn?**
The core mental model fits in this chapter. The XML format takes an
afternoon. Mastery of contact parameters takes longer — but you can
make a hexapod walk in your first week.

**Is MuJoCo free?**
Yes — fully open source (Apache 2.0) since Google DeepMind acquired
and released it in 2021–22.

**MuJoCo vs Gazebo vs Isaac Sim?**
MuJoCo: fastest and most accurate contact for learning research.
Gazebo: deep ROS integration for systems work. Isaac Sim:
photorealistic rendering, heavy GPU requirements. For learning to
*walk*, MuJoCo is the standard.

---

[◀ Chapter 2](02-legs-and-fingers.md) &nbsp;·&nbsp; [🏠 Overview](index.md) &nbsp;·&nbsp; [**Next: Chapter 4 — Reinforcement Learning ▶**](04-rl-intuition.md)
