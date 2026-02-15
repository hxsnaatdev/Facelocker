from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    camera_index: int = 0
    target_fps: float = 5.0
    lock_after_absence_seconds: float = 10.0
    min_face_size: int = 60
    embeddings_path: str = "data/authorized_faces.json"
    match_threshold: float = 0.5
    dry_run: bool = False
    show_preview: bool = False

    def frame_interval_seconds(self) -> float:
        if self.target_fps <= 0:
            return 0.0
        return 1.0 / self.target_fps
