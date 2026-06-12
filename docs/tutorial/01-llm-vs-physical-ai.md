---
description: >-
  What is Physical AI and how is it different from LLMs like ChatGPT?
  Tokens vs torques, Moravec's paradox, and why robots need simulators
  — explained for beginners.
---

# Chapter 1 — LLM AI vs Physical AI

## What is Physical AI?

**Physical AI is artificial intelligence that controls a body in the
real world** — a robot arm, a drone, a self-driving car, or our
six-legged spider robot. Where a large language model (LLM) predicts
the next *word*, a Physical AI predicts the next *motor command* — and
the world grades its answer with gravity, friction, and broken servos.

## The poet who can't stand up

Ask a modern LLM to explain quantum field theory in the style of Dr.
Seuss and it delivers. Ask it to drive 18 servo motors so a half-kilo
hexapod doesn't face-plant, and it has nothing to offer. This isn't a
gap in cleverness — it's a gap in *kind*. The two problems differ in
almost every dimension that matters:

| | LLM AI | Physical AI |
|---|---|---|
| Output | next token (a word piece) | next torque (a motor command) |
| Speed required | seconds is fine | every 10–20 **milliseconds**, forever |
| A single mistake | mildly embarrassing | robot falls, servo strips a gear |
| Undo button | regenerate the answer | none — physics already happened |
| Training data | the entire internet | doesn't exist; you must *generate* it |
| World model | implicit, learned from text | explicit: mass, friction, contact forces |

## Moravec's paradox: the hard things are easy and the easy things are hard

In the 1980s roboticist Hans Moravec noticed something strange: making
computers do "hard" human things (chess, calculus, law exams) is easy,
while making them do "easy" things (walking, picking up a cup) is
brutally hard. The reason is evolutionary: nature spent **hundreds of
millions of years** perfecting sensorimotor control and only a few tens
of thousands on abstract reasoning. Walking *feels* easy to you because
the hard part is hidden in machinery so old and optimized you can't
even feel it running.

That's why Physical AI — not chess — is the frontier.

## Why is there no "internet of movement"?

LLMs got great because text is cheap: trillions of tokens, free to
copy. There is no equivalent dataset of "what torque to send to servo
#14 when the robot tips left on wet soil." Every robot, terrain, and
task is different, and collecting real-robot data breaks real robots.

The fix is the central trick of modern robotics:

> **Simulation is to Physical AI what the internet was to LLMs — the
> place where unlimited training data comes from.**

A physics simulator like [MuJoCo](03-mujoco-intuition.md) can run our
hexapod thousands of times faster than real time, in thousands of
parallel copies, falling over millions of times — for free. That's
where Chapters 3 and 4 take us.

## Where they meet

The frontier in 2026 is gluing the two together: LLM-class models for
high-level reasoning ("the tomato row is to the left, go inspect it")
sitting on top of Physical AI policies for low-level control ("fire
this gait pattern, shift weight now"). Robo-Greeno lives squarely in
the second layer — the layer that has to be *right* 50 times per
second.

!!! abstract "Key takeaways"
    - Physical AI outputs motor commands under hard real-time limits;
      mistakes have irreversible physical costs.
    - Moravec's paradox: sensorimotor control is harder than abstract
      reasoning, because evolution optimized it longer.
    - There's no internet-scale dataset of movement — simulation
      generates the training data instead.

## FAQ

**Is Physical AI the same as robotics?**
Robotics is the body (mechanics, electronics); Physical AI is the
learned brain that controls it. You need both.

**Can't we just put ChatGPT in a robot?**
For high-level planning, partly yes. For balance and locomotion, no —
language models are far too slow and have no notion of torque, contact,
or inertia.

**Do I need expensive hardware to learn Physical AI?**
No. This entire project runs in simulation on a free Google Colab GPU,
and the real robot it targets costs roughly \$100 in parts.

---

*Next: [Chapter 2 — Legs and Fingers: Nature's Engineering](02-legs-and-fingers.md)*
