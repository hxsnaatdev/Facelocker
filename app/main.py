import argparse
import logging

from app.camera import CameraMonitor
from app.config import AppConfig
from app.locker import MacLocker
from app.recognition import FaceRecognizer
from app.state_machine import Action, PresenceStateMachine


def parse_args() -> AppConfig:
    parser = argparse.ArgumentParser(
        description="Locks macOS when no authorized face is present for N seconds."
    )
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--fps", type=float, default=5.0)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--min-face-size", type=int, default=60)
    parser.add_argument("--embeddings", default="data/authorized_faces.json")
    parser.add_argument("--match-threshold", type=float, default=0.5)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--show-preview", action="store_true")
    args = parser.parse_args()

    return AppConfig(
        camera_index=args.camera_index,
        target_fps=args.fps,
        lock_after_absence_seconds=args.timeout,
        min_face_size=args.min_face_size,
        embeddings_path=args.embeddings,
        match_threshold=args.match_threshold,
        dry_run=args.dry_run,
        show_preview=args.show_preview,
    )


def run() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    config = parse_args()
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

    try:
        with CameraMonitor(config) as camera:
            for obs in camera.observe():
                summary = recognizer.classify(obs.frame)
                action = state.on_observation(
                    authorized_present=summary.authorized_present,
                    now=obs.timestamp,
                )

                status = (
                    f"AUTHORIZED={summary.authorized_faces} "
                    f"UNAUTHORIZED={summary.unauthorized_faces}"
                )
                logging.debug(status)

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
    except KeyboardInterrupt:
        logging.info("Shutting down by user request")
    except Exception as exc:
        logging.exception("Fatal error: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
