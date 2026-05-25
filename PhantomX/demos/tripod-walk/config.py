"""
config.py  --  the ONE geometry file for the Robo-Greeno hexapod.

Everything about the robot's shape lives here. The MJCF model, the
inverse kinematics and the runner all read these numbers and nothing
else. When the real PhantomX hardware lands, you edit this file only
-- no other file needs to change. That is the whole point.

Units: metres and radians.  Frame: +X forward, +Y left, +Z up.
"""

import math

# --------------------------------------------------------------------
# Leg link lengths  (one 3-DOF leg: coxa -> femur -> tibia)
# Same 4 : 8 : 13 proportions as the Stage A leg explorer, in metres.
# Swap for real AX-12 dimensions when the hardware lands.
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
# --------------------------------------------------------------------
LEGS = [
    ("front_left",   math.radians(  45.0)),
    ("mid_left",     math.radians(  90.0)),
    ("back_left",    math.radians( 135.0)),
    ("back_right",   math.radians(-135.0)),
    ("mid_right",    math.radians( -90.0)),
    ("front_right",  math.radians( -45.0)),
]

# --------------------------------------------------------------------
# Alternating tripod gait groups (indices into LEGS).
# One tripod is on the ground while the other swings.
# --------------------------------------------------------------------
TRIPOD_A = [0, 2, 4]   # front_left, back_left, mid_right
TRIPOD_B = [1, 3, 5]   # mid_left,  back_right, front_right

# --------------------------------------------------------------------
# Joint travel limits  (radians)
# --------------------------------------------------------------------
COXA_RANGE  = (math.radians(-50.0), math.radians( 50.0))
FEMUR_RANGE = (math.radians(-90.0), math.radians(120.0))
TIBIA_RANGE = (math.radians(-170.0), math.radians( 20.0))

# --------------------------------------------------------------------
# Default standing stance
#   STANCE_RADIUS  -- foot distance from body centre, on the ground
#   STANCE_HEIGHT  -- height of the body centre above the ground
# --------------------------------------------------------------------
STANCE_RADIUS = 0.200
STANCE_HEIGHT = 0.075

# --------------------------------------------------------------------
# Tripod walk parameters (used by run.py --walk)
# --------------------------------------------------------------------
GAIT_PERIOD = 1.4     # seconds for one full A+B cycle
GAIT_STRIDE = 0.060   # metres a foot travels along +X per cycle
GAIT_LIFT   = 0.030   # metres a swinging foot lifts off the ground


def describe():
    """Print a short human summary of the configured robot."""
    span = 2.0 * STANCE_RADIUS
    leg_reach = COXA + FEMUR + TIBIA
    print("Robo-Greeno hexapod -- configured geometry")
    print(f"  legs            : {len(LEGS)}  x 3 DOF = {3 * len(LEGS)} joints")
    print(f"  link lengths    : coxa {COXA*100:.0f} cm | "
          f"femur {FEMUR*100:.0f} cm | tibia {TIBIA*100:.0f} cm")
    print(f"  max leg reach   : {leg_reach*100:.0f} cm")
    print(f"  stance width    : {span*100:.0f} cm  (foot to foot)")
    print(f"  body ride height: {STANCE_HEIGHT*100:.0f} cm")


if __name__ == "__main__":
    describe()
