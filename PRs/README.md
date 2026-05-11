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

## <img src="https://github.com/ingyukoh.png?size=32" width="24" align="center"> [PR #3264 — \[MJX\] Use scan-based loop in solver to enable reverse-mode autodiff](https://github.com/google-deepmind/mujoco/pull/3264)

![Status: Open](https://img.shields.io/badge/status-Open-1a7f37?style=flat-square) ![Diff: +42 / -1](https://img.shields.io/badge/diff-%2B42%20%2F%20--1-blue?style=flat-square) ![Files: 2](https://img.shields.io/badge/files-2-lightgrey?style=flat-square)

**Fixes:** [#2259](https://github.com/google-deepmind/mujoco/issues/2259) · **Status:** Awaiting review

### What this PR does

Switches the outer constraint solver loop in `mjx/mujoco/mjx/_src/solver.py` from `jax.lax.while_loop` to the existing `_while_loop_scan` helper (already used for the linesearch loop in the same file). This unblocks `jax.grad` through `mjx.solve` for any user running with `m.opt.iterations > 1` — previously only `iterations = 1` worked, which the issue author flagged as physically inaccurate.

| | |
|---|---|
| **Forward semantics** | Identical to `jax.lax.while_loop` |
| **Reverse-mode AD** | Now works (was `ValueError` before) |
| **Existing solver tests** | 13 / 13 pass |
| **New regression test** | `test_solver_reverse_mode_grad` added |

### Why this fix shape was chosen

The `_while_loop_scan` helper was **already in the codebase** at lines 239–253 of `solver.py`, used by the linesearch loop. Its docstring literally reads *"Scan-based implementation (jit ok, reverse-mode autodiff ok)"*. The fix is one functional line: apply the same helper to the outer solver loop.

### Takeaway for students

> **Lesson:** Before writing a new abstraction, search the codebase for *"the team already solved this somewhere else"*. The smallest possible diff that compiles is almost always the right diff. Reusing trusted helpers is friendlier to reviewers than introducing new ones.

**[→ Open PR #3264 on GitHub](https://github.com/google-deepmind/mujoco/pull/3264)**

---

## Summary

| Metric | Count |
|---|---|
| Total PRs to `google-deepmind/mujoco` | **2** |
| Open (awaiting review) | 🟢 **1** |
| Closed without merge | 🔴 **1** |
| Tests added | 3 |
| Maintainer engagements received | 1 ([@Balint-H](https://github.com/Balint-H)) |

---

## Lessons distilled

1. **A technically-correct PR can still be declined.** Scope and project philosophy matter as much as code quality. (PR #3266)
2. **Validate the approach *before* writing code.** One issue-comment round-trip prevents the most common rejection mode.
3. **Reuse existing helpers.** The smallest diff that compiles is usually the right one. (PR #3264)
4. **Read the maintainer's reasoning carefully.** A closed PR with a thoughtful comment is more valuable feedback than a silent merge — it teaches you the project's culture.

---

<sub>Portfolio page for KamaTechOrg learning track · Repo: [google-deepmind/mujoco](https://github.com/google-deepmind/mujoco)</sub>
