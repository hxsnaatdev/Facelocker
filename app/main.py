import argparse
import logging

from app.config import AppConfig
from app.runtime import run_guard


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

    try:
        return run_guard(config)
    except KeyboardInterrupt:
        logging.info("Shutting down by user request")
    except Exception as exc:
        logging.exception("Fatal error: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
