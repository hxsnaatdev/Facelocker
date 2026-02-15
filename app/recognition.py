import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class FaceMatchSummary:
    total_faces: int
    authorized_faces: int
    unauthorized_faces: int

    @property
    def authorized_present(self) -> bool:
        return self.authorized_faces > 0


class FaceRecognizer:
    def __init__(self, embeddings_path: str, match_threshold: float) -> None:
        self._embeddings_path = Path(embeddings_path)
        self._match_threshold = match_threshold
        self._known_embeddings = self._load_embeddings(self._embeddings_path)

    def classify(self, frame_bgr) -> FaceMatchSummary:
        try:
            import face_recognition
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "face_recognition is not installed. Install requirements first."
            ) from exc

        frame_rgb = frame_bgr[:, :, ::-1]
        locations = face_recognition.face_locations(frame_rgb, model="hog")
        encodings = face_recognition.face_encodings(frame_rgb, known_face_locations=locations)

        if not encodings:
            return FaceMatchSummary(total_faces=0, authorized_faces=0, unauthorized_faces=0)

        authorized = 0
        for encoding in encodings:
            if self._is_authorized(np.array(encoding)):
                authorized += 1

        total = len(encodings)
        return FaceMatchSummary(
            total_faces=total,
            authorized_faces=authorized,
            unauthorized_faces=total - authorized,
        )

    def _is_authorized(self, encoding: np.ndarray) -> bool:
        if self._known_embeddings.size == 0:
            return False

        distances = np.linalg.norm(self._known_embeddings - encoding, axis=1)
        return bool(np.min(distances) <= self._match_threshold)

    @staticmethod
    def _load_embeddings(path: Path) -> np.ndarray:
        if not path.exists():
            return np.zeros((0, 128), dtype=np.float64)

        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        raw = payload.get("embeddings", [])
        if not raw:
            return np.zeros((0, 128), dtype=np.float64)

        arr = np.array(raw, dtype=np.float64)
        if arr.ndim != 2 or arr.shape[1] != 128:
            raise ValueError(f"Invalid embeddings shape {arr.shape} in {path}")
        return arr
