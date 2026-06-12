# Plan — Citable Repo + "Physical AI" Tutorial Site

Goal: make `robo-greeno-data-a` (1) citable like a paper, and (2) the home
of an intuitive, search-friendly **Physical AI tutorial** that turns the
hexapod project into teaching material anyone can find on Google.

## Part 1 — Citability

| Step | What | Why |
|------|------|-----|
| 1.1 | Add `CITATION.cff` at repo root | GitHub shows a "Cite this repository" button (APA + BibTeX) automatically |
| 1.2 | Add a "Citing this work" section to README with ready-made BibTeX | Copy-paste citation for students and bloggers |
| 1.3 | Link the repo to [Zenodo](https://zenodo.org) and cut a GitHub Release (e.g. `v0.1.0`) | Zenodo archives the release and mints a **DOI** — the gold standard for citability |
| 1.4 | Paste the DOI badge back into README and CITATION.cff | Permanent, version-pinned reference |

Only 1.3 needs a manual step (log in to Zenodo with GitHub, flip the
repo switch, publish a release). Everything else is files in this repo.

## Part 2 — Tutorial content (4 chapters)

Written for a smart beginner; every concept gets a physical metaphor
before any math. Hosted on GitHub Pages, source in `docs/tutorial/`.

1. **LLM AI vs Physical AI** — why a model that writes poetry can't
   keep a robot from falling over. Moravec's paradox; tokens vs
   torques; simulation as the robot's training data.
2. **Legs and fingers: nature's engineering** — 6 legs (insects,
   tripod gait), 8 legs (spiders, hydraulics), 2 legs (humans,
   controlled falling), 10 fingers (manipulation). Why a hexapod:
   static stability = beginner-friendly.
3. **MuJoCo without tears** — physics engine as "Newton's laws in a
   for-loop"; bodies/joints/actuators; timesteps; contact forces.
4. **Reinforcement learning, intuitively** — training a puppy with
   treats; states/actions/rewards; reward design; PPO; sim-to-real
   and domain randomization.

Each chapter ends with: a runnable Colab link, a "key takeaways" box,
and an FAQ (doubles as SEO structured data).

## Part 3 — Site mechanics (GitHub Pages)

- **Generator:** MkDocs + Material theme (`mkdocs.yml` in repo root).
- **Deploy:** GitHub Actions workflow (`.github/workflows/docs.yml`)
  publishes `docs/` to Pages on every push to `main`.
- **URL:** `https://kamatechorg.github.io/robo-greeno-data-a/`
- Enable in repo **Settings → Pages → Source: GitHub Actions**.

## Part 4 — SEO strategy

- Each page: one H1, descriptive `description:` front-matter, question
  headings that match real queries ("What is Physical AI?", "Why do
  robots have six legs?", "Is MuJoCo hard to learn?").
- FAQ sections → Google rich results; Material emits clean HTML +
  sitemap.xml automatically.
- Internal links between chapters; external links to MuJoCo, SB3,
  Gymnasium docs (authority signals).
- Target keywords: *physical AI tutorial, physical AI vs LLM, hexapod
  robot simulation, MuJoCo tutorial for beginners, reinforcement
  learning robot walking, tripod gait*.
