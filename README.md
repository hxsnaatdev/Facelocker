# FaceRec Guard

FaceRec Guard is a macOS-focused face-presence lock tool.
It keeps your session active while an authorized face is visible and locks when no authorized face is present for a configured timeout.

## What is implemented

- Face detection and recognition pipeline (`face_recognition` + OpenCV)
- macOS lock action through `CGSession -suspend`.
- Enrollment command that captures your face embeddings and saves them locally.
- Unit-tested lock-state logic.
- Nix flake dev environment.
- Home Manager module for shell aliases and project environment variables.


Policy hardening
- Lock on absence of authorized faces only.
- Keep unlocked when authorized + unauthorized are both visible.

Reproducible environment
- Add `flake.nix` dev shell with Python and required build/runtime tools.


## Requirements

- macOS (Apple Silicon profile included in flake Home Manager config).
- Nix with flakes enabled.
- Camera permission enabled for terminal/python runtime.

## Quick start with Nix flake


nix develop
python -m unittest discover -s tests -p "test_*.py"
python -m app.enroll --samples 12 --output data/authorized_faces.json
python -m app.main --timeout 10 --fps 5 --embeddings data/authorized_faces.json --show-preview --dry-run


Remove `--dry-run` to enable real locking.

## Home Manager setup

The flake exports:

- `homeConfigurations."ariz@facerec"`

Apply it:

```bash
home-manager switch --flake .#ariz@facerec
```

After switch, these aliases are available in zsh:

- `facerec-dev`
- `facerec-test`
- `facerec-enroll`
- `facerec-run`

## Non-Nix fallback

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -p "test_*.py"
```

## Project structure

- `app/main.py`: app entrypoint and runtime loop.
- `app/camera.py`: frame ingestion.
- `app/recognition.py`: authorized/unauthorized classification.
- `app/state_machine.py`: lock decision state machine.
- `app/locker.py`: macOS lock command wrapper.
- `app/enroll.py`: enrollment workflow.
- `tests/test_state_machine.py`: lock policy unit tests.
- `flake.nix`: reproducible dev shell + Home Manager output.
- `nix/home-manager/home.nix`: user shell/env integration.

## Security and operational notes

- No cloud processing in this repo; embeddings stay local by default.
- This app does not bypass macOS authentication.
- Lock command uses user-space APIs only (`CGSession -suspend`).
- Tune `--match-threshold` per environment to reduce false positives/negatives.

## Testing

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Known limitations

- Lighting and camera angle can impact recognition quality.
- Current tests focus on lock policy state logic, not camera integration.
- Home Manager output currently targets `aarch64-darwin` for the configured profile.
