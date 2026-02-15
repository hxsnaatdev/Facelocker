import unittest

from app.state_machine import Action, PresenceStateMachine


class PresenceStateMachineTests(unittest.TestCase):
    def test_does_not_lock_while_authorized_present(self):
        sm = PresenceStateMachine(lock_after_absence_seconds=5.0)

        self.assertEqual(sm.on_observation(True, 0.0), Action.NONE)
        self.assertEqual(sm.on_observation(True, 1.0), Action.NONE)
        self.assertEqual(sm.on_observation(True, 100.0), Action.NONE)
        self.assertFalse(sm.locked)

    def test_locks_after_continuous_absence_of_authorized_face(self):
        sm = PresenceStateMachine(lock_after_absence_seconds=5.0)

        self.assertEqual(sm.on_observation(False, 0.0), Action.NONE)
        self.assertEqual(sm.on_observation(False, 4.9), Action.NONE)
        self.assertEqual(sm.on_observation(False, 5.0), Action.LOCK)
        self.assertTrue(sm.locked)

    def test_resets_absence_timer_when_authorized_face_returns(self):
        sm = PresenceStateMachine(lock_after_absence_seconds=5.0)

        self.assertEqual(sm.on_observation(False, 0.0), Action.NONE)
        self.assertEqual(sm.on_observation(False, 4.0), Action.NONE)
        self.assertEqual(sm.on_observation(True, 4.2), Action.NONE)
        self.assertEqual(sm.on_observation(False, 6.0), Action.NONE)
        self.assertEqual(sm.on_observation(False, 10.9), Action.NONE)
        self.assertEqual(sm.on_observation(False, 11.0), Action.LOCK)

    def test_only_emits_lock_once(self):
        sm = PresenceStateMachine(lock_after_absence_seconds=1.0)

        self.assertEqual(sm.on_observation(False, 0.0), Action.NONE)
        self.assertEqual(sm.on_observation(False, 1.0), Action.LOCK)
        self.assertEqual(sm.on_observation(False, 2.0), Action.NONE)

    def test_authorized_plus_unauthorized_stays_unlocked_by_policy(self):
        sm = PresenceStateMachine(lock_after_absence_seconds=1.0)

        # authorized face present => do not move toward lock, even if others are unauthorized
        self.assertEqual(sm.on_observation(True, 0.0), Action.NONE)
        self.assertEqual(sm.on_observation(True, 1.0), Action.NONE)
        self.assertFalse(sm.locked)


if __name__ == "__main__":
    unittest.main()
