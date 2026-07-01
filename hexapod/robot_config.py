"""
robot_config.py  --  the ONE geometry file for the Robo-Greeno hexapod.

Everything about the robot's shape lives here. The MuJoCo model, the
inverse kinematics, the gait and both backends (sim + real) read these
numbers and nothing else. When the real PhantomX hardware lands you edit
this file only -- no other file needs to change. That is the whole point.

This is the canonical copy for the consolidated `hexapod/` package,
identical to the geometry in ShiriStern/wave-walk/config.py and the
channel map in interfaces/servo_conventions.md.

Units: metres and radians.  Frame: +X forward, +Y left, +Z up.
"""

import math

# --------------------------------------------------------------------
# Leg link lengths  (one 3-DOF leg: coxa -> femur -> tibia)
# --------------------------------------------------------------------
COXA  = 0.040   # L1  hip link  (horizontal swing link)
FEMUR = 0.080   # L2  thigh
TIBIA = 0.130   # L3  shin

FOOT_RADIUS = 0.012   # rounded foot tip -- also the ground contact radius

# --------------------------------------------------------------------
# Body
# --------------------------------------------------------------------
BODY_RADIUS = 0.100   # centre of body  ->  each coxa joint
BODY_HALF_H = 0.018   # half the trunk thickness
TRUNK_MASS  = 0.45    # kg  (small-scale learning model)

# --------------------------------------------------------------------
# The six legs.  Each is (name, mount angle).
# Mount angle: body XY-plane, 0 = forward, positive = CCW (toward +Y).
# The LEGS order fixes the servo channel order: channel = leg*3 + joint.
# --------------------------------------------------------------------
LEGS = [
    ("front_left",   math.radians(  45.0)),
    ("mid_left",     math.radians(  90.0)),
    ("back_left",    math.radians( 135.0)),
    ("back_right",   math.radians(-135.0)),
    ("mid_right",    math.radians( -90.0)),
    ("front_right",  math.radians( -45.0)),
]

# Alternating tripod gait groups (indices into LEGS).
TRIPOD_A = [0, 2, 4]   # front_left, back_left, mid_right
TRIPOD_B = [1, 3, 5]   # mid_left,  back_right, front_right

# --------------------------------------------------------------------
# Joint travel limits  (radians)  -- coxa 100 deg, femur 210 deg, tibia 190 deg
# --------------------------------------------------------------------
COXA_RANGE  = (math.radians(-50.0), math.radians( 50.0))
FEMUR_RANGE = (math.radians(-90.0), math.radians(120.0))
TIBIA_RANGE = (math.radians(-170.0), math.radians( 20.0))

# Per-joint order and their ranges -- the three channels of every leg.
JOINTS = (("coxa", COXA_RANGE), ("femur", FEMUR_RANGE), ("tibia", TIBIA_RANGE))

# --------------------------------------------------------------------
# Default standing stance
# --------------------------------------------------------------------
STANCE_RADIUS = 0.200   # foot distance from body centre, on the ground
STANCE_HEIGHT = 0.075   # height of the body centre above the ground

# --------------------------------------------------------------------
# Tripod / wave walk parameters
# --------------------------------------------------------------------
GAIT_PERIOD = 1.4     # seconds for one full cycle
GAIT_STRIDE = 0.060   # metres a foot travels along +X per cycle
GAIT_LIFT   = 0.030   # metres a swinging foot lifts off the ground

# --------------------------------------------------------------------
# Robot identity + control rate (shared with the interfaces contract)
# --------------------------------------------------------------------
ROBOT_ID    = "spider-01"
CONTROL_HZ  = 50.0    # 50 Hz (20 ms) command rate; matches servo_conventions.md


def n_channels():
    return 3 * len(LEGS)   # 18


def channel_ranges():
    """Return the (lo, hi) rad range for every channel 0..17, in order."""
    out = []
    for _name, _mount in LEGS:
        for _joint, rng in JOINTS:
            out.append(rng)
    return out


def describe():
    """Print a short human summary of the configured robot."""
    span = 2.0 * STANCE_RADIUS
    leg_reach = COXA + FEMUR + TIBIA
    print("Robo-Greeno hexapod -- configured geometry")
    print(f"  legs            : {len(LEGS)}  x 3 DOF = {n_channels()} joints")
    print(f"  link lengths    : coxa {COXA*100:.0f} cm | "
          f"femur {FEMUR*100:.0f} cm | tibia {TIBIA*100:.0f} cm")
    print(f"  max leg reach   : {leg_reach*100:.0f} cm")
    print(f"  stance width    : {span*100:.0f} cm  (foot to foot)")
    print(f"  body ride height: {STANCE_HEIGHT*100:.0f} cm")
    print(f"  control rate    : {CONTROL_HZ:.0f} Hz")


if __name__ == "__main__":
    describe()
