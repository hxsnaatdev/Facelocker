# FaceRec Guard

FaceRec Guard is a macOS-focused face lock tool.
It keeps your session active while an authorized face is visible and locks when no authorized face is present for a configured timeout.

## What is implemented

- Face detection and recognition pipeline (`face_recognition` + OpenCV).
- Policy: at least one authorized face keeps the laptop unlocked.
- Edge-case policy: authorized + unauthorized faces together still stay unlocked.
- macOS lock action via `CGSession -suspend`.
- Enrollment flow to store local authorized embedding data.
- Minimal GUI app (`app.gui`) with Start/Stop and live status.
- Homebrew cask scaffolding for distributing a `.dmg` GUI build.
- Nix flake + Home Manager setup.

## Minimal GUI usage

Run directly:

```bash
python -m app.gui
```

GUI features:

- Set timeout, FPS, threshold, embeddings path.
- Dry-run toggle.
- Start/Stop monitoring.
- Live status (`AUTHORIZED` and `UNAUTHORIZED` counts).

## Homebrew cask support

Cask files:

- `Casks/facerec-guard.rb` (tap-compatible location)
- `packaging/homebrew/Casks/facerec-guard.rb` (packaging workspace copy)

### Build a macOS app + DMG

```bash
./scripts/build_macos_app.sh 0.1.0
```

This creates `dist/FaceRecGuard-0.1.0.dmg` and prints its SHA256.

### Update cask metadata

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

```bash
nix develop
python -m unittest discover -s tests -p "test_*.py"
python -m app.enroll --samples 12 --output data/authorized_faces.json
python -m app.main --timeout 10 --fps 5 --embeddings data/authorized_faces.json --show-preview --dry-run
```

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
