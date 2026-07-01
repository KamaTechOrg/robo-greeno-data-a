"""
sim_mujoco.py  --  the SIMULATION backend (Data A).

Builds the hexapod in MuJoCo straight from robot_config.py (no hand-edited
XML) and drives it through the exact same 18-channel interface the real
hardware uses:

    backend.set_joint_targets(targets_rad)   # 18 rad, channel order 0..17
    backend.step()                           # advance the physics

so main.py can swap this for real_pca9685.Pca9685Backend without changing
a line of gait or kinematics code. The sim also exposes the trunk pose
(pose_stamped block) so camera.py can tag frames the way Data B expects.
"""

import time

import robot_config as cfg


# --------------------------------------------------------------------
# MJCF model, generated from the config
# --------------------------------------------------------------------
def _leg_mjcf(name, mount, math):
    rx = cfg.BODY_RADIUS * math.cos(mount)
    ry = cfg.BODY_RADIUS * math.sin(mount)
    c0, c1 = cfg.COXA_RANGE
    f0, f1 = cfg.FEMUR_RANGE
    t0, t1 = cfg.TIBIA_RANGE
    L1, L2, L3 = cfg.COXA, cfg.FEMUR, cfg.TIBIA
    rf = cfg.FOOT_RADIUS
    return f"""
      <body name="{name}_coxa" pos="{rx:.6f} {ry:.6f} 0" euler="0 0 {mount:.6f}">
        <joint name="{name}_coxa" axis="0 0 1" range="{c0:.6f} {c1:.6f}"/>
        <geom type="capsule" fromto="0 0 0 {L1:.6f} 0 0" size="0.012" rgba="0.60 0.58 0.54 1"/>
        <body name="{name}_femur" pos="{L1:.6f} 0 0">
          <joint name="{name}_femur" axis="0 -1 0" range="{f0:.6f} {f1:.6f}"/>
          <geom type="capsule" fromto="0 0 0 {L2:.6f} 0 0" size="0.010" rgba="0.11 0.62 0.46 1"/>
          <body name="{name}_tibia" pos="{L2:.6f} 0 0">
            <joint name="{name}_tibia" axis="0 -1 0" range="{t0:.6f} {t1:.6f}"/>
            <geom type="capsule" fromto="0 0 0 {L3:.6f} 0 0" size="0.008" rgba="0.18 0.49 0.85 1"/>
            <geom name="{name}_foot" type="sphere" pos="{L3:.6f} 0 0" size="{rf:.6f}" rgba="0.85 0.35 0.19 1"/>
            <site name="{name}_foot" pos="{L3:.6f} 0 0" size="0.006"/>
          </body>
        </body>
      </body>"""


def _actuators_mjcf():
    rows = []
    for name, _ in cfg.LEGS:
        for joint, rng in cfg.JOINTS:
            kp = 18.0 if joint == "coxa" else 30.0
            rows.append(
                f'    <position name="{name}_{joint}" joint="{name}_{joint}" '
                f'kp="{kp}" ctrlrange="{rng[0]:.6f} {rng[1]:.6f}"/>')
    return "\n".join(rows)


def build_mjcf():
    """Return the complete MuJoCo model (MJCF/XML) as a string."""
    import math
    legs = "".join(_leg_mjcf(name, mount, math) for name, mount in cfg.LEGS)
    return f"""<mujoco model="robo_greeno_hexapod">
  <compiler angle="radian" autolimits="true"/>
  <option timestep="0.002" integrator="implicitfast" gravity="0 0 -9.81"/>
  <default>
    <joint damping="0.14" armature="0.012"/>
    <geom friction="1.1 0.06 0.01" density="700"/>
  </default>
  <visual>
    <headlight diffuse="0.5 0.5 0.5" ambient="0.4 0.4 0.4"/>
    <rgba haze="0.95 0.95 0.93 1"/>
  </visual>
  <worldbody>
    <light pos="0 0 1.4" dir="0 0 -1" diffuse="0.7 0.7 0.7"/>
    <geom name="ground" type="plane" size="3 3 0.1" rgba="0.92 0.91 0.87 1"/>
    <body name="trunk" pos="0 0 {cfg.STANCE_HEIGHT:.4f}">
      <freejoint name="trunk"/>
      <geom name="trunk" type="cylinder" size="{cfg.BODY_RADIUS:.4f} {cfg.BODY_HALF_H:.4f}"
            mass="{cfg.TRUNK_MASS}" rgba="0.36 0.35 0.33 1"/>
      <site name="trunk_center" pos="0 0 0" size="0.01"/>{legs}
    </body>
  </worldbody>
  <actuator>
{_actuators_mjcf()}
  </actuator>
</mujoco>
"""


# --------------------------------------------------------------------
# The backend
# --------------------------------------------------------------------
class MujocoBackend:
    """MuJoCo simulation backend. Same set_joint_targets / step interface as
    the real PCA9685 backend, so they are interchangeable in main.py."""

    name = "sim (mujoco)"

    def __init__(self):
        import mujoco
        self.mj = mujoco
        self.model = mujoco.MjModel.from_xml_string(build_mjcf())
        self.data = mujoco.MjData(self.model)
        self.dt = float(self.model.opt.timestep)
        # cache actuator ids in channel order (leg*3 + joint)
        self._ctrl_ids = []
        for name, _ in cfg.LEGS:
            for joint, _rng in cfg.JOINTS:
                self._ctrl_ids.append(self._aid(f"{name}_{joint}"))
        self._trunk_adr = self.model.jnt_qposadr[
            mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_JOINT, "trunk")]
        self.init_stance()

    def _aid(self, actuator_name):
        return self.mj.mj_name2id(
            self.model, self.mj.mjtObj.mjOBJ_ACTUATOR, actuator_name)

    def _jadr(self, joint_name):
        return self.model.jnt_qposadr[self.mj.mj_name2id(
            self.model, self.mj.mjtObj.mjOBJ_JOINT, joint_name)]

    def init_stance(self):
        """Spawn already standing so the robot does not snap on start."""
        import kinematics as ik
        self.mj.mj_resetData(self.model, self.data)
        t = self._trunk_adr
        self.data.qpos[t:t + 7] = [0, 0, cfg.STANCE_HEIGHT, 1, 0, 0, 0]
        for (name, mount), tgt in zip(cfg.LEGS, ik.default_stance()):
            coxa, femur, tibia = ik.leg_ik(*ik.body_target_to_leg(tgt, mount))
            for joint, val in (("coxa", coxa), ("femur", femur), ("tibia", tibia)):
                self.data.qpos[self._jadr(f"{name}_{joint}")] = val
        self.mj.mj_forward(self.model, self.data)

    def set_joint_targets(self, targets_rad):
        """Write the 18 channel-ordered joint targets (radians) to the servos."""
        if len(targets_rad) != cfg.n_channels():
            raise ValueError(f"expected {cfg.n_channels()} targets, "
                             f"got {len(targets_rad)}")
        for aid, val in zip(self._ctrl_ids, targets_rad):
            self.data.ctrl[aid] = val

    def step(self):
        """Advance the physics one timestep."""
        self.mj.mj_step(self.model, self.data)

    def pose(self):
        """Trunk pose as a pose_stamped 'pose' block (for camera tagging)."""
        t = self._trunk_adr
        q = self.data.qpos
        return {
            "position_m": [float(q[t]), float(q[t + 1]), float(q[t + 2])],
            "orientation_quat": [float(q[t + 3]), float(q[t + 4]),
                                 float(q[t + 5]), float(q[t + 6])],
        }

    def ride_height(self):
        return float(self.data.qpos[self._trunk_adr + 2])

    @property
    def sim_time(self):
        return float(self.data.time)

    def close(self):
        pass


def make():
    return MujocoBackend()
