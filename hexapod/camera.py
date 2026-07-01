"""
camera.py  --  the CSI camera interface (Data B boundary).

An ArduCam-class CSI camera on the Raspberry Pi 5, captured in Python with
picamera2. The CSI ribbon carries power, ground, I2C (sensor config), the
CSI-2 data lanes and the pixel clock on one cable (see interfaces/
MujocoRpiPca9685.pdf, page 1).

Data A never touches pixels -- but this is where the Data B contract lives:
`capture_tagged(pose_provider)` grabs a frame and attaches the freshest
`pose` + `stamp_ms` to it (INTEGRATION.md section 2, option (a) "Embedded
stamps at capture"), so Data B can spatially tag detections without a 50 Hz
pose subscription.

No Pi / no picamera2?  The camera drops into a SYNTHETIC mode that returns a
generated test frame, so the tagging path runs on a laptop with no hardware.
"""

import time

import robot_config as cfg

FRAME_W, FRAME_H = 640, 480


def _now_ms():
    return int(time.time() * 1000)


class CsiCamera:
    """CSI camera capture. Real frames via picamera2 when present, otherwise a
    synthetic frame so the pose-tagging path is testable anywhere."""

    def __init__(self, width=FRAME_W, height=FRAME_H, robot_id=cfg.ROBOT_ID,
                 verbose=True):
        self.width, self.height = width, height
        self.robot_id = robot_id
        self.verbose = verbose
        self._picam = None
        self._frame_id = 0
        self.synthetic = self._open()
        self.name = "csi (synthetic)" if self.synthetic else "csi (picamera2)"

    def _open(self):
        """Try to open picamera2. Return True if we must run synthetic."""
        try:
            from picamera2 import Picamera2
        except Exception as exc:
            if self.verbose:
                print(f"  picamera2 unavailable ({type(exc).__name__}); "
                      f"synthetic frames.")
            return True
        try:
            self._picam = Picamera2()
            config = self._picam.create_preview_configuration(
                main={"size": (self.width, self.height), "format": "RGB888"})
            self._picam.configure(config)
            self._picam.start()
            return False
        except Exception as exc:
            if self.verbose:
                print(f"  CSI camera not found ({type(exc).__name__}); synthetic.")
            self._picam = None
            return True

    def get_frame(self):
        """Return one frame as an (H, W, 3) uint8 ndarray."""
        import numpy as np
        if not self.synthetic:
            return self._picam.capture_array()
        # synthetic: a moving gradient so successive frames differ.
        # compute in int32 then cast, to satisfy numpy 2.x strict uint8 rules.
        n = self._frame_id
        col = np.arange(self.width, dtype=np.int32)
        row = np.arange(self.height, dtype=np.int32)
        f = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        f[:, :, 0] = ((col[None, :] + n) % 256).astype(np.uint8)
        f[:, :, 1] = ((row[:, None] + n) % 256).astype(np.uint8)
        f[:, :, 2] = np.uint8((n * 7) % 256)
        return f

    def capture_tagged(self, pose_provider=None):
        """Grab a frame and attach the freshest pose + stamp_ms (Data B option
        (a)). `pose_provider` is a callable returning a pose_stamped 'pose'
        block (e.g. sim backend's .pose()); None when pose is unavailable."""
        stamp_ms = _now_ms()
        frame = self.get_frame()
        pose = pose_provider() if pose_provider is not None else None
        self._frame_id += 1
        return {
            "robot_id": self.robot_id,
            "frame_id": self._frame_id,
            "stamp_ms": stamp_ms,
            "pose": pose,               # None if not co-located with the estimator
            "frame": frame,             # ndarray; Data B runs detection on this
        }

    def close(self):
        if self._picam is not None:
            try:
                self._picam.stop()
            except Exception:
                pass


def make(**kw):
    return CsiCamera(**kw)


if __name__ == "__main__":
    cam = CsiCamera()
    tagged = cam.capture_tagged(pose_provider=lambda: {
        "position_m": [0.0, 0.0, cfg.STANCE_HEIGHT],
        "orientation_quat": [1.0, 0.0, 0.0, 0.0]})
    f = tagged["frame"]
    print(f"camera: {cam.name}")
    print(f"  frame {tagged['frame_id']}  shape {f.shape}  stamp_ms {tagged['stamp_ms']}")
    print(f"  pose  {tagged['pose']}")
    cam.close()
