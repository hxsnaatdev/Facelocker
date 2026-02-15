import argparse
import json
import time
from pathlib import Path

import cv2
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enroll authorized face embeddings.")
    parser.add_argument("--camera-index", type=int, default=0)
    parser.add_argument("--samples", type=int, default=12)
    parser.add_argument("--interval", type=float, default=0.7)
    parser.add_argument("--output", default="data/authorized_faces.json")
    return parser.parse_args()


def main() -> int:
    try:
        import face_recognition
    except ModuleNotFoundError as exc:
        raise SystemExit("face_recognition is not installed. Install requirements first.") from exc

    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(args.camera_index)
    if not cap.isOpened():
        raise SystemExit(f"Unable to open camera index {args.camera_index}")

    collected: list[np.ndarray] = []
    last_capture = 0.0

    try:
        while len(collected) < args.samples:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.1)
                continue

            now = time.time()
            if now - last_capture < args.interval:
                _draw_status(frame, len(collected), args.samples)
                continue

            frame_rgb = frame[:, :, ::-1]
            locations = face_recognition.face_locations(frame_rgb, model="hog")
            encodings = face_recognition.face_encodings(frame_rgb, known_face_locations=locations)

            if len(encodings) == 1:
                collected.append(np.array(encodings[0], dtype=np.float64))
                last_capture = now

            _draw_status(frame, len(collected), args.samples)
    finally:
        cap.release()
        cv2.destroyAllWindows()

    mean_embedding = np.mean(np.vstack(collected), axis=0)
    payload = {
        "version": 1,
        "created_at_unix": int(time.time()),
        "embeddings": [mean_embedding.tolist()],
    }
    with output.open("w", encoding="utf-8") as f:
        json.dump(payload, f)

    print(f"Enrollment complete. Wrote {output}")
    return 0


def _draw_status(frame, captured: int, target: int) -> None:
    text = f"Enroll: {captured}/{target} (keep only your face in frame)"
    cv2.putText(
        frame,
        text,
        (16, 32),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 200, 0),
        2,
        cv2.LINE_AA,
    )
    cv2.imshow("FaceRec Enroll", frame)
    cv2.waitKey(1)


if __name__ == "__main__":
    raise SystemExit(main())
