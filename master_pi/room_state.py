class RoomState:
    """Abstract base class for room states."""

    VALID_TRANSITIONS = set()

    def get_name(self):
        raise NotImplementedError

    def can_transition_to(self, new_status):
        return new_status in self.VALID_TRANSITIONS

    def transition(self, new_status):
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Invalid transition: '{self.get_name()}' -> '{new_status}'"
            )
        return RoomStateFactory.create(new_status)


class AvailableState(RoomState):
    VALID_TRANSITIONS = {"in use", "maintenance", "fault"}

    def get_name(self):
        return "available"


class InUseState(RoomState):
    VALID_TRANSITIONS = {"available", "maintenance", "fault"}

    def get_name(self):
        return "in use"


class MaintenanceState(RoomState):
    VALID_TRANSITIONS = {"available", "fault"}

    def get_name(self):
        return "maintenance"


class FaultState(RoomState):
    VALID_TRANSITIONS = {"maintenance", "available"}

    def get_name(self):
        return "fault"


class RoomStateFactory:
    _states = {
        "available": AvailableState,
        "in use": InUseState,
        "maintenance": MaintenanceState,
        "fault": FaultState,
    }

    @classmethod
    def create(cls, status):
        state_class = cls._states.get(status)
        if not state_class:
            raise ValueError(f"Unknown room status: '{status}'")
        return state_class()


class RoomContext:
    """Holds and manages the current state of a room."""

    def __init__(self, current_status):
        self._state = RoomStateFactory.create(current_status)

    def get_status(self):
        return self._state.get_name()

    def can_transition_to(self, new_status):
        return self._state.can_transition_to(new_status)

    def transition_to(self, new_status):
        self._state = self._state.transition(new_status)
        return self._state.get_name()
