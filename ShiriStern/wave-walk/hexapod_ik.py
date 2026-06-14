"""
hexapod_ik.py  --  closed-form kinematics for one 3-DOF hexapod leg.

This is the exact same maths as the Stage A leg explorer
(hexapod-leg-ik-explorer.html), packaged for the MuJoCo runner.
No iteration, no solver -- pure trigonometry students can derive on
paper and check by hand.

A leg has three joints:
  coxa   -- yaw, swings the whole leg left/right
  femur  -- pitch, lifts the leg in its own vertical plane
  tibia  -- pitch at the knee

Joint sign convention (matches the MJCF model):
  coxa  > 0  -> leg swings toward +Y
  femur > 0  -> leg lifts upward
  tibia      -> 0 is a straight leg, negative folds the foot under
"""

import math

import config as cfg


def leg_ik(x, y, z, L1=cfg.COXA, L2=cfg.FEMUR, L3=cfg.TIBIA):
    """Inverse kinematics: foot target -> three joint angles.

    x, y, z : desired foot position relative to the COXA joint, in
              that leg's own frame (+x points out along the leg).
    Returns (coxa, femur, tibia) in radians, or None if out of reach.
    """
    coxa = math.atan2(y, x)                 # top view: aim the leg
    r    = math.hypot(x, y)                 # horizontal run to the foot
    rho  = r - L1                           # reach past the coxa link
    D    = math.hypot(rho, z)               # femur joint -> foot

    # reach test: the femur+tibia 2-link arm must be able to span D
    if not (abs(L2 - L3) - 1e-9 <= D <= L2 + L3 + 1e-9):
        return None

    cos_knee = (L2 * L2 + L3 * L3 - D * D) / (2.0 * L2 * L3)
    knee     = math.acos(_clamp(cos_knee))

    cos_beta = (L2 * L2 + D * D - L3 * L3) / (2.0 * L2 * D)
    beta     = math.acos(_clamp(cos_beta))

    femur = math.atan2(z, rho) + beta       # knee-up solution
    tibia = knee - math.pi                  # 0 = straight leg
    return (coxa, femur, tibia)


def leg_fk(coxa, femur, tibia, L1=cfg.COXA, L2=cfg.FEMUR, L3=cfg.TIBIA):
    """Forward kinematics: three joint angles -> foot (x, y, z).
    Used to verify the IK by round-trip:  FK(IK(target)) == target."""
    pitch_t = femur + tibia                 # absolute pitch of the tibia
    rho_foot = L1 + L2 * math.cos(femur) + L3 * math.cos(pitch_t)
    z_foot = L2 * math.sin(femur) + L3 * math.sin(pitch_t)
    return (rho_foot * math.cos(coxa),
            rho_foot * math.sin(coxa),
            z_foot)


def body_target_to_leg(foot_body, mount_angle, body_radius=cfg.BODY_RADIUS):
    """Body frame -> leg frame.

    A foot target is naturally given in the body frame. Each leg's
    coxa joint sits on the body rim at its mount angle and the leg's
    own +x axis points radially outward. This rotates a body-frame
    target into the leg frame that leg_ik() expects."""
    fx, fy, fz = foot_body
    dx = fx - body_radius * math.cos(mount_angle)
    dy = fy - body_radius * math.sin(mount_angle)
    c, s = math.cos(mount_angle), math.sin(mount_angle)
    return (dx * c + dy * s,
            -dx * s + dy * c,
            fz)


def solve_all(foot_targets_body):
    """Solve every leg at once.

    foot_targets_body : 6 (x, y, z) foot targets in the body frame,
                        one per leg in config.LEGS order.
    Returns 6 (coxa, femur, tibia) tuples.
    Raises ValueError if any leg cannot reach its target."""
    angles = []
    for (name, mount), target in zip(cfg.LEGS, foot_targets_body):
        leg_xyz = body_target_to_leg(target, mount)
        sol = leg_ik(*leg_xyz)
        if sol is None:
            raise ValueError(f"leg '{name}' cannot reach {target}")
        angles.append(sol)
    return angles


def default_stance(stance_radius=None, stance_height=None):
    """Return 6 foot targets in the body frame for a neutral stand.

    The body frame sits at the trunk centre, so a foot resting on the
    ground is FOOT_RADIUS - STANCE_HEIGHT below it (the rounded foot
    tip touches the ground, its centre sits one radius higher)."""
    R = cfg.STANCE_RADIUS if stance_radius is None else stance_radius
    H = cfg.STANCE_HEIGHT if stance_height is None else stance_height
    foot_z = cfg.FOOT_RADIUS - H
    return [(R * math.cos(mount), R * math.sin(mount), foot_z)
            for name, mount in cfg.LEGS]


def _clamp(v, lo=-1.0, hi=1.0):
    return max(lo, min(hi, v))


if __name__ == "__main__":
    print("IK / FK round-trip on the default standing stance\n")
    worst = 0.0
    for (name, mount), target in zip(cfg.LEGS, default_stance()):
        leg_xyz = body_target_to_leg(target, mount)
        sol = leg_ik(*leg_xyz)
        err = math.dist(leg_xyz, leg_fk(*sol))
        worst = max(worst, err)
        deg = tuple(round(math.degrees(a), 1) for a in sol)
        print(f"  {name:12s}  coxa/femur/tibia = {deg}  err = {err:.2e} m")
    print(f"\nworst round-trip error: {worst:.2e} m  "
          f"({'PASS' if worst < 1e-9 else 'FAIL'})")
