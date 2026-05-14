# MuJoCo Open-Source Contributions

**Contributor:** [@ingyukoh](https://github.com/ingyukoh) · ![KamaTechOrg](https://img.shields.io/badge/KamaTechOrg-student-blue)

Contributions to [google-deepmind/mujoco](https://github.com/google-deepmind/mujoco). Each card below links straight to the PR on GitHub and includes the maintainer's feedback and the takeaway for KamaTechOrg students.

---

## <img src="https://github.com/ingyukoh.png?size=32" width="24" align="center"> [PR #3266 — Fix Unity passive flag compatibility](https://github.com/google-deepmind/mujoco/pull/3266)

![Status: Closed](https://img.shields.io/badge/status-Closed-cf222e?style=flat-square) ![Diff: +14 / -2](https://img.shields.io/badge/diff-%2B14%20%2F%20--2-blue?style=flat-square) ![Files: 2](https://img.shields.io/badge/files-2-lightgrey?style=flat-square)

**Fixes:** [#2972](https://github.com/google-deepmind/mujoco/issues/2972) · **Closed by:** [@Balint-H](https://github.com/Balint-H) (Collaborator)

### What this PR did

Preserved compatibility for legacy MJCF files containing `<flag passive="...">` by mapping `passive` to both `spring` and `damper` on import, and writing the modern schema (`spring` + `damper`, never `passive`) on export. Added regression coverage for both legacy parsing and generated XML.

| | |
|---|---|
| **Verification** | `git diff --check` clean |
| **Unity tests** | `MjGlobalSettingsGenerationTests` — 2 / 2 passed |
| **Unity tests** | `MjGlobalSettingsParsingTests` — 2 / 2 passed |
| **Unity version** | 6000.3.15f1 on macOS Apple Silicon |

### Maintainer feedback

> **[@Balint-H](https://github.com/Balint-H) commented:**
> Hello, thank you for contributing! However, the main part of this PR is already merged into main (update to spring and damper). Backwards compatibility is not without merit, however, MuJoCo itself treats the change as a breaking change too, so I don't see a good reason to semi-support the passive flag. Let me know if there is a use case I'm missing.

### Takeaway for students

The code was **technically correct** — clean diff, all tests green. The PR was declined on **scope and philosophy**: upstream MuJoCo deliberately treats `passive` as a breaking change, so adding a silent compatibility shim in the Unity plugin would mask the upstream signal.

> **Lesson:** Before writing a PR, post a short comment on the issue confirming the approach with a maintainer ("planning to do X — does this align?"). One round-trip avoids the wasted cycle.

**[→ Open PR #3266 on GitHub](https://github.com/google-deepmind/mujoco/pull/3266)**

---

## Summary

| Metric | Count |
|---|---|
| Total PRs to `google-deepmind/mujoco` | **1** |
| Closed without merge | 🔴 **1** |
| Tests added | 2 |
| Maintainer engagements received | 1 ([@Balint-H](https://github.com/Balint-H)) |

---

## Lessons distilled

1. **A technically-correct PR can still be declined.** Scope and project philosophy matter as much as code quality.
2. **Validate the approach *before* writing code.** Post a short comment on the issue ("planning to do X — does this align?") and wait for a maintainer thumbs-up. One round-trip prevents the most common rejection mode.
3. **Read the maintainer's reasoning carefully.** A closed PR with a thoughtful comment is more valuable feedback than a silent merge — it teaches you the project's culture.

---

<sub>Portfolio page for KamaTechOrg learning track · Repo: [google-deepmind/mujoco](https://github.com/google-deepmind/mujoco)</sub>
