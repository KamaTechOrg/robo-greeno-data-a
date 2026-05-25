"""
hexapod_model.py  --  build the MuJoCo model of the hexapod.

The whole robot is generated in code from config.py, so there is no
separate hand-edited XML to keep in sync. Call build_mjcf() to get the
MJCF (MuJoCo's XML) as a string, or run this file directly to write a
hexapod.xml you can inspect.

A self-contained PhantomX-class hexapod: a round trunk with six
identical 3-DOF legs, 18 hinge joints, one position servo per joint,
and a ground plane. No external mesh or URDF download needed.
"""

import math

import config as cfg


def _leg(name, mount):
    """Return the MJCF body block for one leg: coxa -> femur -> tibia."""
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


def _actuators():
    rows = []
    for name, _ in cfg.LEGS:
        for joint, rng in (("coxa", cfg.COXA_RANGE),
                           ("femur", cfg.FEMUR_RANGE),
                           ("tibia", cfg.TIBIA_RANGE)):
            kp = 18.0 if joint == "coxa" else 30.0
            rows.append(
                f'    <position name="{name}_{joint}" joint="{name}_{joint}" '
                f'kp="{kp}" ctrlrange="{rng[0]:.6f} {rng[1]:.6f}"/>')
    return "\n".join(rows)


def build_mjcf():
    """Return the complete MuJoCo model as an MJCF (XML) string."""
    legs = "".join(_leg(name, mount) for name, mount in cfg.LEGS)
    spawn_z = cfg.STANCE_HEIGHT
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

    <body name="trunk" pos="0 0 {spawn_z:.4f}">
      <freejoint name="trunk"/>
      <geom name="trunk" type="cylinder" size="{cfg.BODY_RADIUS:.4f} {cfg.BODY_HALF_H:.4f}"
            mass="{cfg.TRUNK_MASS}" rgba="0.36 0.35 0.33 1"/>
      <site name="trunk_center" pos="0 0 0" size="0.01"/>{legs}
    </body>
  </worldbody>

  <actuator>
{_actuators()}
  </actuator>
</mujoco>
"""


def save(path="hexapod.xml"):
    """Write the generated MJCF to a file and return the path."""
    with open(path, "w") as fh:
        fh.write(build_mjcf())
    return path


if __name__ == "__main__":
    p = save()
    print(f"wrote {p}")
    print(f"  {3 * len(cfg.LEGS)} joints, {3 * len(cfg.LEGS)} position servos, "
          f"{len(cfg.LEGS)} legs")
