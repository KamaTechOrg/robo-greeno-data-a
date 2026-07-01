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

## <img src="https://github.com/ingyukoh.png?size=32" width="24" align="center"> [PR #3264 — [MJX] Use scan-based loop in solver to enable reverse-mode autodiff](https://github.com/google-deepmind/mujoco/pull/3264)

![Status: Approved](https://img.shields.io/badge/status-Approved%20%C2%B7%20awaiting%20merge-2da44e?style=flat-square) ![Diff: +42 / -0](https://img.shields.io/badge/diff-%2B42%20%2F%20--0-blue?style=flat-square) ![Files: 4](https://img.shields.io/badge/files-4-lightgrey?style=flat-square)

**Closes:** [#2259](https://github.com/google-deepmind/mujoco/issues/2259) · **Reviewed by:** [@btaba](https://github.com/btaba) (Collaborator)

### What this PR did

Adds an opt-in `OptionJAX.solver_scan` flag that swaps the outer MJX solver loop from `jax.lax.while_loop` to a `jax.lax.scan`-based loop. With the flag enabled, `jax.grad` works through `mjx.solve` for `iterations > 1`. With it disabled (the default), behavior and performance are unchanged.

Without this fix, users wanting reverse-mode autodiff through the solver had to set `m.opt.iterations = 1` — the issue reporter notes that "leads to potentially inaccurate simulation and gradients."

| | |
|---|---|
| **Files** | `mjx/_src/{types,io,solver,solver_test}.py` |
| **Regression test** | `test_solver_reverse_mode_grad` — sphere-on-plane scene with `iterations=4`, asserts `jax.grad` returns finite values |
| **CI** | 22 / 22 checks green (Linux × GCC/Clang matrix, macOS arm64+x86_64, Windows, WASM, Studio) |
| **Backward compat** | Default `solver_scan=False` keeps existing `while_loop` path byte-identical |

### Maintainer feedback

> **[@btaba](https://github.com/btaba) commented (round 1):**
> Thanks for the contribution. I'd expect a perf diff with this change, have you verified? I'd prefer if this were hidden behind a flag in `OptionJAX`.
> — *CHANGES_REQUESTED*

After the flag was added (`OptionJAX.solver_scan`, default `False`) so the existing `while_loop` path is preserved unless users explicitly opt in:

> **[@btaba](https://github.com/btaba) commented (round 2):**
> Thanks! LGTM
> — *APPROVED*

### Takeaway for students

The same change took two trajectories depending on how the maintainer's concern was addressed. The first version swapped the loop unconditionally — that risked changing performance for every existing user. The second version moved the new behavior behind a default-off flag, which converts the question from *"should this land for everyone?"* to *"individual users can opt in when they want gradients."* Same code, different framing, fast merge.

> **Lesson:** When a maintainer asks for a flag, give them the flag. Default-off opt-in is the universal compromise for "useful change that might affect existing users." It removes the burden of having to predict every downstream impact before the PR can land.

**[→ Open PR #3264 on GitHub](https://github.com/google-deepmind/mujoco/pull/3264)**

---

## <img src="https://github.com/ingyukoh.png?size=32" width="24" align="center"> [PR #3268 — [Unity plugin] Surface a clear error when mesh asset is missing](https://github.com/google-deepmind/mujoco/pull/3268)

![Status: In review](https://img.shields.io/badge/status-In%20review-d29922?style=flat-square) ![Diff: +6 / -0](https://img.shields.io/badge/diff-%2B6%20%2F%20--0-blue?style=flat-square) ![Files: 1](https://img.shields.io/badge/files-1-lightgrey?style=flat-square)

**Related to:** [#1354](https://github.com/google-deepmind/mujoco/issues/1354) (closed) · **Reviewed by:** [@Balint-H](https://github.com/Balint-H) (Collaborator)

### What this PR did

When `Resources.Load<Mesh>(assetName)` returned `null` in `MjMeshShape.FromMjcf`, the failure was silent — `Mesh` was left null and downstream code (`BuildMesh`, `DebugDraw`) threw an opaque `NullReferenceException` far from the root cause. This patch throws a descriptive exception at the load site so the import aborts with a message that points at the actual problem.

### Context

The runtime fix BH proposed in #1354 (typed `Resources.Load<Mesh>(assetName)`) was already in `main`. This PR fills the **diagnostic gap** that the typed-load fix left behind: when the load returns null (mesh wasn't imported, or its import failed), the user now sees a clear error rather than a downstream NPE.

### Maintainer feedback

> **[@Balint-H](https://github.com/Balint-H) commented (round 1):**
> A reasonable tweak to make errors with imports from broken MJCFs more instructive. Could also be useful for the future when there are new mesh formats in main MJ that haven't been implemented in Unity yet. Please adjust the wording of the error message based on the feedback!

> *Inline comment:* I thought that non-mesh assets that share the name are no longer the issue. The failure is only when a mesh was not imported, or there was a failure in the import, no? If that's the case, the second half of the error message sentence is unhelpful/redundant.

After the wording was updated — dropped the type-collision clause that BH's own typed-load fix already handles, replaced with the unsupported-mesh-format scenario BH suggested:

> *Currently awaiting BH's re-review.*

### Takeaway for students

Two lessons fused into one small PR. First, **look adjacent to a maintainer's own merged fix** — when BH wrote the typed `Resources.Load<Mesh>` fix for #1354, he closed the *type-collision* failure mode but left a *diagnostic gap* (silent null returns producing crashes far from their cause). That window was real and unclaimed. Second, when a maintainer flags wording that's now wrong because of their own earlier fix, take their suggested replacement scenario **verbatim** — they're telling you exactly what they want to read.

> **Lesson:** Look adjacent to a maintainer's own merged fix for follow-on improvements that polish their work. The maintainer is already invested in that area and is primed to merge improvements that build on what they shipped.

**[→ Open PR #3268 on GitHub](https://github.com/google-deepmind/mujoco/pull/3268)**

---

## Summary

| Metric | Count |
|---|---|
| Total PRs to `google-deepmind/mujoco` | **3** |
| Approved / awaiting merge | 🟡 **1** |
| In review (wording revision pushed) | 🟠 **1** |
| Closed without merge | 🔴 **1** |
| Tests added | 3 |
| Maintainer engagements received | 2 ([@Balint-H](https://github.com/Balint-H), [@btaba](https://github.com/btaba)) |

---

## Lessons distilled

1. **A technically-correct PR can still be declined.** Scope and project philosophy matter as much as code quality.
2. **Validate the approach *before* writing code.** Post a short comment on the issue ("planning to do X — does this align?") and wait for a maintainer thumbs-up. One round-trip prevents the most common rejection mode.
3. **Read the maintainer's reasoning carefully.** A closed PR with a thoughtful comment is more valuable feedback than a silent merge — it teaches you the project's culture.
4. **When asked for a flag, give them the flag.** Default-off opt-in turns "should this land for everyone?" into "users can opt in later" — the cheapest possible compromise on contentious behavior changes.
5. **Look adjacent to merged fixes.** A maintainer's recent fix often closes the obvious failure mode but leaves a diagnostic or edge-case gap. That gap is the perfect target for a tiny follow-on PR — the maintainer is already engaged in the area and primed to merge polish that builds on their own work.

---

<sub>Portfolio page for KamaTechOrg learning track · Repo: [google-deepmind/mujoco](https://github.com/google-deepmind/mujoco)</sub>
