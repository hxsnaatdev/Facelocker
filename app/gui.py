import queue
import threading
import tkinter as tk
from tkinter import ttk

from app.config import AppConfig
from app.runtime import RuntimeStatus, run_guard
from app.state_machine import Action


class FaceRecGuardGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("FaceRec Guard")
        self.root.geometry("420x260")
        self.root.resizable(False, False)

        self.status_queue: queue.Queue[tuple[str, RuntimeStatus | bool | None]] = queue.Queue()
        self.stop_event = threading.Event()
        self.worker: threading.Thread | None = None

        self.timeout_var = tk.StringVar(value="10")
        self.fps_var = tk.StringVar(value="5")
        self.threshold_var = tk.StringVar(value="0.5")
        self.embeddings_var = tk.StringVar(value="data/authorized_faces.json")
        self.dry_run_var = tk.BooleanVar(value=True)

        self.state_var = tk.StringVar(value="Idle")
        self.faces_var = tk.StringVar(value="AUTHORIZED=0 UNAUTHORIZED=0")

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(200, self._drain_queue)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Timeout (seconds)").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.timeout_var, width=12).grid(row=0, column=1, sticky="w")

        ttk.Label(frame, text="FPS").grid(row=1, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.fps_var, width=12).grid(row=1, column=1, sticky="w")

        ttk.Label(frame, text="Match threshold").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.threshold_var, width=12).grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="Embeddings file").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.embeddings_var, width=30).grid(row=3, column=1, sticky="w")

        ttk.Checkbutton(frame, text="Dry run", variable=self.dry_run_var).grid(row=4, column=0, sticky="w")

        buttons = ttk.Frame(frame)
        buttons.grid(row=5, column=0, columnspan=2, pady=(10, 0), sticky="w")
        ttk.Button(buttons, text="Start", command=self._start).pack(side="left")
        ttk.Button(buttons, text="Stop", command=self._stop).pack(side="left", padx=(8, 0))

        ttk.Label(frame, text="State").grid(row=6, column=0, sticky="w", pady=(12, 0))
        ttk.Label(frame, textvariable=self.state_var).grid(row=6, column=1, sticky="w", pady=(12, 0))

        ttk.Label(frame, text="Faces").grid(row=7, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.faces_var).grid(row=7, column=1, sticky="w")

    def _build_config(self) -> AppConfig:
        return AppConfig(
            camera_index=0,
            target_fps=float(self.fps_var.get()),
            lock_after_absence_seconds=float(self.timeout_var.get()),
            min_face_size=60,
            embeddings_path=self.embeddings_var.get(),
            match_threshold=float(self.threshold_var.get()),
            dry_run=self.dry_run_var.get(),
            show_preview=False,
        )

    def _start(self) -> None:
        if self.worker is not None and self.worker.is_alive():
            return

        self.stop_event.clear()
        self.state_var.set("Running")

        config = self._build_config()

        def _worker() -> None:
            try:
                code = run_guard(
                    config=config,
                    stop_event=self.stop_event,
                    status_callback=lambda status: self.status_queue.put(("status", status)),
                )
                self.status_queue.put(("exit", code == 0))
            except Exception:
                self.status_queue.put(("exit", False))

        self.worker = threading.Thread(target=_worker, daemon=True)
        self.worker.start()

    def _stop(self) -> None:
        self.stop_event.set()
        self.state_var.set("Stopping")

    def _on_close(self) -> None:
        self._stop()
        self.root.after(150, self.root.destroy)

    def _drain_queue(self) -> None:
        while True:
            try:
                event, payload = self.status_queue.get_nowait()
            except queue.Empty:
                break

            if event == "status" and payload is not None:
                assert isinstance(payload, RuntimeStatus)
                self.faces_var.set(
                    f"AUTHORIZED={payload.authorized_faces} UNAUTHORIZED={payload.unauthorized_faces}"
                )
                if payload.action == Action.LOCK:
                    self.state_var.set("Lock sent")
                else:
                    self.state_var.set("Running")
            elif event == "exit":
                if payload is True:
                    self.state_var.set("Stopped")
                else:
                    self.state_var.set("Error")

        self.root.after(200, self._drain_queue)


def main() -> int:
    root = tk.Tk()
    FaceRecGuardGUI(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
