# References — Robo-Greeno Data A

Starter reading. Curated to fit student laptops + free GPU credits, no
paid sim or expensive lab hardware required.

## Hexapod kinematics and gait

- **SpiderBotTutorials** — proposed shared URDF and servo conventions
  with the Embedded track.
- **OpenPode / PhantomX hexapod URDFs** — reference URDFs.
- Buss, S. R. (2009). *Introduction to Inverse Kinematics with
  Jacobian Transpose, Pseudoinverse and Damped Least Squares.*

## Reinforcement learning for legged locomotion

- Rudin, N. et al. (2021). *Learning to Walk in Minutes Using
  Massively Parallel Deep RL* — paired with `legged_gym`.
- Lee, J. et al. (2020). *Learning quadrupedal locomotion over
  challenging terrain.* Science Robotics.
- Hwangbo, J. et al. (2019). *Learning agile and dynamic motor skills
  for legged robots* (ANYmal sim-to-real). Science Robotics.

## Simulation

- [MuJoCo](https://github.com/google-deepmind/mujoco) — Google
  DeepMind, open source. Default sim.
- [MuJoCo MJX](https://github.com/google-deepmind/mujoco/tree/main/mjx)
  — JAX rewrite for parallel sim on GPU / TPU. For Wk 6-8.
- [MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie)
  — curated robot models.
- [Gymnasium](https://github.com/Farama-Foundation/Gymnasium)
- [Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3)
- [SBX](https://github.com/araffin/sbx) — SB3 in JAX (faster, same API).

## IMU stabilization

- Madgwick, S. (2010). *An efficient orientation filter for inertial
  and inertial/magnetic sensor arrays.*
- Mahony, R. et al. (2008). *Nonlinear complementary filters on the
  special orthogonal group.*
- [ROS robot_localization](https://github.com/cra-ros-pkg/robot_localization)
  — EKF / UKF reference design.

## Neighbor relative localization (BLE-only)

- BLE RSSI ranging surveys.
- Angle-of-arrival on Nordic nRF radios.
- Acoustic time-of-flight using on-board microphone (in the spec
  sensor list).
- Roumeliotis, S. I. and Bekey, G. A. (2002). *Distributed multirobot
  localization.*

## Special tasks (picking, pollination)

- Octinion **Rubion** strawberry-picking robot.
- Harvest **CROO** Robotics.
- Sim-to-real dexterous manipulation surveys.

## Embedded targets

- ESP32 + FreeRTOS — see `agrinode-edge` repo for the
  ESP32-CAM scaffold from the gap-week prep.
- [Wokwi](https://wokwi.com) — browser-based ESP32 simulator for
  zero-install student onboarding.
