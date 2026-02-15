from dataclasses import dataclass
from enum import Enum


class Action(str, Enum):
    NONE = "none"
    LOCK = "lock"


@dataclass
class PresenceStateMachine:
    lock_after_absence_seconds: float
    absent_since: float | None = None
    locked: bool = False

    def on_observation(self, authorized_present: bool, now: float) -> Action:
        if self.locked:
            return Action.NONE

        if authorized_present:
            self.absent_since = None
            return Action.NONE

        if self.absent_since is None:
            self.absent_since = now
            return Action.NONE

        if now - self.absent_since >= self.lock_after_absence_seconds:
            self.locked = True
            return Action.LOCK

        return Action.NONE
