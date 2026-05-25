# Robo-Greeno — two kinematics problems for two students

This is the assignment that follows the demo samples. The two demos in
this folder — [`pose-wave/`](../demos/pose-wave/) and
[`tripod-walk/`](../demos/tripod-walk/) — are worked examples: they
already run. They are **not** the assignment. They are the starting
point each student copies, reads, and then changes into something new
that is theirs.

Each problem below is sized for one student. They are matched in
difficulty, so it does not matter which student takes which. Both end
in a runnable demo the student can record and show at the checkpoint.

## Assignments

| Problem | Builds on | Assigned to |
|---|---|---|
| [Problem A — Body-pose control](./problem-a-body-pose.md) | `demos/pose-wave/` | **Hadas Sigaron** ([`HadasSigaron/`](../../HadasSigaron/)) |
| [Problem B — Turn in place](./problem-b-turn-in-place.md) | `demos/tripod-walk/` | **Shira Marzel** ([`ShiraMarzel/`](../../ShiraMarzel/)) |

## Why these two problems

A few things make a good first assignment here, and both of these have
all of them:

- **Scoped.** Each problem is really one new function. The student is
  not staring at a blank file — the demo around it already works.
- **Built on something they have seen run.** The task is "change this
  one thing", not "start from nothing". That is the difference between
  a student who feels stuck and one who feels in control.
- **Genuine ownership.** The core idea in each — a rotation applied in
  the right place — is written by the student, not handed to them. That
  is exactly the "students should feel they are creating the robot" goal.
- **Visible and recordable.** Each ends in a demo you can watch and film.
  A checkpoint with something moving on screen is worth ten status updates.
- **Verifiable.** Each has a clear `--check` the student can run to know
  they are done — no guessing, no waiting for a mentor to grade it.

Together they also cover the two halves of how the robot moves:
**posing** (controlling the body) and **locomotion** (gaits). Problem A
is the next step past the pose demo; Problem B is the next step past
the walk demo. Both reduce, underneath, to the same skill: apply a 2-D
rotation in the correct reference frame. That is why they are peers.

## Notes for the mentor

- Assign both at the same checkpoint. They are matched in difficulty,
  so the two students can help each other without one being far ahead.
- A short daily check-in is enough. When a student is stuck, the
  unblock is almost always the same: print the foot targets and pass
  them through `solve_all` to see which leg fails and why.
- Encourage them to hit the reach limit on purpose and write down the
  number (the largest tilt, the largest turn angle). Finding a limit
  is real engineering — it is a result, not a failure.
- Where this leads: body-pose control and turning are exactly what the
  Stage B gait work and the later uneven-terrain work are built on. A
  student who finishes one of these has built a real piece of the
  robot.
