# Contributing — Robo-Greeno Data A

This repository is part of the **KamaTech OSS On-the-Job Training**
program. Contributions are expected primarily from program
participants and TAs, but issues, discussion, and pull requests from
the wider open-source community are welcome.

## How participants work in this repo

This repository follows the **standard open-source fork and pull
request workflow**. Learning this workflow is part of the OJT
curriculum — TAs in the upcoming bootcamp will teach the same flow.

### One-time setup (per participant)

1. Open https://github.com/KamaTechOrg/robo-greeno-data-a in your
   browser and click **Fork** (top right). This creates a copy of
   the repo under your own GitHub account.
2. Clone your fork to your laptop:

   ```
   git clone https://github.com/<your-username>/robo-greeno-data-a.git
   cd robo-greeno-data-a
   ```

3. Add the upstream remote so you can pull mentor-reviewed changes:

   ```
   git remote add upstream https://github.com/KamaTechOrg/robo-greeno-data-a.git
   ```

### Each piece of work

1. Sync with upstream first:

   ```
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. Create a feature branch named `wkN/<short-topic>` (for example
   `wk2/forward-kinematics`):

   ```
   git checkout -b wk2/forward-kinematics
   ```

3. Do the work, commit in small steps with clear messages.
4. Push the branch to your fork:

   ```
   git push origin wk2/forward-kinematics
   ```

5. Open a pull request from your fork's branch to
   `KamaTechOrg/robo-greeno-data-a:main`. GitHub will offer a
   "Compare & pull request" button after the push.
6. Address review comments by pushing more commits to the same
   branch — the PR updates automatically.
7. Once approved, the mentor merges. You can then delete the branch.

Each weekly phase in [`PLAN.md`](../project/PLAN.md) corresponds to a folder
that gets added when the phase begins. Each phase ends with a
tagged release (`wk2-ik`, `wk5-imu`, ...) so the bootcamp lab
corresponding to that phase has a stable reference point.

## Issue conventions

Use issue labels:

- `phase/wkN` — which week the issue belongs to
- `track/data-a` — vs cross-track issues
- `bootcamp` — when the work also feeds the future bootcamp lab
- `cross-team` — touches Embedded, Cloud, or Data B

## Cross-team coordination

For changes that touch shared interfaces (URDF, telemetry schema,
relative-pose conventions), open an issue with the `cross-team` label
and tag the relevant mentor before merging. See [`README.md`](README.md)
for the current mentor list.

## License

All contributions are accepted under the MIT license — see
[`LICENSE`](LICENSE).
