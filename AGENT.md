# AGENT.md

## Scope

This document records architecture and delivery decisions for FaceRec Guard, including Nix/Home Manager and Homebrew cask packaging.

## What was delivered

1. Identity-based lock logic with explicit edge-case policy.
2. Enrollment flow for authorized face embeddings.
3. Reusable runtime module used by both CLI and GUI.
4. Minimal GUI for operator-friendly local usage.
5. Homebrew cask scaffolding for `.dmg` installation.
6. Nix flake and Home Manager integration.

## Runtime architecture

### Components

- `app/main.py`
  - CLI entrypoint.
  - Builds config and calls shared runtime.

- `app/gui.py`
  - Minimal `tkinter` desktop GUI.
  - Controls Start/Stop and shows live face counts.

- `app/runtime.py`
  - Shared loop used by CLI and GUI.
  - Reads camera frames, classifies faces, evaluates lock state.

- `app/recognition.py`
  - Uses `face_recognition` to produce authorized/unauthorized counts.

- `app/state_machine.py`
  - Lock decision policy based on absence of authorized faces.

- `app/locker.py`
  - Executes `CGSession -suspend` to lock macOS.

### Policy behavior

- Lock trigger depends only on `authorized_present`.
- If any authorized face exists, lock timer resets.
- If authorized face is absent for full timeout, lock command is sent.
- Required edge case is preserved:
  - authorized + unauthorized simultaneously => remain unlocked.

## Minimal GUI design

`app/gui.py` intentionally keeps UI small:

- Inputs: timeout, FPS, threshold, embeddings path.
- Toggle: dry-run.
- Buttons: Start, Stop.
- Status: running state and face counts.

No heavy framework was added; this keeps packaging simple.

## Libraries used

- `face_recognition`
  - Face locations and 128-d embeddings.
- `opencv-python`
  - Camera capture and optional frame preview.
- `numpy`
  - Embedding distance math.
- `tkinter` (stdlib)
  - Minimal desktop GUI.

## Packaging and distribution

### Homebrew cask files

- `Casks/facerec-guard.rb`
- `packaging/homebrew/Casks/facerec-guard.rb`

The top-level `Casks/` location supports standard tap layout.

### macOS app bundle and DMG

Script:

- `scripts/build_macos_app.sh`

What it does:

1. Installs/updates `pyinstaller`.
2. Builds `FaceRecGuard.app` from `app/gui.py`.
3. Creates `dist/FaceRecGuard-<version>.dmg`.
4. Prints SHA256 for cask updates.

## Nix and Home Manager

### Flake

- `flake.nix` provides:
  - `devShells.default`
  - `formatter`
  - `homeConfigurations."ariz@facerec"`

### Home Manager module

- `nix/home-manager/home.nix`
- Adds packages, env vars, and command aliases for routine tasks.

## Operational commands

### CLI run

```bash
python -m app.main --timeout 10 --fps 5 --embeddings data/authorized_faces.json --show-preview --dry-run
```

### GUI run

```bash
python -m app.gui
```

### Build DMG

```bash
./scripts/build_macos_app.sh 0.1.0
```

### Local cask install

```bash
brew install --cask ./Casks/facerec-guard.rb
```

### Nix shell

```bash
nix develop
```

### Home Manager apply

```bash
home-manager switch --flake .#ariz@facerec
```

## Validation done

- Unit tests for lock policy pass.
- Python source compiles.
- Flake and Home Manager outputs evaluate successfully.

## Known constraints

- Recognition quality is sensitive to lighting and camera angle.
- Cask requires a published GitHub release asset and matching SHA.
- GUI currently focuses on essential controls only.

## Next recommended engineering steps

1. Add temporal smoothing in recognition decisions.
2. Add integration tests with mocked recognizer outputs.
3. Add signed/notarized app pipeline for smoother Gatekeeper UX.
4. Add multi-user enrollment support.
