"""
gait.py  --  foot-trajectory generators (body frame) vs. time.

A gait is just a schedule of foot targets. Each function here takes a time
`t` in seconds and returns six (x, y, z) foot targets in the body frame,
ready for kinematics.solve_channels(). The only thing that changes between
tripod and wave is *when* each leg swings -- the per-leg phase offset and
the swing window -- which is the central lesson of legged locomotion.

  stand   -- hold the neutral standing stance (no motion)
  tripod  -- fast gait, three legs swing at once (duty factor 1/2)
  wave    -- slow, steady gait, one leg swings at a time (duty factor 5/6)
"""

import robot_config as cfg
import kinematics as ik


def stand(t=0.0):
    """Hold the neutral standing stance. `t` is ignored."""
    return ik.default_stance()


def _walk(t, offsets, swing_window):
    """Shared straight-line walk. `offsets` are per-leg phase offsets (in
    cycles) and `swing_window` is the fraction of the cycle a leg is airborne.
    Swing lifts the foot and carries it forward; stance pushes the body."""
    base = ik.default_stance()
    half = cfg.GAIT_STRIDE / 2.0
    out = []
    for i, (name, mount) in enumerate(cfg.LEGS):
        bx, by, bz = base[i]
        phase = (t / cfg.GAIT_PERIOD) % 1.0
        local = (phase + offsets[i]) % 1.0
        if local < swing_window:                      # swing: lift + forward
            s = local / swing_window
            dx = -half + s * cfg.GAIT_STRIDE
            dz = cfg.GAIT_LIFT
        else:                                         # stance: push back
            s = (local - swing_window) / (1.0 - swing_window)
            dx = half - s * cfg.GAIT_STRIDE
            dz = 0.0
        out.append((bx + dx, by, bz + dz))
    return out


# Tripod: two groups of three, half a cycle apart; each leg airborne half the
# time. Legs 0,2,4 (tripod A) at offset 0; legs 1,3,5 (tripod B) at offset 1/2.
_TRIPOD_OFFSETS = [0.0, 0.5, 0.0, 0.5, 0.0, 0.5]


def tripod(t):
    """Fast alternating-tripod walk (three legs swing at once)."""
    return _walk(t, _TRIPOD_OFFSETS, swing_window=0.5)


# Wave: six evenly-spaced offsets, one leg airborne at a time; the swing
# window shrinks to 1/6 so only a single foot is ever off the ground.
_WAVE_OFFSETS = [i / 6.0 for i in range(6)]


def wave(t):
    """Slow, steady wave walk (one leg swings at a time)."""
    return _walk(t, _WAVE_OFFSETS, swing_window=1.0 / 6.0)


# name -> generator, for main.py's --gait flag
GAITS = {"stand": stand, "tripod": tripod, "wave": wave}
