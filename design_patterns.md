# Design Patterns Summary Document

## Pattern 1: State Pattern

### What pattern was used

The State Pattern is a behavioural design pattern where an object changes its behaviour based on its internal state. Each state is represented as a separate class, and the object delegates state-specific behaviour to the current state instance.

### Where and how it was implemented

**File:** `master_pi/room_state.py`

A hierarchy of state classes was created:

- `RoomState` — abstract base class defining the interface
- `AvailableState`, `InUseState`, `MaintenanceState`, `FaultState` — concrete states, each declaring which transitions are valid from that state
- `RoomStateFactory` — creates state objects by name
- `RoomContext` — holds the current state and delegates transition logic to it

**Valid transition table:**

| From \ To   | Available | In Use | Maintenance | Fault |
| ----------- | --------- | ------ | ----------- | ----- |
| Available   | —         | ✅     | ✅          | ✅    |
| In Use      | ✅        | —      | ✅          | ✅    |
| Maintenance | ✅        | ❌     | —           | ✅    |
| Fault       | ✅        | ❌     | ✅          | —     |

**File:** `master_pi/database.py` — `update_room_status()`

Before writing to the database, the function fetches the room's current status, constructs a `RoomContext`, and calls `transition_to(new_status)`. If the transition is invalid (e.g., going from `Fault` directly to `In Use`), a `ValueError` is raised and the update is rejected.

```python
context = RoomContext(current_status)
context.transition_to(new_status)  # raises ValueError if invalid
```

### Why this pattern was suitable

Room status is inherently a state machine — only certain transitions make sense (e.g., a room cannot go from `Fault` directly to `In Use` without maintenance). Without the State pattern, this logic would have been a large chain of `if/elif` checks scattered throughout the codebase. The State pattern:

- Encapsulates each state's valid transitions in its own class
- Makes it easy to add new states without modifying existing ones (Open/Closed Principle)
- Prevents invalid state transitions at the domain level, not just the UI level

### Challenges and alternatives considered

**Challenge:** Room status values in the database use different casing conventions in different parts of the system (e.g., `"Available"` vs `"available"`). The `RoomStateFactory` uses exact string matching, so status values must be normalised before being passed to it.

**Alternative considered:** A simple dictionary lookup (`VALID_TRANSITIONS = {"Available": ["In Use", "Maintenance", "Fault"], ...}`) would have worked but provides no encapsulation and would have required a central if-else dispatcher rather than polymorphic dispatch.

---

## Pattern 2: Facade Pattern

### What pattern was used

The Facade Pattern is a structural design pattern that provides a simplified interface to a complex subsystem. It hides the internal complexity from the rest of the system, exposing only what is needed.

### Where and how it was implemented

**File:** `master_pi/database.py`

`database.py` acts as a Facade over all database operations. The rest of the system (Admin Pi, Agent Pi) never writes raw SQL or manages connections directly — they simply call named functions:

```python
login_user(email, password)
book_room(room_id, start_time, end_time)
update_room_status(room_name, new_status)
get_all_room_status()
get_fault_reports()
```

Each function internally handles:

- Opening a database connection
- Executing one or more SQL queries
- Committing transactions
- Closing the connection
- Returning a structured result

The callers know nothing about the underlying MySQL queries, connection pooling, or error handling — the Facade absorbs all of that complexity.

**File:** `master_pi/db_setup.py`

The connection setup itself also uses a Facade-like approach — `get_connection()` hides the host, credentials, and driver details behind a single call.

```python
def get_connection():
    return MySQLdb.connect(host=..., user=..., passwd=..., db=...)
```

### Why this pattern was suitable

The system has four separate components (Admin Pi, Agent Pi, Room Pi, Master Pi) all needing to interact with the same database. Without a Facade, each component would need to manage its own SQL queries and connections, leading to duplicated code and tight coupling to the database schema. The Facade pattern:

- Provides a single, consistent interface to all database operations
- Hides low-level SQL and connection management from the rest of the system
- Makes it easy to change the underlying database logic without affecting callers

### Challenges and alternatives considered

**Challenge:** Because all database logic is centralised in one file, `database.py` grows large as the system adds more features. This is a known trade-off of the Facade pattern — simplicity for the caller comes at the cost of a larger subsystem file.

**Alternative considered:** Each Pi component could have managed its own database connection directly. This would have been simpler initially but would have scattered SQL logic across the codebase and made schema changes much harder to maintain.
