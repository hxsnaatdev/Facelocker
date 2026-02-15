import subprocess


class MacLocker:
    CGSESSION_PATH = (
        "/System/Library/CoreServices/Menu Extras/"
        "User.menu/Contents/Resources/CGSession"
    )

    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run

    def lock(self) -> bool:
        if self.dry_run:
            return True

        result = subprocess.run(
            [self.CGSESSION_PATH, "-suspend"],
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
