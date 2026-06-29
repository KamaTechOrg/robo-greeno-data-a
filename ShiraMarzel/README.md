# Shira Marzel · שירה מרזל

KamaTechOrg · Robo-Greeno Data A · 2026

## About me

_One paragraph: your year, background, what drew you to this project._

## My assignment — Problem B: Turn in place

→ **Full spec, here in this folder:** [`Problem-B-Turn-In-Place.md`](./Problem-B-Turn-In-Place.md)

The robot spins on the spot using the same alternating tripod rhythm
— a stance foot traces an arc instead of a straight line. Builds on
the [`PhantomX/demos/tripod-walk/`](../PhantomX/demos/tripod-walk/)
demo.

**Deliver:** a `turn-in-place/` folder with `demo_turn_in_place.py`,
a `--check`, a short README, and a screen recording.

(Drawn from the two-problem set in
[`../PhantomX/assignments/`](../PhantomX/assignments/); the companion,
Problem A — Body-pose control, goes to Hadas Sigaron.)

## My demo

→ **Self-contained folder:** [`turn-in-place/`](./turn-in-place/) —
`demo_turn_in_place.py` (the turn gait, the part I own) + the three
shared modules + a folder [`README`](./turn-in-place/README.md).
Run `python demo_turn_in_place.py --check`; it prints
`ALL CHECKS PASSED` (in sim the robot turns ~178° in 8 s with ~0.1 cm
drift — it spins, it does not walk away).

→ **Colab notebook:** [`turn_in_place_demo.ipynb`](./turn_in_place_demo.ipynb)
— Runtime → Run all: writes the modules, runs the self-test, and
renders an inline video of the hexapod spinning. No robot needed.

## My weekly log

- **Week 1 (2026-05-18):** [ ] Read `PLAN.md`. Edit this README → fill in "About me". Reply to the Week 1 issue with a link to your commit.
- **Week 2 (2026-05-25):** [ ] Run `notebooks/leg_kinematics_colab.ipynb` on Colab; paste a screenshot of the rendered leg into `experiments/`.
- **Week 3 (2026-06-01):** [ ] Open `notebooks/robo_greeno_3plus3_colab.ipynb`; commit one observation about the gait diagram to `notes/`.
- **Week 4 (2026-06-08):** [ ] Train PPO on the hexapod env (`RL/hexapod_env.py`) for 20k steps; save the model + a video into `experiments/`.
- **Week 5 (2026-06-15):** [ ] Write a short reflection (3–5 sentences) on what surprised you. Commit to `notes/`.

## Contents

- `notes/` — what I'm learning
- `experiments/` — code I'm trying
- `presentation/` — slides for the final demo

## Contact

s0527684199@gmail.com · GitHub [@your-username-here](#)

> *Replace the GitHub link above with your handle once you've made your first commit.*
