# Robo-Greeno Data A — Team Demo

Demo session for the Robo-Greeno **Data A** (hexapod locomotion) track. Each
student took one **Stage-A kinematics problem**, copied a worked example, and
turned it into a runnable demo of their own — a self-test (`--check`), a MuJoCo
viewer, and a Colab notebook that renders an inline video with no robot needed.

The four problems are matched in difficulty: **two posing** (the body or one foot
moves, the robot stays put) and **two locomotion** (the robot walks or turns).
They share one robot — the same `config.py`, `hexapod_ik.py` and
`hexapod_model.py` — so every demo targets the exact same 18-servo hexapod.

## 🎥 Watch the demo

**[▶ Team Demo — Loom](https://www.loom.com/share/f6e59470fcdc4c89b8f049259a3c8dac)**

This Loom is the single recording for the **entire demo (all students and
topics)** — the Google Meet session recording is contained inside it: screen
share of the running demos plus the live walkthrough and discussion.

## Status at a glance

| Student | Problem | Type | Demo to run | Verified | Status |
|---|---|---|---|---|---|
| **Shiri Stern** | D — Wave gait | locomotion | `ShiriStern/wave-walk/demo_wave_walk.py` | walks **+42.9 cm / 10 s** | ✅ done · recorded |
| **Hadas Sigaron** | A — Body-pose control | posing | `HadasSigaron/demo_body_pose.py` | feet planted to **0 m** | ✅ done · recorded |
| **Shira Marzel** | B — Turn in place | locomotion | `ShiraMarzel/turn-in-place/demo_turn_in_place.py` | spins **+177.9° / 8 s** | ✅ done · recorded |
| **Miriam Kahaneman** | C — Draw a shape in the air | posing | `MiriamKahaneman/draw-shape/` *(planned)* | — | 🚧 in progress |

> Mentor: **Ingyu Koh** ([`project/IngyuKoh/`](project/IngyuKoh)) — Data A track, May–Jul 2026.

---

## Shiri Stern — Problem D: The wave gait  ✅

**[📄 spec](ShiriStern/Problem-D-Wave-Gait.md) · [📁 code](ShiriStern/wave-walk) · [▶ open in Colab](https://colab.research.google.com/github/KamaTechOrg/robo-greeno-data-a/blob/main/ShiriStern/wave_walk_demo.ipynb)**

**What it does.** The hexapod walks straight ahead using the **wave gait** — legs
step **one at a time** instead of three at once. Five legs are always on the
ground supporting the body while a single sixth leg swings forward, giving a
slow, steady, very stable walk.

**The key idea — a gait is a choice of timing.** The fast tripod walk splits the
six legs into two groups of three, half a cycle apart (per-leg phase offsets
`0, ½, 0, ½, 0, ½`). The wave gait keeps the *exact same* swing path and stance
push and changes only **when** each leg swings: six evenly-spaced offsets
`0, ⅙, 2⁄6 … 5⁄6`. For stability the swing window also shrinks — each leg is airborne
for just **1⁄6** of the cycle (duty factor 5⁄6) instead of ½ — so only one foot is
ever off the ground. That one insight (gait = timing schedule of identical parts)
generalises to ripple, metachronal, and every other gait.

**Run it.** `python demo_wave_walk.py` for the viewer, or `--check` for the
headless self-test. The folder keeps the original `demo_tripod_walk.py` as a
sibling for a direct tripod-vs-wave comparison.

**Verified:** `--check` → **ALL CHECKS PASSED** — every gait step reachable, robot
walks forward **+42.9 cm in 10 s** at a 7.5 cm ride height, no sideways drift.
Merged to `main` via PR [#2](https://github.com/KamaTechOrg/robo-greeno-data-a/pull/2) (commit `e6a3fec`).

**Recording:** captured in the team session (Loom above).

---

## Hadas Sigaron · הדס סיגרון — Problem A: Body-pose control  ✅

**[📄 spec](HadasSigaron/Problem-A-Body-Pose.md) · [📁 code](HadasSigaron) · [▶ open in Colab](https://colab.research.google.com/github/KamaTechOrg/robo-greeno-data-a/blob/main/HadasSigaron/demo_body_pose.ipynb)**

**What it does.** All six feet stay **planted** on the ground while the **body**
moves — it rises, lowers, pitches forward and back, then rolls, in a smooth
keyframed routine. Think of a person standing with their feet fixed, shifting
their weight and looking around. One height/pitch/roll command drives all 18
servos.

**The key idea — two reference frames.** A foot that is fixed in the *world* is
**not** fixed in the *body frame* once the body tilts. The inverse kinematics
works in the body frame, so each frame the demo takes the six planted world feet,
re-expresses them in the moving body frame —
`body_frame_foot = R_bodyᵀ · (p − body_centre)` — and hands those six targets to
`solve_all`. Keeping the body level while the feet sit where they are is exactly
the maths later used to stand on uneven terrain.

**Run it.** `python demo_body_pose.py` for the viewer, `--check` for the
self-test; the Colab notebook renders the routine as an inline video.

**Verified:** `--check` → **ALL CHECKS PASSED** — the neutral pose matches the
standing stance to **0 m** (the feet really do stay planted), all ~72 poses in
the routine are reachable, and the body holds itself up at 5.4 cm throughout.
*(A bug where the planted feet sat one foot-radius too low — making the body
lurch at t=0 — was fixed in commit `4ded3f4`, with a "feet stay planted" guard
added to the self-test.)*

**Recording:** individual screen recording captured; watch it in the team session
Loom above.

---

## Shira Marzel · שירה מרזל — Problem B: Turn in place  ✅

**[📄 spec](ShiraMarzel/Problem-B-Turn-In-Place.md) · [📁 code](ShiraMarzel/turn-in-place) · [▶ open in Colab](https://colab.research.google.com/github/KamaTechOrg/robo-greeno-data-a/blob/main/ShiraMarzel/turn_in_place_demo.ipynb)**

**What it does.** The hexapod **spins on the spot** to face a new direction
without walking anywhere, using the same alternating-tripod rhythm as the
straight walk. `--cw` spins it the other way.

**The key idea — change the foot path, not the scaffold.** The whole tripod
machinery is reused — swing and stance, tripod A (front-left, back-left,
mid-right) and tripod B (mid-left, back-right, front-right), the phase logic. The
*only* change is the path a stance foot follows: a straight backward slide (which
pushes the body forward) becomes an **arc about the body centre**. Rotate every
stance foot's home `(hx, hy)` by `−Δ` —
`x' = hx·cos a − hy·sin a`, `y' = hx·sin a + hy·cos a` — and the body rotates by
`+Δ`; do it each step and the turns add up. The lesson: the body's motion is
decided entirely by the path each foot traces on the ground.

**Run it.** `python demo_turn_in_place.py` (viewer), `--check` (self-test),
`--cw` (clockwise); the Colab notebook renders the spin as an inline video.

**Verified:** `--check` → **ALL CHECKS PASSED** — every gait step reachable, the
trunk turns **+177.9° in 8 s** with only **0.1 cm** drift and stays upright (it
spins, it does not walk away).

**Recording:** individual screen recording captured; watch it in the team session
Loom above.

---

## Miriam Kahaneman · מרים כהנמן — Problem C: Draw a shape in the air  🚧

**[📄 spec](MiriamKahaneman/Problem-C-Draw-Shape.md) · [📁 folder](MiriamKahaneman)**

> **Status: in progress.** The assignment and plan are in place; the demo folder
> (`draw-shape/demo_draw_shape.py` + `--check` + recording) is not finished yet.

**What it will do.** The robot stands stably on **five** legs while the **sixth**
lifts off and **traces shapes in the air** — a circle, a square, and a
figure-eight — at a chosen size and speed, then sets the foot back down. The body
stays still throughout.

**The key idea — a parametric foot trajectory.** Where Hadas's pose problem moved
the whole body, this moves a single foot along a designed path. Each shape is a
function of a phase `s ∈ [0, 1]` that loops as time advances —
e.g. circle `u = R·cos 2πs, v = R·sin 2πs`; figure-eight (Lissajous)
`u = R·sin 2πs, v = R·sin 4πs / 2` — added to a centre point in front of the leg
at a clearance height, then fed straight through the existing IK. The five other
feet hold their stance. The real lesson is the leg's **reachable workspace**: a
circle that is too big or centred too far out pushes the foot past where the leg
can reach and `solve_all` raises — finding that edge is the point.

**Next steps:** copy `PhantomX/demos/pose-wave/` → `draw-shape/`, write the three
trajectory functions and `foot_at(t)`, add a `--check` over ~120 trajectory
points, and record the three shapes.

---

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
  firmware target the exact same robot. The physical wiring (CSI camera → Pi 5,
  I²C → PCA9685 ×2 → 18 servos) is in
  [`interfaces/MujocoRpiPca9685.pdf`](interfaces/MujocoRpiPca9685.pdf).
- **Cloud** — the Week-10 **hand-off package**: telemetry schema + relative-pose
  data for collaborative mapping.
- **Data B** — agreed **timestamp + body-frame conventions** on relative-pose
  output, so vision-based mapping fuses cleanly with camera frames.

> [!NOTE]
> **Let's work together.** Reach out to schedule a cross-team demo or to lock down
> any interface detail — Data A is ready to integrate.
