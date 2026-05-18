"""Gymnasium environment wrapping the Robo-Greeno (3+3) hexapod in MuJoCo.

Pairs with robo_greeno_3plus3_colab.ipynb. Designed for training a walking
policy with Stable Baselines3 (PPO or SAC). See accompanying README for
usage examples.

Conventions:
- Action: 18-dim, in [-1, 1]; scaled to ±0.3 rad joint-angle deltas around
  the rest pose, written to position actuators.
- Observation: 53-dim (chassis z, chassis quat, 18 joint angles, 6 chassis
  vels, 18 joint vels, 6 foot-contact flags).
- Reward: forward velocity + alive bonus + upright bonus - control cost
  - jerk cost - lateral drift cost.
"""

from __future__ import annotations

import numpy as np
import mujoco
import gymnasium as gym
from gymnasium import spaces


# ---------------------------------------------------------------------------
# Model geometry (must match robo_greeno_3plus3_colab.ipynb)
# ---------------------------------------------------------------------------
CHASSIS_LX, CHASSIS_LY, CHASSIS_LZ = 0.16, 0.10, 0.025
COXA_LEN, FEMUR_LEN, TIBIA_LEN = 0.05, 0.15, 0.20
BODY_Z = 0.22

LEG_LAYOUT = [
    ("LF", 0.12, "L"), ("LM", 0.00, "L"), ("LR", -0.12, "L"),
    ("RF", 0.12, "R"), ("RM", 0.00, "R"), ("RR", -0.12, "R"),
]

# Rest pose (degrees) used as the action's zero point.
REST_COXA_DEG = 0.0
REST_FEMUR_DEG = -20.0
REST_TIBIA_DEG = -60.0
ACTION_RANGE_RAD = 0.3   # action ∈ [-1, 1] maps to ±0.3 rad around rest


def _make_leg(name: str, attach_x: float, side: str) -> str:
    """Return XML for one leg attached to the chassis."""
    if side == "L":
        attach_y, fy = +CHASSIS_LY, +1
        coxa_axis, lift_axis = "0 0 -1", "1 0 0"
    else:
        attach_y, fy = -CHASSIS_LY, -1
        coxa_axis, lift_axis = "0 0 1", "-1 0 0"
    return f"""
      <body name="{name}_coxa" pos="{attach_x} {attach_y} 0">
        <joint name="{name}_coxa_j"  axis="{coxa_axis}" range="-45 45"/>
        <geom  type="capsule" size="0.012" fromto="0 0 0  0 {fy*COXA_LEN} 0" rgba="0.30 0.50 0.30 1"/>
        <body name="{name}_femur" pos="0 {fy*COXA_LEN} 0">
          <joint name="{name}_femur_j" axis="{lift_axis}" range="-60 60"/>
          <geom  type="capsule" size="0.011" fromto="0 0 0  0 {fy*FEMUR_LEN} 0" rgba="0.20 0.65 0.40 1"/>
          <body name="{name}_tibia" pos="0 {fy*FEMUR_LEN} 0">
            <joint name="{name}_tibia_j" axis="{lift_axis}" range="-90 30"/>
            <geom  type="capsule" size="0.009" fromto="0 0 0  0 {fy*TIBIA_LEN} 0" rgba="0.10 0.75 0.45 1"/>
            <site name="{name}_foot" pos="0 {fy*TIBIA_LEN} 0" size="0.012" rgba="1 0.4 0 1"/>
          </body>
        </body>
      </body>"""


def _build_xml() -> str:
    """Build the full MJCF for the hexapod with ground contact + position actuators."""
    legs_xml = "\n".join(_make_leg(name, x, s) for name, x, s in LEG_LAYOUT)

    # Position actuators, one per joint.
    acts = []
    for name, _, _ in LEG_LAYOUT:
        for jname in (f"{name}_coxa_j", f"{name}_femur_j", f"{name}_tibia_j"):
            acts.append(f'    <position name="{jname}_act" joint="{jname}" kp="35" forcerange="-3 3"/>')
    actuator_xml = "\n".join(acts)

    return f"""
<mujoco model="robo_greeno_3plus3_rl">
  <compiler angle="degree" autolimits="true"/>
  <option gravity="0 0 -9.81" timestep="0.005"/>
  <visual><global offwidth="1024" offheight="768"/></visual>

  <default>
    <joint type="hinge" damping="0.5" armature="0.005"/>
    <geom contype="1" conaffinity="1" density="500" friction="1.2 0.005 0.0001"
          solref="0.005 1" solimp="0.9 0.95 0.001"/>
    <site size="0.012"/>
  </default>

  <worldbody>
    <light pos="0 -2 2" dir="0 0.5 -1"/>
    <camera name="chase" pos="-0.6 -0.9 0.55" xyaxes="0.83 -0.55 0  0.18 0.27 0.95" fovy="55"/>
    <camera name="side"  pos="0 -1.2 0.35" xyaxes="1 0 0  0 0.3 1" fovy="50"/>
    <geom name="ground" type="plane" size="10 10 0.05" rgba="0.88 0.88 0.92 1"/>

    <body name="chassis" pos="0 0 {BODY_Z}">
      <freejoint name="root"/>
      <geom name="chassis_g" type="box" size="{CHASSIS_LX} {CHASSIS_LY} {CHASSIS_LZ}"
            rgba="0.20 0.50 0.30 1"/>
      {legs_xml}
    </body>
  </worldbody>

  <actuator>
{actuator_xml}
  </actuator>
</mujoco>
"""


MODEL_XML = _build_xml()


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
class HexapodEnv(gym.Env):
    """Robo-Greeno hexapod walking environment."""

    metadata = {"render_modes": ["rgb_array"], "render_fps": 40}

    def __init__(self, xml_string: str | None = None, frame_skip: int = 5,
                 max_steps: int = 1000, render_mode: str | None = None):
        super().__init__()
        self.xml = xml_string or MODEL_XML
        self.model = mujoco.MjModel.from_xml_string(self.xml)
        self.data = mujoco.MjData(self.model)
        self.frame_skip = frame_skip
        self.max_steps = max_steps
        self.render_mode = render_mode

        # Pre-compute joint qpos addresses (root is freejoint, qpos[0:7]).
        self._leg_names = [n for n, _, _ in LEG_LAYOUT]
        self._joint_qpos = {}
        for n in self._leg_names:
            for j in ("coxa", "femur", "tibia"):
                jid = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_JOINT, f"{n}_{j}_j")
                self._joint_qpos[(n, j)] = self.model.jnt_qposadr[jid]

        # Foot site ids for contact / position reads.
        self._foot_site_ids = {
            n: mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_SITE, f"{n}_foot")
            for n in self._leg_names
        }
        self._foot_geom_ids = {
            n: mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_GEOM, f"{n}_tibia") if False
            else None for n in self._leg_names  # we use site_xpos[z] threshold instead
        }
        self.chassis_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "chassis")

        # Rest pose in joint-angle order matching data.ctrl.
        self._rest_ctrl = np.array([
            np.deg2rad(REST_COXA_DEG),
            np.deg2rad(REST_FEMUR_DEG),
            np.deg2rad(REST_TIBIA_DEG),
        ] * 6, dtype=np.float32)
        assert self._rest_ctrl.shape[0] == self.model.nu

        self.action_space = spaces.Box(-1.0, 1.0, (self.model.nu,), dtype=np.float32)

        obs_dim = (
            1                  # chassis z
            + 4                # chassis quat
            + 18               # joint angles
            + 6                # chassis linear + angular vel
            + 18               # joint vels
            + 6                # foot contact flags
        )
        self.observation_space = spaces.Box(-np.inf, np.inf, (obs_dim,), dtype=np.float32)

        self._step_count = 0

    # ------------------------------------------------------------------
    # Gym API
    # ------------------------------------------------------------------
    def reset(self, seed: int | None = None, options=None):
        super().reset(seed=seed)
        mujoco.mj_resetData(self.model, self.data)

        # Chassis pose: standing height, identity orientation.
        self.data.qpos[0:7] = [0.0, 0.0, BODY_Z, 1.0, 0.0, 0.0, 0.0]

        # Legs into rest pose.
        for n in self._leg_names:
            self.data.qpos[self._joint_qpos[(n, "coxa")]] = np.deg2rad(REST_COXA_DEG)
            self.data.qpos[self._joint_qpos[(n, "femur")]] = np.deg2rad(REST_FEMUR_DEG)
            self.data.qpos[self._joint_qpos[(n, "tibia")]] = np.deg2rad(REST_TIBIA_DEG)

        # Small randomization helps RL avoid degenerate symmetry.
        self.data.qpos[7:] += self.np_random.uniform(-0.03, 0.03, size=self.model.nq - 7)

        mujoco.mj_forward(self.model, self.data)
        self._step_count = 0
        return self._get_obs(), {}

    def step(self, action):
        action = np.clip(action, -1.0, 1.0).astype(np.float32)
        # Action = delta from rest pose, scaled to ±ACTION_RANGE_RAD.
        self.data.ctrl[:] = self._rest_ctrl + ACTION_RANGE_RAD * action

        for _ in range(self.frame_skip):
            mujoco.mj_step(self.model, self.data)

        obs = self._get_obs()
        reward = self._get_reward()
        terminated = self._fell_over()
        self._step_count += 1
        truncated = self._step_count >= self.max_steps
        return obs, reward, terminated, truncated, {}

    def render(self):
        if self.render_mode != "rgb_array":
            return None
        if not hasattr(self, "_renderer"):
            self._renderer = mujoco.Renderer(self.model, height=420, width=720)
        self._renderer.update_scene(self.data, "chase")
        return self._renderer.render()

    def close(self):
        if hasattr(self, "_renderer"):
            self._renderer.close()
            del self._renderer

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _get_obs(self) -> np.ndarray:
        d = self.data
        return np.concatenate([
            d.qpos[2:3],                        # chassis z
            d.qpos[3:7],                        # chassis quat (w, x, y, z)
            d.qpos[7:7 + 18],                   # 18 joint angles
            d.qvel[0:6],                        # chassis 6-dof velocity
            d.qvel[6:6 + 18],                   # 18 joint velocities
            self._foot_contacts(),              # 6 binary flags
        ]).astype(np.float32)

    def _foot_contacts(self) -> np.ndarray:
        """Binary contact flag per foot, derived from foot-site z-height."""
        d = self.data
        z = np.array([d.site_xpos[self._foot_site_ids[n]][2] for n in self._leg_names])
        # Simple threshold: foot within 1.5 cm of the ground counts as contact.
        return (z < 0.015).astype(np.float32)

    def _get_reward(self) -> float:
        d = self.data
        # Reward forward (x) velocity.
        forward_vel = float(d.qvel[0])
        r_forward = 2.0 * forward_vel

        # Constant alive bonus so policy isn't incentivized to fall fast.
        r_alive = 0.5

        # Reward upright orientation. xmat[2,2] = cosine of body tilt from world +z.
        upright = float(d.xmat[self.chassis_id].reshape(3, 3)[2, 2])
        r_upright = 0.5 * upright

        # Costs.
        c_ctrl = 0.0005 * float(np.square(d.ctrl).sum())
        c_jerk = 0.0001 * float(np.square(d.qvel[6:]).sum())
        c_lateral = 0.5 * float(d.qvel[1] ** 2)

        return r_forward + r_alive + r_upright - c_ctrl - c_jerk - c_lateral

    def _fell_over(self) -> bool:
        z = float(self.data.qpos[2])
        upright = float(self.data.xmat[self.chassis_id].reshape(3, 3)[2, 2])
        return z < 0.08 or upright < 0.5


# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    env = HexapodEnv()
    obs, _ = env.reset(seed=0)
    print(f"observation dim: {obs.shape[0]} (expected {env.observation_space.shape[0]})")
    print(f"action dim:      {env.action_space.shape[0]} (= nu = {env.model.nu})")

    total = 0.0
    for i in range(50):
        a = env.action_space.sample()
        obs, r, term, trunc, _ = env.step(a)
        total += r
        if term or trunc:
            print(f"  episode ended at step {i}")
            break
    print(f"smoke test: 50 random steps, cumulative reward = {total:.3f}")
    env.close()
