import time
from dataclasses import dataclass

import cv2

from app.config import AppConfig


@dataclass(frozen=True)
class FrameObservation:
    timestamp: float
    frame: object


class CameraMonitor:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._capture: cv2.VideoCapture | None = None

    def __enter__(self) -> "CameraMonitor":
        self._capture = cv2.VideoCapture(self._config.camera_index)
        if not self._capture.isOpened():
            raise RuntimeError(
                f"Unable to open camera index {self._config.camera_index}. "
                "Verify camera permissions."
            )
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._capture is not None:
            self._capture.release()

        if self._config.show_preview:
            cv2.destroyAllWindows()

    def observe(self):
        if self._capture is None:
            raise RuntimeError("CameraMonitor must be used as a context manager.")

        interval = self._config.frame_interval_seconds()
        while True:
            started = time.time()
            ok, frame = self._capture.read()
            if not ok:
                time.sleep(max(interval, 0.2))
                continue

            yield FrameObservation(timestamp=time.time(), frame=frame)

            elapsed = time.time() - started
            if interval > elapsed:
                time.sleep(interval - elapsed)

    def show_preview(self, frame, status_text: str) -> None:
        color = (0, 200, 0) if status_text.startswith("AUTHORIZED") else (0, 0, 200)
        cv2.putText(
            frame,
            status_text,
            (16, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2,
            cv2.LINE_AA,
        )
        cv2.imshow("FaceRec Guard", frame)
        cv2.waitKey(1)
