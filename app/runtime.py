import logging
import threading
from dataclasses import dataclass
from typing import Callable

from app.camera import CameraMonitor
from app.config import AppConfig
from app.locker import MacLocker
from app.recognition import FaceRecognizer
from app.state_machine import Action, PresenceStateMachine


@dataclass(frozen=True)
class RuntimeStatus:
    authorized_faces: int
    unauthorized_faces: int
    action: Action


def run_guard(
    config: AppConfig,
    stop_event: threading.Event | None = None,
    status_callback: Callable[[RuntimeStatus], None] | None = None,
) -> int:
    locker = MacLocker(dry_run=config.dry_run)
    recognizer = FaceRecognizer(config.embeddings_path, config.match_threshold)
    state = PresenceStateMachine(config.lock_after_absence_seconds)

    logging.info(
        "Starting FaceRec Guard (fps=%.2f timeout=%.2fs dry_run=%s threshold=%.3f)",
        config.target_fps,
        config.lock_after_absence_seconds,
        config.dry_run,
        config.match_threshold,
    )

    with CameraMonitor(config) as camera:
        for obs in camera.observe():
            if stop_event is not None and stop_event.is_set():
                logging.info("Stop requested")
                return 0

            summary = recognizer.classify(obs.frame)
            action = state.on_observation(
                authorized_present=summary.authorized_present,
                now=obs.timestamp,
            )

            if status_callback is not None:
                status_callback(
                    RuntimeStatus(
                        authorized_faces=summary.authorized_faces,
                        unauthorized_faces=summary.unauthorized_faces,
                        action=action,
                    )
                )

            if config.show_preview:
                preview_status = (
                    "AUTHORIZED PRESENT"
                    if summary.authorized_present
                    else "NO AUTHORIZED FACE"
                )
                camera.show_preview(obs.frame, preview_status)

            if action == Action.LOCK:
                logging.warning(
                    "No authorized face for %.2fs. Locking now.",
                    config.lock_after_absence_seconds,
                )
                success = locker.lock()
                if not success:
                    logging.error("Lock command failed")
                    return 1
                logging.info("Lock command sent")

    return 0
