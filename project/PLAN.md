# Robo-Greeno Data A — 10-Week Plan

Each phase is sized to (a) ship a working artifact at the end of the
week and (b) become a single TA-led bootcamp lab.

| Wk    | Focus                                                                                  | Deliverable                                                | Bootcamp lab       |
|-------|----------------------------------------------------------------------------------------|------------------------------------------------------------|--------------------|
| 1     | Onboard. Pick sim stack. Import hexapod URDF. Sync HW constraints with Embedded track. | Local MuJoCo runs hexapod URDF; team conventions doc.      | -                  |
| 2-3   | Forward + inverse kinematics. Tripod / wave / ripple gaits in simulation.              | Open-loop walking in MuJoCo; gait comparison video.        | "IK lab"           |
| 4-5   | IMU fusion (Madgwick) + closed-loop stabilization on uneven terrain.                   | Stabilized walk over heightfield; IMU vs ground-truth log. | "IMU filter lab"   |
| 6-8   | RL: walk-to-point → approach plant → picking / pollination stub. Massively-parallel    | Trained policy + sim-to-real video; cost-of-transport      | "Sim-to-real RL    |
|       | training with domain randomization on MuJoCo MJX (free Colab GPU).                     | metric.                                                    | lab"               |
| 9     | Neighbor relative-position estimation (BLE RSSI + acoustic ToF). Multi-agent sim.      | Two-agent simulation with relative-pose RMSE plot.         | "Neighbor RSSI     |
|       |                                                                                        |                                                            | lab"               |
| 10    | Hand-off package to Cloud team for collaborative mapping. Demo + writeup.              | Telemetry schema doc + integrated demo video.              | Integrated demo    |

## Metrics tracked across phases

- **Cost-of-transport** (energy / distance) per gait
- **IMU pose RMSE** vs simulator ground truth
- **Task success rate** for walk-to-point and picking stub
- **Relative-pose RMSE** for neighbor localization

## Hardware budget

| Component               | Unit cost | Per-spider qty | Notes                                    |
|-------------------------|-----------|----------------|------------------------------------------|
| ESP32 dev board         | ~$4       | 1              | FreeRTOS, low-level motion + IMU + BLE   |
| Raspberry Pi 4/5        | ~$45-80   | 1 (carrier)    | On-device inference, BLE coordination    |
| Raspberry Pi Zero 2 W   | ~$15      | 1 (small)      | Lightweight Linux node alternative       |
| MPU-9250 / BNO055 IMU   | ~$5-15    | 1              | 6-axis or 9-axis                         |
| MG90S micro servo       | ~$3       | 18             | 3 DOF × 6 legs                           |
| LiPo 2S 1000mAh         | ~$10      | 1              | Power                                    |

A small spider BOM lands in the ~$80-110 range with conservative
sourcing. A carrier with a Pi 4 plus a USB camera lands ~$140-180.

## Cross-team checkpoints

- **End Wk 1:** URDF + servo conventions agreed with Embedded (Pavan).
- **End Wk 5:** IMU + body-frame convention shared with Data B (Scot).
- **End Wk 8:** Telemetry + relative-pose schema draft sent to Cloud
  (Kayvan).
- **End Wk 10:** Integrated demo with all four tracks.
