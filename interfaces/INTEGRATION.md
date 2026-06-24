# Data A — cross-team integration contract

How **Data A (hexapod locomotion)** connects to the other Robo-Greeno tracks.
This is Data A's side of the contract — a concrete proposal to align on, not a
unilateral decision. It is built from what each team's repo actually does today
(investigated 2026-06-22).

- **Embedded** — `KamaTechOrg/robogreeno-emb`
- **Data B** — `KamaTechOrg/robo-greeno-data-b`
- **Cloud** — `KamaTechOrg/robogreeno-cloud`
- **Canonical platform** — `KamaTechOrg/AgCloud`, `KamaTechOrg/AgStream`

## 0. Shared conventions (proposed, aligned to AgCloud)

The robot pipeline ultimately publishes to AgCloud, so Data A adopts AgCloud's
canonical conventions rather than inventing new ones:

| Concern | Convention | Why |
|---|---|---|
| **Timestamp** | epoch **milliseconds**, UTC (`stamp_ms`) | matches AgCloud `captured_ts` (ms). Data B and Cloud currently use float **seconds** — this is the one change we ask of them. |
| **Body frame** | **+X forward, +Y left, +Z up** (right-handed) | matches `config.py` and REP-103; unambiguous for IMU + pose. |
| **Units** | metres, radians, m/s, rad/s | SI throughout. |
| **Orientation** | unit quaternion `[w, x, y, z]` | no Euler ambiguity. |
| **Geo (Cloud/AgCloud)** | WGS84 lat/lon when a global fix exists | AgCloud `telemetry.lat/lon`. Indoors we use `odom` + `node_id` instead. |
| **robot_id** | stable string e.g. `spider-01` | same id everywhere (MQTT topics, messages). |

The canonical message is **[`pose_stamped.schema.json`](pose_stamped.schema.json)**
(see [`pose_stamped.example.json`](pose_stamped.example.json)).

## 1. Data A ↔ Embedded — robot model & joint commands

**What Data A provides:** [`hexapod.urdf`](hexapod.urdf) (generated from
`config.py`) + [`servo_conventions.md`](servo_conventions.md): the 18-channel
servo map, joint ranges, command format (18 absolute joint targets in rad at
50 Hz), and a PWM calibration template.

**What Embedded provides back:** servo feedback availability (open vs closed
loop), confirmation the controller wiring follows channel order 0…17, and the
filled PWM calibration table.

**Status (June 2026):** the org repo `robogreeno-emb` is still empty, but the
Embedded track is active in students' personal repos (mentor Dosithee Miet),
working through a session curriculum — now at **PCA9685 servo control by angle**
(e.g. `r83575/robo-greeno-embedded/session-14-pca9685-servo-control`). This pins
down the hardware: **PCA9685, 16-ch I²C, open-loop, 50 Hz**, and since 18 > 16
they need **two boards** (0x40 + 0x41). See
[`servo_conventions.md`](servo_conventions.md) for the two-board channel map and
incremental single-leg → hexapod bring-up. Open ask: consolidate the driver into
`robogreeno-emb` so Data A targets one canonical place.

## 2. Data A ↔ Data B — pose for spatial tagging of detections

Data B runs on-bot detection and publishes to MQTT topic
`MQTT/vision/detections` (JSON: `frame_id`, `timestamp`, `image_quality`,
`detection.results[…]` with pixel `bbox`). Their plan explicitly needs **robot
pose + IMU per frame** to spatially tag detections (Sprint 4 / SLAM). Their
**Issue #11 "Data A Integration Questions" was closed as completed (2026-06-22)**
once Data A's answers landed; the pose *delivery* refinement below (pull vs 50 Hz
stream) was raised separately after that, in the cross-team thread.

**Who owns pose (settles the (a)-vs-(c) question):** Embedded owns the **raw
sensors** (camera frames, IMU); **Data A owns pose** — it fuses IMU + leg
kinematics into the `odom` `pose_stamped` and is the one process that holds the
*latest* pose. So Embedded does **not** inherently have pose: it has sensor data
it sends to Data A. That makes **(c) the default** (Data B pulls pose from Data A
directly); **(a) only applies if Data A's estimator is co-located in Embedded's
process** (then the grabber can call `get_latest_pose()` locally). Either way we
do **not** route pose Data A → Embedded → Data B just to hand it over.

**Contract:**

1. **Time base.** Camera frames and `pose_stamped` share one clock, in
   `stamp_ms` (epoch ms, UTC). On a single Pi this is the system clock; if IMU
   runs on the ESP32, Embedded disciplines it to the Pi clock. (Data B converts
   its current float-seconds `timestamp` → ms.) This shared clock is what lets
   Data B bind a Data-A pose to an Embedded frame even though they come from two
   processes.
2. **Pose delivery — three options, recommend (a), else (c):** Data B pulls
   frames on demand (CPU-only) and does **not** want to run a 50 Hz subscriber
   for poses it will mostly discard. Both pull-based options below honour that —
   pose is fetched only for the frames Data B actually processes.
   - **(a) Embedded stamps at capture (preferred):** the frame grabber attaches
     the latest `pose` + `stamp_ms` to each frame before handing it to Data B.
     No clock-skew, no lookup, no extra IPC. Data B copies the block into its
     detection JSON. *Requires Embedded to have pose in-process* — true if Data A
     locomotion is co-located with the grabber (import `get_latest_pose()`).
   - **(c) Synchronous "freshest pose now" from Data A (pull):** if Embedded does
     **not** carry pose, Data B requests the freshest pose from Data A at capture
     time — in-process `get_latest_pose()` when co-located, or MQTT request/reply
     (Data A serves with `pose_publisher.py --serve`; Data B calls
     `request_latest_pose()` / `--get`: publish `<topic>/get` → reply on a
     per-frame `reply_topic`). Data A's 50 Hz control
     loop already holds the current pose, so this is just a different door on the
     same state — **pub/sub is not the only access pattern.** Returns a pure
     `pose_stamped`; Data B rejects the pair if `|frame_stamp_ms − stamp_ms|` >
     its skew budget (e.g. 50 ms), so the pose is bound to **capture**, not to
     inference time.
   - **(b) Pose stream + nearest-time lookup (fallback):** Data A publishes
     `pose_stamped` at ~50 Hz on `robogreeno/data-a/<robot_id>/pose`; Data B
     samples the pose whose `stamp_ms` is closest to the frame's `stamp_ms`
     (reject if Δt > 50 ms). The 50 Hz publisher stays up for Cloud odometry and
     replay-based dev, but Data B need not subscribe.
3. **What Data B adds to each detection message** (additive, non-breaking):
   ```json
   "robot_id": "spider-01",
   "pose": { "...": "the pose_stamped 'pose' block" },
   "pose_stamp_ms": 1781000130123
   ```
   Detections stay in pixel coords; 3D back-projection (camera intrinsics +
   extrinsics) is deferred jointly — Data B owns intrinsics, Data A owns the
   camera→body extrinsic once the mount is fixed.

**Answers to Data B Issue #11** (frame rate 50 Hz, same time domain yes,
pose = position+quaternion in `odom`, formalize at Sprint 1) are posted to that
issue.

## 3. Data A ↔ Cloud — odometry for collaborative mapping

Cloud is a DTN/swarm relay: carriers publish `TelemetryMessage`
(`spider_id`, `battery`, `storage_ratio`, `node_id`, float-seconds `timestamp`)
to `robogreeno/carrier/<id>/telemetry`. Position today is a greenhouse-graph
`node_id`, not continuous pose; no mapping/fusion exists yet. The Wk-10 hand-off
is Data A → Cloud relative-pose for collaborative mapping.

**Contract:**

1. Data A emits a **slim odometry variant** of `pose_stamped` sized for BLE/DTN
   (well under the 512 B budget) — drop `imu`, `covariance6`, `joint_angles_rad`:
   ```json
   {"schema":"robo-greeno/data-a/pose_stamped","version":1,"robot_id":"spider-01",
    "stamp_ms":1781000130123,"frame":"body","odom_frame":"odom",
    "pose":{"position_m":[3.142,-0.871,0.075],"orientation_quat":[0.995,0,0,0.098]},
    "node_id":"n12"}
   ```
2. **Routing:** carried as a new field/record alongside `TelemetryMessage`
   (same topic family), or a new `pose` message type — Cloud's call. `node_id`
   bridges Data A's continuous `odom` pose to Cloud's graph model so Cloud can
   fuse without immediately running SLAM.
3. **Fusion ownership:** Data A provides per-robot **odometry** (drifts over
   time, relative to power-on). Cloud owns multi-robot fusion / loop closure.
   Data A does not claim a global frame indoors.

**Cloud's blocker first:** Cloud Issue #14 (message serialization) must land
before this flows end-to-end; the schema above is ready to slot in.

## 4. What this resolves

- A **single timestamp + frame convention** across four repos that currently
  disagree (float-s vs ms; no agreed body frame).
- Embedded's Week-1 unblock (URDF + servo map exist now).
- A concrete answer to Data B's open Issue #11 and a pose block they can paste in.
- A DTN-sized odometry message Cloud can ingest once their serialization lands.

## 5. Open questions (tracked per team)

| # | Team | Question | Owner |
|---|------|----------|-------|
| 1 | Embedded | ~~Controller / loop type~~ → resolved: **PCA9685 ×2, open-loop, 50 Hz**. Remaining: consolidate driver into `robogreeno-emb`; fill PWM calibration | Dosithee / Pavan |
| 2 | Data B / Embedded | ~~50 Hz subscribe vs pull~~ → resolved: **pull, not stream** — option (a) if Embedded carries pose, else (c) synchronous freshest-pose from Data A. Open: does Embedded have pose in-process? + Data B adopts `stamp_ms` (ms) | Naama / Scot / Pavan |
| 3 | Data B | Who owns camera→body extrinsic calibration, and when? | Data A + Data B |
| 4 | Cloud | Extend `TelemetryMessage` or add a `pose` message type? | Kayvan |
| 5 | All | One `robot_id` scheme across all repos/topics | all mentors |

*Generated from repo investigation on 2026-06-22. Regenerate the URDF with
`python interfaces/gen_urdf.py` after any `config.py` change.*
