# FaceRec Guard

FaceRec Guard is a macOS-focused face lock tool.
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


Edit `Casks/facerec-guard.rb`:

- set `version`
- set `sha256`
- keep `url` pointing to your GitHub release asset

Mirror the same change in `packaging/homebrew/Casks/facerec-guard.rb`.

### Install locally from cask file

```bash
brew install --cask ./Casks/facerec-guard.rb
```

### Tap-based install (after publishing a tap repo)

```bash
brew tap ariz/facerec
brew install --cask facerec-guard
```

## Nix quick start


nix develop
python -m unittest discover -s tests -p "test_*.py"
python -m app.enroll --samples 12 --output data/authorized_faces.json
python -m app.main --timeout 10 --fps 5 --embeddings data/authorized_faces.json --show-preview --dry-run


## Home Manager setup

Apply:

```bash
home-manager switch --flake .#ariz@facerec
```

Aliases:

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

- `app/main.py`: CLI entrypoint.
- `app/gui.py`: minimal desktop GUI.
- `app/runtime.py`: shared runtime loop.
- `app/camera.py`: frame ingestion.
- `app/recognition.py`: authorized/unauthorized classification.
- `app/state_machine.py`: lock policy state machine.
- `app/locker.py`: macOS lock command wrapper.
- `app/enroll.py`: enrollment workflow.
- `scripts/build_macos_app.sh`: app bundle + DMG build script.
- `Casks/facerec-guard.rb`: Homebrew cask definition.
- `flake.nix`: reproducible shell + Home Manager output.
- `nix/home-manager/home.nix`: user shell/env integration.

## Security and operational notes

- Embeddings are local by default.
- No auto-unlock bypass; macOS auth remains required.
- Uses user-space lock (`CGSession -suspend`).
- Tune `--match-threshold` for your environment.

## Testing

```bash
python -m unittest discover -s tests -p "test_*.py"
```
