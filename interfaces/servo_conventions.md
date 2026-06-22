# Servo & joint conventions — Data A ↔ Embedded

This is Data A's proposed contract for the Embedded team (`robogreeno-emb`) so
that **simulation and firmware target the exact same robot**. All numbers are
derived from the single source-of-truth geometry in
[`ShiriStern/wave-walk/config.py`](../ShiriStern/wave-walk/config.py) and the
generated [`hexapod.urdf`](hexapod.urdf).

> Frame: **+X forward, +Y left, +Z up** (right-handed). Units: **metres, radians**.

## Channel map (18 servos)

`channel = leg_index * 3 + joint_index`, where leg order is the order in
`config.LEGS` and joint order is `coxa, femur, tibia`.

| Ch | Leg | Joint | Axis | Range (deg) | Range (rad) |
|----|-----|-------|------|-------------|-------------|
| 0  | front_left  | coxa  | +Z (yaw)  | −50 … +50   | −0.873 … +0.873 |
| 1  | front_left  | femur | +Y (lift) | −90 … +120  | −1.571 … +2.094 |
| 2  | front_left  | tibia | +Y (lift) | −170 … +20  | −2.967 … +0.349 |
| 3  | mid_left    | coxa  | +Z | −50 … +50  | −0.873 … +0.873 |
| 4  | mid_left    | femur | +Y | −90 … +120 | −1.571 … +2.094 |
| 5  | mid_left    | tibia | +Y | −170 … +20 | −2.967 … +0.349 |
| 6  | back_left   | coxa  | +Z | −50 … +50  | −0.873 … +0.873 |
| 7  | back_left   | femur | +Y | −90 … +120 | −1.571 … +2.094 |
| 8  | back_left   | tibia | +Y | −170 … +20 | −2.967 … +0.349 |
| 9  | back_right  | coxa  | +Z | −50 … +50  | −0.873 … +0.873 |
| 10 | back_right  | femur | +Y | −90 … +120 | −1.571 … +2.094 |
| 11 | back_right  | tibia | +Y | −170 … +20 | −2.967 … +0.349 |
| 12 | mid_right   | coxa  | +Z | −50 … +50  | −0.873 … +0.873 |
| 13 | mid_right   | femur | +Y | −90 … +120 | −1.571 … +2.094 |
| 14 | mid_right   | tibia | +Y | −170 … +20 | −2.967 … +0.349 |
| 15 | front_right | coxa  | +Z | −50 … +50  | −0.873 … +0.873 |
| 16 | front_right | femur | +Y | −90 … +120 | −1.571 … +2.094 |
| 17 | front_right | tibia | +Y | −170 … +20 | −2.967 … +0.349 |

Leg **mount angles** (body XY-plane, 0 = forward, +CCW): FL +45°, ML +90°,
BL +135°, BR −135°, MR −90°, FR −45°. Link lengths: coxa 0.040 m, femur
0.080 m, tibia 0.130 m.

This 0…17 order is **identical** to the 18-dim RL action/observation vector in
[`RL/hexapod_env.py`](../RL/hexapod_env.py), so a trained policy maps to servo
channels with no reindexing.

## Command interface (Data A → Embedded)

Data A emits **18 absolute joint targets in radians**, channel-ordered as above.

```json
{
  "schema": "robo-greeno/data-a/joint_command",
  "robot_id": "spider-01",
  "stamp_ms": 1781000130123,
  "mode": "position",
  "joint_targets_rad": [c0, c1, c2,  c3, c4, c5,  c6, c7, c8,
                        c9, c10, c11, c12, c13, c14, c15, c16, c17]
}
```

- **Rate:** target **50 Hz (20 ms)**; **20 Hz (50 ms)** acceptable fallback for
  power/CPU budget. (RL policy runs at 50 Hz.)
- **Rest / home pose** (servo zero reference): the standing stance in
  `config.py` (`STANCE_RADIUS`, `STANCE_HEIGHT`). Send this on startup before
  enabling a gait.
- **Safety:** Embedded clamps every target to the per-channel range above.

### RL-policy form (equivalent)
A policy outputs `action ∈ [−1, 1]^18`; the joint target is
`target = rest + 0.3 · action` (rad). Embedded can take either absolute targets
(above) or `{action, rest}` — absolute is preferred for hardware.

## Confirmed hardware — PCA9685 (Embedded sessions, June 2026)

Per the Embedded track (mentor Dosithee Miet; sessions in students' repos, e.g.
[r83575/robo-greeno-embedded `session-14-pca9685-servo-control`](https://github.com/r83575/robo-greeno-embedded/tree/main/session-14-pca9685-servo-control)),
the controller is the **PCA9685** — 16-channel, 12-bit PWM, driven from the
Raspberry Pi over **I²C**. Two consequences pin down the open questions:

1. **18 servos > 16 channels → two PCA9685 boards** on the same I²C bus at
   different addresses (`0x40`, `0x41`). Logical channel 0…17 maps to:
   `board = channel // 16`, `pin = channel % 16` — i.e. joints **0–15 → board0
   (0x40) pins 0–15**, joints **16–17 → board1 (0x41) pins 0–1**. (A single leg
   = 3 channels on board0, which matches the team's current single-leg stage.)
2. **Open-loop.** PCA9685 is PWM-out only and hobby servos give no position
   feedback → `pose_stamped.joint_angles_rad` is **commanded, not measured**.
   Q2 resolved: open-loop control.
3. **Rate fits for free.** PCA9685 servo refresh is set to **50 Hz**, so one PWM
   frame per command at our 50 Hz target — I²C fast-mode (400 kHz) updates both
   boards well within 20 ms.

Incremental bring-up path (matches the sessions): **1 leg (3 ch, board0)** →
**5 legs (15 ch, board0)** → **6 legs (18 ch, board0+board1)**.

**Real stack on the bench today** (Ruth's
[`session-14-pca9685-servo-control`](https://github.com/r83575/robo-greeno-embedded/tree/main/session-14-pca9685-servo-control)):
Raspberry Pi 3B + PCA9685 + **MG996R** servos, driven with the high-level
**`adafruit_servokit.ServoKit`** library — you command **degrees** and call
`set_pulse_width_range(500, 2500)`; the library handles µs→tick. So Data A's
radians map straight onto `kit.servo[ch].angle` (see bridge below). Only
**2 servos** are on hand so far → start with coxa+femur (channels 0,1), add
tibia when a third arrives.

> ⚠️ **Range check:** a standard MG996R travels ~**180°**, but `config.py` asks
> for **femur 210°** (−90…+120) and **tibia 190°** (−170…+20). Either use 270°
> servos, gear them, or clamp the usable joint range to ≤180° in `config.py`
> before hardware bring-up. Coxa (100°) is fine.

## PWM calibration (per servo, filled on real hardware)

With `adafruit_servokit`, calibration is just `set_pulse_width_range(min_us,
max_us)` per channel (the team uses **500–2500 µs** for MG996R) plus a per-joint
**home angle** and **direction sign** that tie the servo's 0–180° to the joint's
zero. Template (Embedded fills these after calibrating each servo; `reverse`
flips direction for back-to-front mounting):

```json
{
  "0":  {"min_us": 1000, "max_us": 2000, "at_rad": [-0.873, 0.873], "reverse": false, "trim_us": 0},
  "1":  {"min_us": 1000, "max_us": 2000, "at_rad": [-1.571, 2.094], "reverse": false, "trim_us": 0}
}
```

Conversion: `us = lerp(min_us, max_us, (angle - at_rad[0]) / (at_rad[1] - at_rad[0]))`,
then apply `reverse` and `trim_us`. Data A works purely in radians; **PWM lives
only on the Embedded side**, keyed by this table.

## Open items with Embedded (mentor Dosithee Miet / Pavan)

- ✅ **Controller:** PCA9685 (16-ch I²C) — *resolved*. Two boards for 18 servos
  (0x40 + 0x41), channel→`(board, pin)` map above.
- ✅ **Feedback:** open-loop — *resolved*. `joint_angles_rad` is commanded.
- ⬜ **Consolidation:** session work currently lives in students' personal repos
  (`r83575/robo-greeno-embedded`, `Yaffi4909/embedded-systems-mentoring`); the
  org repo `KamaTechOrg/robogreeno-emb` is still empty. Propose moving the
  PCA9685 driver into `robogreeno-emb` so Data A can target one canonical place.
- ⬜ **Per-servo calibration table** filled for the servos on hand (they have the
  `calibration_notes.txt` workflow started — align its format with the JSON above).
- ⬜ **Hardware count:** only a few servos on the bench so far → bring up one leg
  (3 ch) end-to-end first, then scale to 18.
- ⬜ **Sim parity:** `RL/hexapod_env.py` uses tighter joint ranges
  (−45/45, −60/60, −90/30) than canonical `config.py` (−50/50, −90/120,
  −170/20). **`config.py` wins**; widen the RL sim before hardware bring-up.
