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

Facelocker/
├── .vscode/
│   └── settings.json
├── AGENT.md
├── app/
│   ├── __init__.py
│   ├── __pycache__/
│   │   ├── __init__.cpython-314.pyc
│   │   ├── camera.cpython-314.pyc
│   │   ├── config.cpython-314.pyc
│   │   ├── enroll.cpython-314.pyc
│   │   ├── gui.cpython-314.pyc
│   │   ├── locker.cpython-314.pyc
│   │   ├── main.cpython-314.pyc
│   │   ├── recognition.cpython-314.pyc
│   │   ├── runtime.cpython-314.pyc
│   │   └── state_machine.cpython-314.pyc
│   ├── camera.py
│   ├── config.py
│   ├── enroll.py
│   ├── gui.py
│   ├── locker.py
│   ├── main.py
│   ├── recognition.py
│   ├── runtime.py
│   └── state_machine.py
├── Casks/
│   └── facerec-guard.rb
├── flake.lock
├── flake.nix
├── launchd/
│   └── com.facerec.guard.plist
├── nix/
│   └── home-manager/
│       └── home.nix
├── packaging/
│   └── homebrew/
│       └── Casks/
│           └── facerec-guard.rb
├── README.md
├── requirements.txt
├── scripts/
│   └── build_macos_app.sh
└── tests/
    ├── __pycache__/
    │   └── test_state_machine.cpython-314.pyc
    └── test_state_machine.py
