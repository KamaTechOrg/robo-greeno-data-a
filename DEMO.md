# Robo-Greeno Data A — Team Demo Video

Recording of the full team demo session for the Robo-Greeno **Data A** track.

## 🎥 Watch the demo

**[▶ Team Demo — Loom](https://www.loom.com/share/f6e59470fcdc4c89b8f049259a3c8dac)**

This Loom is the single recording for the **entire demo (all students and
topics)**. The **Google Meet session recording is contained inside the Loom
video** — screen share of the running demos plus the live walkthrough and
discussion. Open the link above to watch the complete Google Meet demo.

## Featured in this session

- **Shiri Stern — wave-walk:** hexapod wave-gait demo, merged into `main` via PR
  [#2](https://github.com/KamaTechOrg/robo-greeno-data-a/pull/2) "add wave walk"
  (commit `e6a3fec`). Code:
  [`ShiriStern/wave-walk/`](ShiriStern/wave-walk).

- **Hadas Sigaron — body-pose control (Problem A):** all six feet stay planted
  while the body rises, lowers, pitches and rolls — every pose driven by the
  inverse kinematics. Code: [`HadasSigaron/`](HadasSigaron) — runnable
  [`demo_body_pose.py`](HadasSigaron/demo_body_pose.py) and the Colab notebook
  [`demo_body_pose.ipynb`](HadasSigaron/demo_body_pose.ipynb)
  ([▶ open in Colab](https://colab.research.google.com/github/KamaTechOrg/robo-greeno-data-a/blob/main/HadasSigaron/demo_body_pose.ipynb)).

- **Shira Marzel — turn in place (Problem B):** rotate the hexapod on the spot
  with a tripod gait whose stance feet trace arcs. Assignment spec:
  [`ShiraMarzel/Problem-B-Turn-In-Place.md`](ShiraMarzel/Problem-B-Turn-In-Place.md)
  — demo in progress.

- **Miriam Kahaneman — draw a shape in the air (Problem C):** lift one leg and
  trace a shape in the air with the foot, using the inverse kinematics.
  Assignment spec:
  [`MiriamKahaneman/Problem-C-Draw-Shape.md`](MiriamKahaneman/Problem-C-Draw-Shape.md)
  — demo in progress.

## 📚 Further learning — the Physical AI tutorial

New to embodied AI? Start with our four-chapter, beginner-friendly
**[Physical AI tutorial](tutorial/README.md)**. It renders natively right here on
GitHub — clickable, no website or build step — and each chapter ends with a
runnable Colab notebook.

1. **[LLM vs Physical AI](tutorial/01-llm-vs-physical-ai.md)** — what changes when intelligence gets a body.
2. **[Legs and Fingers](tutorial/02-legs-and-fingers.md)** — why nature builds six, eight, and two legs (and ten fingers) the way it does.
3. **[MuJoCo Intuition](tutorial/03-mujoco-intuition.md)** — how a physics simulator actually works, with zero hand-waving.
4. **[RL Intuition](tutorial/04-rl-intuition.md)** — states, actions, rewards, PPO, and sim-to-real, through one hexapod learning to walk.

## 🤝 Cross-team coordination — ready

Data A's outputs are designed to plug into the other Robo-Greeno tracks. The shared
interfaces are defined and we're ready to integrate:

- **Embedded** — a shared hexapod **URDF + servo conventions**, so simulation and
  firmware target the exact same robot.
- **Cloud** — the Week-10 **hand-off package**: telemetry schema + relative-pose
  data for collaborative mapping.
- **Data B** — agreed **timestamp + body-frame conventions** on relative-pose
  output, so vision-based mapping fuses cleanly with camera frames.

> [!NOTE]
> **Let's work together.** Reach out to schedule a cross-team demo or to lock down
> any interface detail — Data A is ready to integrate.
