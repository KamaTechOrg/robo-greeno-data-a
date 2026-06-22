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

## PWM calibration (per servo, filled on real hardware)

Cheap servos (MG90S) vary ±5%, so each channel needs a calibration row mapping
**radians → PWM microseconds**. Template (Embedded fills `min_us`/`max_us` after
calibrating each servo; `reverse` flips direction for back-to-front mounting):

```json
{
  "0":  {"min_us": 1000, "max_us": 2000, "at_rad": [-0.873, 0.873], "reverse": false, "trim_us": 0},
  "1":  {"min_us": 1000, "max_us": 2000, "at_rad": [-1.571, 2.094], "reverse": false, "trim_us": 0}
}
```

Conversion: `us = lerp(min_us, max_us, (angle - at_rad[0]) / (at_rad[1] - at_rad[0]))`,
then apply `reverse` and `trim_us`. Data A works purely in radians; **PWM lives
only on the Embedded side**, keyed by this table.

## Open items to confirm with Embedded (Pavan / Dosithee)

1. Controller board: Servo 2040 (RP2040, 18-ch) vs PCA9685 — channel numbering
   matches 0…17 either way; confirm wiring order follows this table.
2. Feedback: do servos report position back to Data A, or is control open-loop?
   (Affects whether `pose_stamped.joint_angles_rad` is measured or commanded.)
3. Note: `RL/hexapod_env.py`'s inline sim currently uses tighter joint ranges
   (−45/45, −60/60, −90/30). **`config.py` ranges above are canonical**; the RL
   sim should be widened to match before hardware bring-up.
