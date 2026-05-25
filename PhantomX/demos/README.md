# Robo-Greeno hexapod — demo samples

Two small, self-contained demos built on the MuJoCo + PhantomX runner.
Each is a folder a student can run, record, and push to GitHub as
their kinematics demo. Both reuse the same `config.py`,
`hexapod_ik.py`, and `hexapod_model.py` as the runner.

| demo                 | what the robot does                          |
|----------------------|-----------------------------------------------|
| `pose-wave/`         | stands, crouches, rises tall, waves a leg     |
| `tripod-walk/`       | walks forward with an alternating tripod gait |

Each folder has its own README. Run the demo's `--check` first — it
must print `ALL CHECKS PASSED` before the demo is ready to show.

These are templates. The shared files are fixed; the demo script
(`demo_pose_wave.py`, `demo_tripod_walk.py`) is the part each student
edits and makes their own.
