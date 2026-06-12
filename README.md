# Robo-Greeno — Data A

Open-source workspace for the **Data A** track of the
[KamaTech](https://kamatech.org.il) OSS On-the-Job Training program,
Robo-Greeno project (May 2026 - Jul 2026, with possible extension).

Robo-Greeno is a swarm of six-legged spider robots and a "carrier"
information dog, designed to wander and act in agricultural settings
(small spiders) and ferry information back to a main server (carriers).
This repository covers the **Data A** track: hexapod kinematics, gait
generation, IMU stabilization, and reinforcement-learning locomotion in
simulation, with a focus on policies that fit ESP32 + Raspberry Pi
class hardware.

## Team

- **Program director:** Shmuel Fine, [KamaTech](https://kamatech.org.il)
- **Mentor (Data A):** Ingyu Koh ([@ingyukoh](https://github.com/ingyukoh))
- **Participants:** 6 members, kickoff Wed May 6 2026
- **Standing meetings:** Mon / Wed / Thu, 10:30 IDT

## Stack

Selected for student laptops + free GPU credits. No expensive lab HW.

- **Simulation:** [MuJoCo](https://github.com/google-deepmind/mujoco)
  (Google DeepMind, open source)
- **RL framework:** [Gymnasium](https://github.com/Farama-Foundation/Gymnasium)
  + [Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3)
- **Parallel RL:** [MuJoCo MJX](https://github.com/google-deepmind/mujoco/tree/main/mjx)
  on free Google Colab T4 (for the Wk 6-8 phase)
- **Filters:** Madgwick / Mahony AHRS for IMU fusion
- **Target hardware:** ESP32 (~\$4) for low-level motion + IMU, Raspberry
  Pi 4/5 for on-device inference and BLE coordination

See [`PLAN.md`](PLAN.md) for the 10-week phase plan and
[`REFERENCES.md`](REFERENCES.md) for the starter reading list.

## Repository layout

```
robo-greeno-data-a/
├── README.md          this file
├── PLAN.md            10-week iteration plan with bootcamp lab outputs
├── REFERENCES.md      papers, datasets, URDFs, and tutorials
├── CONTRIBUTING.md    how participants and TAs work in this repo
├── LICENSE            MIT
└── docs/
    ├── tutorial/      Physical AI tutorial (published to GitHub Pages)
    └── sketches/      design notes and origin material
```

Code lands week by week as each phase is taught. The participants build
the labs; the mentor seeds the plan.

## Bootcamp pipeline

Each 10-week phase ships an open-source repo, a sim video, and metrics
(cost-of-transport, task success rate, relative-pose RMSE). The right
column of [`PLAN.md`](PLAN.md) names the bootcamp lab each phase
becomes — current Robo-Greeno participants are expected to lead these
as TAs in the next bootcamp.

## Coordination with sister tracks

- **Embedded** (mentor: Pavan): shared hexapod URDF and servo
  conventions so simulation and firmware target the same robot.
- **Cloud** (mentor: Kayvan): Wk-10 hand-off format — telemetry schema
  and relative-pose data for collaborative mapping.
- **Data B** (mentor: Scot): aligned timestamp and body-frame
  conventions on relative-pose output so vision-based mapping fuses
  cleanly with camera frames.

## Citing this work

If you use this repository in research or teaching, please cite it.
GitHub's **"Cite this repository"** button (top right of the repo page,
powered by [`CITATION.cff`](CITATION.cff)) gives APA and BibTeX. Or:

```bibtex
@software{robo_greeno_data_a_2026,
  author  = {Koh, Ingyu and {KamaTech Robo-Greeno Data A Team}},
  title   = {Robo-Greeno Data A: Hexapod Kinematics, Gait Generation,
             and RL Locomotion for Agricultural Spider Robots},
  year    = {2026},
  url     = {https://github.com/KamaTechOrg/robo-greeno-data-a},
  license = {MIT},
  version = {0.1.0}
}
```

A version-pinned DOI via Zenodo is planned for the first tagged release.

## Physical AI tutorial

An intuitive 4-chapter tutorial — *LLM AI vs Physical AI*, *Legs and
fingers in nature*, *MuJoCo without tears*, and *RL, intuitively* —
lives in [`docs/tutorial/`](docs/tutorial/) and is published at
<https://kamatechorg.github.io/robo-greeno-data-a/>.

## License

MIT. See [`LICENSE`](LICENSE).
