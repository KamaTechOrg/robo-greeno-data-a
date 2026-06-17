---
description: >-
  Reinforcement learning explained intuitively: states, actions,
  rewards, PPO, reward shaping, domain randomization and sim-to-real —
  all through teaching a hexapod robot to walk.
---

> **📖 Physical AI Tutorial** &nbsp;·&nbsp; [🏠 Overview](index.md) &nbsp;·&nbsp; [◀ Ch 3](03-mujoco-intuition.md) &nbsp;·&nbsp; **Ch 4 — Reinforcement Learning** &nbsp;·&nbsp; 🏁 Final chapter

# Chapter 4 — Reinforcement Learning, Intuitively

## Training a puppy with treats

You can't *explain* "fetch" to a puppy. You wait for behavior that's
vaguely right, reward it instantly, and let the puppy figure out the
pattern. Over many trials the puppy internalizes a policy: *in this
situation, that action earns treats.*

**Reinforcement learning (RL) is exactly this, with math.** Nobody
writes down how to walk. The robot tries, gets scored, and gradually
shifts toward higher-scoring behavior.

## The three words that matter

Every RL problem is defined by three things. For our hexapod:

| RL term | Puppy version | Hexapod version |
|---|---|---|
| **State** (what it senses) | what the puppy sees and feels | 18 joint angles + joint velocities + body tilt from the IMU |
| **Action** (what it does) | run, sit, bite the sofa | 18 torque commands, one per servo, every 20 ms |
| **Reward** (the treat) | snack + "good dog!" | points for forward speed, minus penalties (below) |

A **policy** is the learned mapping state → action — a small neural
network. Training = adjusting it so total reward goes up. That's the
whole field in one sentence.

## Reward design is the real job

Here's the dirty secret: the algorithm is a library import. The thing
*you* actually engineer is the **reward function** — and the robot
will exploit any loophole you leave, like a genie reading your wish
literally:

- Reward "forward velocity" only → it learns to **dive forward and
  crash**. Maximum velocity, briefly.
- Add "stay alive" → it stands perfectly still. Safe, zero progress.
- Reward distance, alive-ness, *and* penalize energy → it discovers
  jittery vibration-walking that games the physics.

Real reward functions are negotiated treaties:

```python
reward = (
    + 2.0 * forward_velocity      # make progress
    - 0.1 * energy_used           # don't burn the servos
    - 0.5 * body_wobble           # keep the torso level
    - 5.0 * fell_over             # seriously, don't
)
```

Watching a policy exploit your reward — then patching the loophole —
is the daily life of an RL practitioner, and honestly the fun part.

## PPO in one paragraph

The training algorithm we use, **PPO (Proximal Policy Optimization)**,
does one intuitive thing: after each batch of experience it nudges the
policy toward actions that scored above expectation — but **clips the
nudge** so the policy never changes too much at once. Small steps,
because a walking policy is a house of cards: one wild update and the
robot forgets everything. "Proximal" literally means *stay close to
what you were.* It's the default workhorse of robot RL, available
off-the-shelf in
[Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3).

## Why simulation makes this possible

A puppy learns fetch in dozens of trials. PPO needs **millions** of
timesteps. On a real robot that's weeks of stripped gears and broken
legs. In MuJoCo MJX ([Chapter 3](03-mujoco-intuition.md)) with 4,096
parallel spiders, a million steps takes minutes on a free Colab GPU.
Simulation doesn't just *help* robot RL — it's what makes it possible
at all.

## Sim-to-real: training in the rain on purpose

A policy trained in one pristine simulation learns that world's quirks
— exact friction, exact motor strength — and fails on real dirt. This
is the **sim-to-real gap**.

The standard fix is **domain randomization**: during training,
deliberately vary everything — friction, masses, motor strength, sensor
noise, terrain bumps. A policy that walks across *thousands of randomly
different simulated worlds* treats the real world as just one more
variation. Like a footballer who trains in rain, mud, and wind: match
day weather can't surprise them.

For Robo-Greeno there's one more constraint: the trained network must
be small enough to run on a **Raspberry Pi** — a policy that needs a
data center can't ride on a \$100 spider. Tiny networks (a few hundred
KB) turn out to be plenty for walking.

> [!NOTE]
> **Key takeaways**
> - RL = puppy training: state, action, reward; the policy is a neural net mapping senses to torques.
> - Reward design, not the algorithm, is where the engineering lives — the robot will exploit every loophole.
> - PPO improves the policy in small, clipped steps so learning never collapses.
> - Domain randomization closes the sim-to-real gap by making training harder than reality.

## FAQ

**How long does it take to train a hexapod to walk?**
With MJX on a free Colab GPU: minutes-to-hours for a basic gait. The
project's Week 6–8 phase covers exactly this.

**Is RL the only way robots learn to walk?**
No — classic gait engineering (Chapter 2's tripod gait, hand-tuned)
works well on flat ground. RL wins on rough terrain, recovery from
pushes, and tasks too messy to hand-code. Robo-Greeno does both, in
that order.

**Do I need to understand the PPO math?**
To use it, no — Stable-Baselines3 is three lines of code. To research
it, eventually. Start by training one and watching what it does.

---

[◀ Chapter 3](03-mujoco-intuition.md) &nbsp;·&nbsp; [🏠 Tutorial Overview](index.md) &nbsp;·&nbsp; [📦 Repository](https://github.com/KamaTechOrg/robo-greeno-data-a)

🎉 **You finished the tutorial.** Next: open the runnable notebooks in [`notebooks/`](../../notebooks) and train a hexapod yourself.
