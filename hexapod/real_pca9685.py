"""
real_pca9685.py  --  the HARDWARE backend (Embedded boundary).

Drives 18 hobby servos through two PCA9685 16-channel PWM boards on the
Raspberry Pi's I2C bus, using the high-level adafruit_servokit.ServoKit
library exactly as the Embedded track does (see interfaces/servo_conventions.md).
It exposes the SAME interface as the simulation backend --

    backend.set_joint_targets(targets_rad)   # 18 rad, channel order 0..17
    backend.step()

so main.py swaps sim <-> real with a flag. Data A works purely in radians;
this file is the one place radians become servo commands.

Channel map (from servo_conventions.md):
    channel = leg_index * 3 + joint_index          (0..17)
    board   = channel // 16      pin = channel % 16
    joints 0..15  -> board0 (0x40) pins 0..15
    joints 16,17  -> board1 (0x41) pins 0..1

No Pi / no adafruit libraries?  The backend drops into DRY-RUN mode: it does
all the radians->degrees math and prints the channel table, so the exact same
code path is exercised on a laptop with nothing attached.
"""

import time

import robot_config as cfg

# Two-board addresses on the shared I2C bus.
BOARD_ADDRESSES = (0x40, 0x41)
# MG996R pulse width range the Embedded team uses with set_pulse_width_range.
PULSE_US = (500, 2500)
# A standard MG996R only travels ~180 deg.
SERVO_TRAVEL_DEG = 180.0


def _default_calibration():
    """Per-channel calibration, mirroring the servo_conventions.md template:
    each channel maps its joint's rad range onto the servo's 0..180 deg travel.
    `reverse` flips direction for back-to-front mounting; Embedded fills real
    numbers after calibrating each servo on the bench."""
    cal = {}
    for ch, (lo, hi) in enumerate(cfg.channel_ranges()):
        cal[ch] = {
            "min_us": PULSE_US[0], "max_us": PULSE_US[1],
            "at_rad": [lo, hi],          # servo 0 deg <-> lo, 180 deg <-> hi
            "reverse": False, "trim_deg": 0.0,
        }
    return cal


def rad_to_servo_deg(ch, rad, cal):
    """Map a joint angle (rad) to a servo command angle in [0, 180] deg,
    using channel `ch`'s calibration. Clamps to the servo's travel."""
    c = cal[ch]
    lo, hi = c["at_rad"]
    frac = 0.0 if hi == lo else (rad - lo) / (hi - lo)
    deg = frac * SERVO_TRAVEL_DEG
    if c["reverse"]:
        deg = SERVO_TRAVEL_DEG - deg
    deg += c.get("trim_deg", 0.0)
    return max(0.0, min(SERVO_TRAVEL_DEG, deg))


def range_warnings():
    """Channels whose commanded joint travel exceeds a 180 deg servo -- the
    documented MG996R femur(210)/tibia(190) problem. Returns list of strings."""
    import math
    warns = []
    for ch, (lo, hi) in enumerate(cfg.channel_ranges()):
        travel = math.degrees(hi - lo)
        if travel > SERVO_TRAVEL_DEG + 1e-6:
            warns.append(f"ch{ch}: joint travel {travel:.0f} deg > "
                         f"{SERVO_TRAVEL_DEG:.0f} deg servo (needs 270 deg servo, "
                         f"gearing, or a clamped range)")
    return warns


class Pca9685Backend:
    """Real hardware backend. Falls back to dry-run printing when the Pi /
    adafruit_servokit stack is not present, so it is testable anywhere."""

    def __init__(self, calibration=None, dry_run=None, verbose=True,
                 channels=None):
        self.cal = calibration or _default_calibration()
        self.verbose = verbose
        self.n = cfg.n_channels()
        # channels: how many are physically wired (bring-up path 3 -> 15 -> 18)
        self.wired = self.n if channels is None else int(channels)
        self._kits = None
        self._last_print = 0.0
        self.dry_run = self._connect() if dry_run is None else dry_run
        self.name = "real (pca9685, dry-run)" if self.dry_run else "real (pca9685)"
        for w in range_warnings():
            if self.verbose:
                print(f"  [warn] {w}")

    def _connect(self):
        """Try to bring up two ServoKit boards. Return True if we must dry-run."""
        try:
            from adafruit_servokit import ServoKit
        except Exception as exc:            # ImportError, board/blinka missing
            if self.verbose:
                print(f"  adafruit_servokit unavailable ({type(exc).__name__}); "
                      f"running DRY (no servos driven).")
            return True
        try:
            self._kits = [ServoKit(channels=16, address=a) for a in BOARD_ADDRESSES]
            for kit in self._kits:
                for pin in range(16):
                    kit.servo[pin].set_pulse_width_range(*PULSE_US)
            return False
        except Exception as exc:            # no I2C bus / boards not found
            if self.verbose:
                print(f"  PCA9685 boards not found ({type(exc).__name__}); "
                      f"running DRY.")
            self._kits = None
            return True

    def set_joint_targets(self, targets_rad):
        """Convert 18 channel-ordered radians to servo degrees and write them
        (or print them in dry-run)."""
        if len(targets_rad) != self.n:
            raise ValueError(f"expected {self.n} targets, got {len(targets_rad)}")
        degs = [rad_to_servo_deg(ch, targets_rad[ch], self.cal)
                for ch in range(self.n)]
        if self.dry_run:
            self._print_frame(targets_rad, degs)
            return degs
        for ch in range(min(self.wired, self.n)):
            board, pin = ch // 16, ch % 16
            self._kits[board].servo[pin].angle = degs[ch]
        return degs

    def _print_frame(self, targets_rad, degs):
        import math
        now = time.time()
        if self.verbose and now - self._last_print >= 1.0:   # throttle to 1 Hz
            self._last_print = now
            head = " ".join(f"{d:5.1f}" for d in degs[:6])
            print(f"  [dry] ch0-5 servo deg: {head}  "
                  f"(ch0 = {math.degrees(targets_rad[0]):+.1f} deg joint)")

    def channel_table(self):
        """Human table: channel -> leg/joint -> (board,pin) -> stance deg."""
        import kinematics as ik
        stance = ik.solve_channels(ik.default_stance())
        rows = []
        ch = 0
        for name, _ in cfg.LEGS:
            for joint, _rng in cfg.JOINTS:
                board, pin = ch // 16, ch % 16
                deg = rad_to_servo_deg(ch, stance[ch], self.cal)
                rows.append((ch, name, joint, board, pin, deg))
                ch += 1
        return rows

    def step(self):
        """No physics to advance on hardware; main.py paces the 50 Hz loop."""
        pass

    def pose(self):
        """Open-loop hardware has no pose feedback -- pose fusion (IMU + leg
        kinematics) is a separate Data A process. Returns None here."""
        return None

    def close(self):
        pass


def make(**kw):
    return Pca9685Backend(**kw)


if __name__ == "__main__":
    print("PCA9685 backend -- stance channel table (dry-run)\n")
    be = Pca9685Backend(dry_run=True, verbose=False)
    print(f"  {'ch':>2}  {'leg':<11} {'joint':<5}  board pin   stance_deg")
    for ch, name, joint, board, pin, deg in be.channel_table():
        print(f"  {ch:>2}  {name:<11} {joint:<5}  0x{BOARD_ADDRESSES[board]:02x}  "
              f"{pin:>2}   {deg:6.1f}")
    for w in range_warnings():
        print(f"\n  [warn] {w}")
