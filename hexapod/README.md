# hexapod/ — sim ↔ real integration

One consolidated package that runs the Robo-Greeno hexapod in **MuJoCo** or on
**real hardware** (PCA9685 servos + CSI camera) behind a single 18-channel
interface. This is the package sketched in
[`interfaces/MujocoRpiPca9685.pdf`](../interfaces/MujocoRpiPca9685.pdf) (page 2),
grounded in [`interfaces/servo_conventions.md`](../interfaces/servo_conventions.md).

```
hexapod/
├── robot_config.py   # the ONE geometry file (leg map, ranges, stance)   ┐
├── kinematics.py     # foot xyz → joint angles (IK/FK, 18-channel solve)  │ Data A
├── gait.py           # stand / tripod / wave foot trajectories            │
├── sim_mujoco.py     # MuJoCo backend (physics)                           ┘
├── real_pca9685.py   # PCA9685 servo backend (I²C)             → Embedded
├── camera.py         # CSI camera + pose-tagged frames         → Data B
└── main.py           # choose sim or real
```

## The one interface

Both backends expose the same two calls, so the gait and kinematics never know
which one they drive:

```python
backend.set_joint_targets(targets_rad)   # 18 rad, channel order (leg*3 + joint)
backend.step()                           # sim: advance physics; real: pace 50 Hz
```

`kinematics.solve_channels(foot_targets)` produces exactly the
`joint_targets_rad[18]` of the Embedded contract, so a trained RL policy or a
gait maps onto servo channels with no reindexing.

## Run it

```bash
python hexapod/main.py --check                             # headless self-test (no hardware)
python hexapod/main.py --backend sim  --gait wave --seconds 6
python hexapod/main.py --backend sim  --gait tripod --camera
python hexapod/main.py --backend real --gait stand --channels 3   # dry-run off-Pi, 1-leg bring-up
python hexapod/real_pca9685.py                             # print the servo channel table
```

`--check` verifies: the sim walks with the wave gait, all three gaits are IK-
reachable, the real backend converts the stance to servo degrees in dry-run, and
the camera returns a pose-tagged frame. No Pi and no MuJoCo viewer required.

## Backends

- **`sim_mujoco.MujocoBackend`** — builds the robot in MuJoCo straight from
  `robot_config.py` (no hand-edited XML) and exposes the trunk pose so the camera
  can tag frames.
- **`real_pca9685.Pca9685Backend`** — drives 18 servos over two PCA9685 boards
  (`0x40` + `0x41`) via `adafruit_servokit`. `channel = leg*3 + joint`,
  `board = channel // 16`, `pin = channel % 16`. Radians → servo degrees per a
  per-channel calibration table (Embedded fills real numbers on the bench).
  **Off a Pi it runs dry** — same math, prints the channel table, drives nothing.
  `--channels` supports the incremental 3 → 15 → 18 servo bring-up.

  > ⚠️ A standard **MG996R travels ~180°**, but `config.py` asks for femur 210°
  > and tibia 190°. The backend flags every out-of-range channel (12 of them) —
  > use 270° servos, gear them, or clamp the ranges before hardware bring-up.

- **`camera.CsiCamera`** — ArduCam-class CSI camera on the Pi 5 via `picamera2`.
  `capture_tagged(pose_provider)` attaches the freshest `pose` + `stamp_ms` to
  each frame — the Data B "stamp at capture" contract
  ([`INTEGRATION.md` §2](../interfaces/INTEGRATION.md), option (a)). Off a Pi it
  returns a synthetic frame so the tagging path is testable anywhere.

## Ownership boundaries

| Module | Owner | Note |
|---|---|---|
| `robot_config`, `kinematics`, `gait`, `sim_mujoco`, `main` | **Data A** | radians only |
| `real_pca9685` | **Embedded** | radians → PWM; open-loop, 50 Hz |
| `camera` | **Data B** | pixels + pose-tagging |

Data A works purely in radians; PWM lives only in `real_pca9685.py`, keyed by the
calibration table in [`servo_conventions.md`](../interfaces/servo_conventions.md).
