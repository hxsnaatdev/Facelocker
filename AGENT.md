# AGENT.md

## Scope

This file documents what was implemented in this repository for FaceRec Guard, why each part exists, and how to operate and extend it safely.

## Summary of work done

1. Added face-recognition-driven lock policy.
2. Added enrollment flow for authorized user embeddings.
3. Added deterministic policy state machine tests.
4. Added Nix flake for reproducible development.
5. Added Home Manager module to standardize user shell and environment.
6. Expanded project documentation.

## Architecture implemented

### Runtime flow

1. `app/main.py` initializes config, recognizer, lock state machine, and locker.
2. `app/camera.py` yields frames at target FPS.
3. `app/recognition.py` classifies detected faces into authorized/unauthorized counts.
4. `app/state_machine.py` tracks absence duration of authorized faces.
5. `app/locker.py` executes macOS lock when policy emits `LOCK`.

### Core policy decision

- Input to policy is `authorized_present` (boolean).
- If `authorized_present == True`, absence timer is reset.
- If `authorized_present == False` continuously for `timeout` seconds, emit lock action.
- Edge case intentionally supported:
  - Authorized + unauthorized together => stay unlocked.

## Libraries and tools used

### Python runtime libraries

- `face_recognition`
  - Role: face location + embedding extraction.
  - Why: straightforward API for 128D face encodings and matching.

- `opencv-python`
  - Role: webcam frame capture and preview UI.
  - Why: stable camera integration and simple overlays.

- `numpy`
  - Role: vector distance operations for embedding comparison.
  - Why: reliable numeric primitives for recognition matching.

### macOS integration

- `CGSession -suspend`
  - Role: trigger lock screen from user space.
  - Why: native behavior without unsafe/private-kernel changes.

### Nix and environment tooling

- `flake.nix`
  - Pins ecosystem inputs and defines reproducible shell.

- Home Manager (`nix/home-manager/home.nix`)
  - Adds shell aliases and session variables.
  - Keeps local setup consistent and repeatable.

## Files added/updated

- Added: `flake.nix`
- Added: `nix/home-manager/home.nix`
- Updated: `README.md`
- Added: `AGENT.md`

## Nix flake details

### Inputs

- `nixpkgs` from `nixos-unstable`
- `flake-utils`
- `home-manager` (follows `nixpkgs`)

### Outputs

- `devShells.default`
  - Includes Python environment with:
    - `numpy`
    - `opencv4`
    - `face_recognition`
  - Includes tooling:
    - `cmake`
    - `ffmpeg`
    - `git`
    - `pkg-config`

- `homeConfigurations."ariz@facerec"`
  - Platform target: `aarch64-darwin`
  - Activates `programs.facerecGuard` module.

## Home Manager module details

Module path: `nix/home-manager/home.nix`

### Option introduced

- `programs.facerecGuard.enable` (bool)
- `programs.facerecGuard.projectDir` (string)

### Effects when enabled

1. Installs packages: `python311`, `git`, `cmake`, `ffmpeg`, `pkg-config`.
2. Sets environment variables:
- `FACEREC_PROJECT_DIR`
- `FACEREC_EMBEDDINGS`
3. Configures zsh aliases:
- `facerec-dev`
- `facerec-test`
- `facerec-enroll`
- `facerec-run`
4. Writes note file:
- `~/.config/facerec/config-note.txt`

## Operational commands

### Enter dev shell

```bash
nix develop
```

### Run tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

### Enroll face

```bash
python -m app.enroll --samples 12 --output data/authorized_faces.json
```

### Run app

```bash
python -m app.main --timeout 10 --fps 5 --embeddings data/authorized_faces.json --show-preview --dry-run
```

### Apply Home Manager profile

```bash
home-manager switch --flake .#ariz@facerec
```

## Design choices and rationale

1. Kept policy logic in a standalone state machine for clean tests.
2. Kept lock integration isolated to one module to reduce platform coupling.
3. Used Nix flake + Home Manager to stabilize developer and user runtime setup.
4. Preserved a non-Nix fallback path (`venv` + `requirements.txt`) for portability.

## Limitations and next technical steps

1. Add temporal smoothing in recognizer pipeline to reduce noisy classifications.
2. Add integration tests with mocked recognizer outputs.
3. Support multi-user enrollment (multiple authorized embeddings).
4. Encrypt local embedding storage and document key management.

## Notes for future contributors

- Do not add auto-unlock logic that bypasses macOS authentication.
- Keep security posture user-space only; avoid private APIs/root hacks.
- Preserve explicit policy behavior for authorized+unauthorized mixed frames.
