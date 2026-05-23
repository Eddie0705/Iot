# Test Plan

## Overview

This document outlines the testing strategy for the Smart Classroom Management System. All tests are written using `unittest` and `pytest`, with `unittest.mock` for isolating components from real database and MQTT connections.

---

## Test Files

- `tests/test_admin.py` — MQTT, room state transitions, error handling
- `tests/test_auth.py` — authentication and registration logic
- `tests/test_socket.py` — socket message format and error handling
- `tests/test_booking.py` — booking, cancellation, and token validation logic

---

## Required Coverage

### 1. User Input Validation
**File:** `tests/test_auth.py`

| Test | Description |
|------|-------------|
| `test_register_duplicate_email` | Verifies that registering with an existing email or RMIT ID returns an appropriate error instead of crashing |
| `test_register_generates_rmit_id_if_missing` | Verifies that a `TEMP-` RMIT ID is auto-generated when none is provided |

**Justification:** User input is the primary entry point for data corruption. Ensuring duplicate detection and fallback ID generation prevents database integrity errors at runtime.

---

### 2. Authentication and Booking Logic
**File:** `tests/test_auth.py`, `tests/test_booking.py`

| Test | Description |
|------|-------------|
| `test_login_success` | Valid credentials return success with correct user data |
| `test_login_wrong_password` | Wrong password returns failure message |
| `test_login_nonexistent_user` | Non-existent email returns failure message |
| `test_login_returns_user_id` | Successful login includes `user_id` in response |
| `test_register_success` | Valid registration returns success with `user_id` |
| `test_register_logs_action` | Successful registration triggers a system log entry |
| `test_book_room_success_returns_token` | Successful booking returns a one-time token |
| `test_book_room_token_is_unique` | Each booking generates a different token |
| `test_book_room_already_occupied` | Booking an occupied room returns an error |
| `test_book_room_time_conflict` | Booking a room with a time conflict returns an error |
| `test_cancel_booking_success` | Valid booking can be cancelled successfully |
| `test_use_room_success` | Valid token allows room check-in |
| `test_use_room_token_marked_as_used` | Token is marked as used after check-in |

**Justification:** Authentication is the gateway to all system features. Booking logic is the core functionality — any failure here directly impacts users. These tests cover both happy paths and all failure cases.

---

### 3. Socket and MQTT Message Format Correctness
**File:** `tests/test_admin.py`, `tests/test_socket.py`

| Test | Description |
|------|-------------|
| `test_announcement_published_to_correct_topic` | Announcements are published to `admin/announcements` |
| `test_room_status_published_to_correct_topic` | Room status updates are published to `rooms/{room_id}/status` |
| `test_mqtt_connects_before_publishing` | MQTT client connects, publishes, and disconnects in correct order |
| `test_message_sent_as_valid_json` | Socket messages are serialized as valid JSON |
| `test_message_contains_action_field` | Socket messages always contain the required `action` field |
| `test_response_is_parsed_from_json` | Socket responses are correctly deserialized from JSON |
| `test_connection_refused_returns_error` | Socket handles `ConnectionRefusedError` gracefully |
| `test_unexpected_error_returns_error` | Socket handles unexpected exceptions gracefully |

**Justification:** MQTT topic correctness is critical — publishing to the wrong topic means subscribers never receive the message. Socket message format must be valid JSON with an `action` field for the Master Pi to process requests correctly.

---

### 4. Room State Transitions
**File:** `tests/test_admin.py`

| Test | Description |
|------|-------------|
| `test_update_to_valid_status` | All valid statuses (`available`, `in_use`, `maintenance`, `fault`) produce the correct SQL |
| `test_update_room_commits` | Status update is committed to the database |
| `test_update_room_closes_connection` | Database connection is closed after update |
| `test_get_all_room_status_returns_rows` | Room status query returns correct data structure |

**Justification:** Room state is central to the system — incorrect transitions could allow double bookings or hide fault conditions from security staff. Testing all valid states ensures the SQL is always correct.

---

### 5. Error and Exception Handling
**File:** `tests/test_admin.py`, `tests/test_auth.py`, `tests/test_booking.py`

| Test | Description |
|------|-------------|
| `test_login_db_error_returns_error_response` | DB crash during login returns a structured error, not an unhandled exception |
| `test_login_wrong_credentials_returns_failure` | Missing user returns correct failure response |
| `test_get_fault_reports_handles_empty` | Empty fault report table returns `[]` not an error |
| `test_connection_always_closed_on_error` | DB connection is closed even when a query fails |
| `test_register_db_error` | DB crash during registration returns a structured error |
| `test_book_room_not_found` | Booking a non-existent room returns a structured error |
| `test_cancel_booking_not_found` | Cancelling a non-existent booking returns a structured error |
| `test_use_room_invalid_token` | Using an invalid or already-used token returns a structured error |

**Justification:** In a distributed IoT system, network and database failures are common. All DB functions must fail gracefully and always close connections to prevent resource leaks.

---

## Additional Feature: Booking Token Uniqueness and One-Time Use

Beyond the minimum coverage, we chose to test the booking token system. Each successful booking generates a unique token using `secrets.token_hex()`, which can only be used once for room check-in.

**Why this feature:**
- Tokens are security-sensitive — a reusable or predictable token allows unauthorized room access
- The one-time use logic involves multiple DB updates (`token_used = TRUE`, room status to `In Use`) that must all succeed together
- A failure here could allow users to check into rooms they haven't booked

**Tests:** `test_book_room_token_is_unique`, `test_use_room_token_marked_as_used`, `test_use_room_invalid_token` in `tests/test_booking.py`

---

## Running the Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific file
python3 -m pytest tests/test_admin.py -v
python3 -m pytest tests/test_auth.py -v
python3 -m pytest tests/test_socket.py -v
python3 -m pytest tests/test_booking.py -v
```

## Dependencies

```bash
pip install pytest pymysql
```
