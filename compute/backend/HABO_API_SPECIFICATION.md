# Habo API Specification

This document specifies the HTTP API endpoints and data schemas required to fully support the Habo Flutter mobile app (`mobile/Habo/`). The app uses a repository pattern where each repository type (Habits, Events, Categories, Backup) can be backed by either SQLite (local) or HTTP (your backend).

## Table of Contents

1. [Habits API](#habits-api)
2. [Events API](#events-api)
3. [Categories API](#categories-api)
4. [Backup API](#backup-api)
5. [Data Models](#data-models)
6. [Implementation Priority](#implementation-priority)

---

## Habits API

**Base Path:** `/<user_id>/habits`

### Current Status
✅ **Partially Implemented** - Basic CRUD exists but needs enhancements for full Habo compatibility.

### Required Endpoints

#### 1. GET `/<user_id>/habits`
**Status:** ✅ Implemented (needs schema extension)

**Description:** Retrieve all habits for a user.

**Response:**
```json
{
  "habits": [
    {
      "id": 1,
      "habit_name": "Push-ups",
      "position": 0,
      "twoDayRule": false,
      "cue": "After breakfast",
      "routine": "Do 20 push-ups",
      "reward": "Feel strong",
      "showReward": true,
      "advanced": false,
      "notification": true,
      "notTime": "08:00",
      "sanction": "",
      "showSanction": false,
      "accountant": "",
      "habitType": 0,
      "targetValue": 100.0,
      "partialValue": 10.0,
      "unit": "reps",
      "archived": false,
      "streak": 5
    }
  ]
}
```

**TODO (Backend):**
- Extend `objects/habit.py` dataclass to include all Habo fields:
  - `position` (int) - Display order
  - `twoDayRule` (bool) - Whether habit uses two-day rule for streaks
  - `cue`, `routine`, `reward` (strings) - Habit loop components
  - `showReward` (bool) - Whether to show reward notifications
  - `advanced` (bool) - Whether advanced features are enabled
  - `notification` (bool) - Whether notifications are enabled
  - `notTime` (string) - Notification time in "HH:MM" format
  - `sanction` (string) - Negative consequence text
  - `showSanction` (bool) - Whether to show sanction notifications
  - `accountant` (string) - Accountability partner name
  - `habitType` (int) - 0=boolean, 1=numeric (see `HabitType` enum)
  - `targetValue` (float) - Target value for numeric habits
  - `partialValue` (float) - Partial completion threshold
  - `unit` (string) - Unit label (e.g., "reps", "miles", "pages")
  - `archived` (bool) - Whether habit is archived/hidden

#### 2. POST `/<user_id>/habits/add`
**Status:** ✅ Implemented (needs response enhancement)

**Description:** Create a new habit.

**Current Request:** Query parameters `name`, `device`

**TODO (Backend):**
- Accept JSON body with full `HabitData` payload:
```json
{
  "title": "Push-ups",
  "position": 0,
  "twoDayRule": false,
  "cue": "After breakfast",
  "routine": "Do 20 push-ups",
  "reward": "Feel strong",
  "showReward": true,
  "advanced": false,
  "notification": true,
  "notTime": "08:00",
  "sanction": "",
  "showSanction": false,
  "accountant": "",
  "habitType": 1,
  "targetValue": 20.0,
  "partialValue": 10.0,
  "unit": "reps",
  "archived": false
}
```

- **Return the created habit** (including generated `id`) instead of just a message:
```json
{
  "habit": {
    "id": 1,
    "habit_name": "Push-ups",
    ...
  }
}
```

#### 3. PUT `/<user_id>/habits/<habit_id>`
**Status:** ❌ Not Implemented

**Description:** Update a habit by ID with full JSON payload.

**Request Body:** Same as POST `/add` (full `HabitData` JSON)

**Response:** Updated habit object

**TODO (Backend):** Implement this endpoint to replace the current field-by-field update pattern.

#### 4. POST `/<user_id>/habits/update`
**Status:** ✅ Implemented (legacy, consider deprecating)

**Description:** Update a specific habit field (legacy endpoint).

**Current:** Query params `name`, `field`, `value`

**Note:** Keep for backwards compatibility, but prefer PUT endpoint above.

#### 5. POST `/<user_id>/habits/delete/<habit_id>`
**Status:** ❌ Not Implemented

**Description:** Delete a habit by ID.

**Response:**
```json
{
  "response": "Successfully deleted Habit <habit_id>"
}
```

**Current Workaround:** Mobile app resolves id → name and calls `POST /<user_id>/habits/delete?name=...`

**TODO (Backend):** Implement delete-by-id endpoint.

#### 6. POST `/<user_id>/habits/delete`
**Status:** ✅ Implemented (legacy)

**Description:** Delete a habit by name (legacy endpoint).

**Note:** Keep for backwards compatibility.

#### 7. POST `/<user_id>/habits/reorder`
**Status:** ❌ Not Implemented

**Description:** Update the display order of multiple habits.

**Request Body:**
```json
{
  "habitIds": [3, 1, 2, 4]
}
```

**Response:** Success message

**TODO (Backend):** Implement bulk position update endpoint.

---

## Events API

**Base Path:** `/<user_id>/events`

### Current Status
❌ **Not Implemented** - This is a new API that needs to be created.

### Overview
Events represent daily habit completion data (check, fail, skip, progress). Each event is tied to a specific habit ID and date. Events are what power Habo's calendar view and streak calculations.

### Data Model

**Event Structure:**
- **Primary Key:** `(habit_id, date)` - Composite key
- **Event Data:** A list containing:
  - `[0]`: `DayType` enum (integer: 0=clear, 1=check, 2=fail, 3=skip, 4=progress)
  - `[1]`: `comment` (string, optional)
  - `[2]`: `progressValue` (float, optional, only for numeric habits with DayType.progress)

**DayType Enum:**
```python
class DayType(Enum):
    CLEAR = 0      # No event (empty day)
    CHECK = 1      # Habit completed successfully
    FAIL = 2       # Habit failed/missed
    SKIP = 3       # Habit skipped intentionally
    PROGRESS = 4   # Partial progress (numeric habits only)
```

### Required Endpoints

#### 1. POST `/<user_id>/events/add`
**Description:** Insert a single event for a habit.

**Request Body:**
```json
{
  "habitId": 1,
  "date": "2026-02-13T00:00:00.000Z",
  "eventData": [1, "Did 20 push-ups", null]
}
```

**Response:**
```json
{
  "result": "Successfully added event"
}
```

**Notes:**
- `date` is ISO 8601 format (date only, time ignored)
- `eventData[0]` is DayType integer
- `eventData[1]` is comment (can be empty string)
- `eventData[2]` is progressValue (only present for DayType.progress)

#### 2. POST `/<user_id>/events/delete`
**Description:** Delete a single event for a habit.

**Request Body:**
```json
{
  "habitId": 1,
  "date": "2026-02-13T00:00:00.000Z"
}
```

**Response:**
```json
{
  "result": "Successfully deleted event"
}
```

#### 3. GET `/<user_id>/events/habit/<habit_id>`
**Description:** Get all events for a specific habit as a list.

**Response:**
```json
{
  "events": [
    ["2026-02-13T00:00:00.000Z", 1, "Did 20 push-ups"],
    ["2026-02-14T00:00:00.000Z", 1, "Did 20 push-ups"],
    ["2026-02-15T00:00:00.000Z", 4, "Did 10 push-ups", 10.0]
  ]
}
```

**Format:** Each event is `[date_string, dayType, comment, progressValue?]`

#### 4. GET `/<user_id>/events/habit/<habit_id>/map`
**Description:** Get all events for a habit as a map (DateTime → event data).

**Response:**
```json
{
  "events": {
    "2026-02-13T00:00:00.000Z": [1, "Did 20 push-ups"],
    "2026-02-14T00:00:00.000Z": [1, "Did 20 push-ups"],
    "2026-02-15T00:00:00.000Z": [4, "Did 10 push-ups", 10.0]
  }
}
```

**Format:** Map keys are ISO 8601 date strings, values are event data arrays.

#### 5. POST `/<user_id>/events/habit/<habit_id>/clear`
**Description:** Delete all events for a specific habit.

**Response:**
```json
{
  "result": "Successfully cleared all events for habit <habit_id>"
}
```

#### 6. POST `/<user_id>/events/habit/<habit_id>/batch`
**Description:** Insert multiple events for a habit in one request.

**Request Body:**
```json
{
  "habitId": 1,
  "events": {
    "2026-02-13T00:00:00.000Z": [1, "Did 20 push-ups"],
    "2026-02-14T00:00:00.000Z": [1, "Did 20 push-ups"],
    "2026-02-15T00:00:00.000Z": [4, "Did 10 push-ups", 10.0]
  }
}
```

**Response:**
```json
{
  "result": "Successfully inserted 3 events"
}
```

**Use Case:** Used during backup/restore operations.

#### 7. POST `/<user_id>/events/clear-all`
**Description:** Delete all events for all habits (used during backup restore).

**Response:**
```json
{
  "result": "Successfully cleared all events"
}
```

### Database Schema Suggestion

```sql
CREATE TABLE events (
    user_id INTEGER NOT NULL,
    habit_id INTEGER NOT NULL,
    date TEXT NOT NULL,  -- ISO 8601 date string (YYYY-MM-DD)
    day_type INTEGER NOT NULL,  -- 0=clear, 1=check, 2=fail, 3=skip, 4=progress
    comment TEXT DEFAULT '',
    progress_value REAL DEFAULT 0.0,
    PRIMARY KEY (user_id, habit_id, date),
    FOREIGN KEY (user_id, habit_id) REFERENCES habits(user_id, habit_id) ON DELETE CASCADE
);
```

---

## Categories API

**Base Path:** `/<user_id>/categories`

### Current Status
❌ **Not Implemented** - This is a new API that needs to be created.

### Overview
Categories allow users to organize habits into groups (e.g., "Health", "Work", "Personal"). Categories have a title, icon, and optional font family. Habits can belong to multiple categories.

### Data Model

**Category Structure:**
```python
{
    "id": 1,
    "title": "Health",
    "iconCodePoint": 0xe8f4,  # Unicode code point for icon
    "fontFamily": "MaterialIcons"  # Optional, defaults to MaterialIcons
}
```

### Required Endpoints

#### 1. GET `/<user_id>/categories`
**Description:** Get all categories for a user.

**Response:**
```json
{
  "categories": [
    {
      "id": 1,
      "title": "Health",
      "iconCodePoint": 58868,
      "fontFamily": "MaterialIcons"
    },
    {
      "id": 2,
      "title": "Work",
      "iconCodePoint": 58869,
      "fontFamily": null
    }
  ]
}
```

#### 2. POST `/<user_id>/categories/add`
**Description:** Create a new category.

**Request Body:**
```json
{
  "title": "Health",
  "iconCodePoint": 58868,
  "fontFamily": "MaterialIcons"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Health",
  "iconCodePoint": 58868,
  "fontFamily": "MaterialIcons"
}
```

#### 3. GET `/<user_id>/categories/<category_id>`
**Description:** Get a specific category by ID.

**Response:**
```json
{
  "category": {
    "id": 1,
    "title": "Health",
    "iconCodePoint": 58868,
    "fontFamily": "MaterialIcons"
  }
}
```

**Status Codes:**
- `200` - Category found
- `404` - Category not found

#### 4. POST `/<user_id>/categories/update/<category_id>`
**Description:** Update a category.

**Request Body:** Same as POST `/add` (full category JSON)

**Response:** Updated category object

#### 5. POST `/<user_id>/categories/delete/<category_id>`
**Description:** Delete a category (also removes all habit-category associations).

**Response:**
```json
{
  "result": "Successfully deleted category <category_id>"
}
```

### Habit-Category Association Endpoints

#### 6. GET `/<user_id>/categories/habit/<habit_id>`
**Description:** Get all categories associated with a specific habit.

**Response:**
```json
{
  "categories": [
    {
      "id": 1,
      "title": "Health",
      "iconCodePoint": 58868,
      "fontFamily": "MaterialIcons"
    }
  ]
}
```

#### 7. POST `/<user_id>/categories/habit/<habit_id>/update`
**Description:** Replace all categories for a habit (bulk update).

**Request Body:**
```json
{
  "categoryIds": [1, 2, 3]
}
```

**Response:**
```json
{
  "result": "Successfully updated categories for habit <habit_id>"
}
```

#### 8. POST `/<user_id>/categories/habit/<habit_id>/add/<category_id>`
**Description:** Add a habit to a category.

**Response:**
```json
{
  "result": "Successfully added habit <habit_id> to category <category_id>"
}
```

#### 9. POST `/<user_id>/categories/habit/<habit_id>/remove/<category_id>`
**Description:** Remove a habit from a category.

**Response:**
```json
{
  "result": "Successfully removed habit <habit_id> from category <category_id>"
}
```

### Database Schema Suggestion

```sql
CREATE TABLE categories (
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    icon_code_point INTEGER NOT NULL,
    font_family TEXT,
    UNIQUE(user_id, title)
);

CREATE TABLE habit_categories (
    user_id INTEGER NOT NULL,
    habit_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, habit_id, category_id),
    FOREIGN KEY (user_id, habit_id) REFERENCES habits(user_id, habit_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id, category_id) REFERENCES categories(user_id, category_id) ON DELETE CASCADE
);
```

---

## Backup API

**Base Path:** `/<user_id>/backup`

### Current Status
❌ **Not Implemented** - Optional feature for backup/restore.

### Overview
Backup endpoints allow users to export and import their complete Habo data (habits, events, categories) as JSON. This is useful for data migration, cloud sync, or manual backups.

### Required Endpoints

#### 1. GET `/<user_id>/backup/export`
**Description:** Export all user data as JSON backup.

**Response:**
```json
{
  "habits": [...],
  "events": {...},
  "categories": [...],
  "habit_categories": [...],
  "metadata": {
    "export_timestamp": "2026-02-13T12:00:00.000Z",
    "version": "1.0",
    "total_habits": 5,
    "total_categories": 3,
    "total_associations": 8
  }
}
```

**Format:**
- `habits`: Array of full habit objects (with all Habo fields)
- `events`: Map of `{habit_id: {date: eventData}}`
- `categories`: Array of category objects
- `habit_categories`: Array of `{habit_id, category_id}` associations
- `metadata`: Export metadata

#### 2. POST `/<user_id>/backup/import`
**Description:** Import data from a backup JSON (replaces all existing data).

**Request Body:** Same format as export response

**Response:**
```json
{
  "result": "Successfully imported backup",
  "imported": {
    "habits": 5,
    "events": 120,
    "categories": 3,
    "associations": 8
  }
}
```

**Warning:** This operation replaces ALL user data. Consider adding a confirmation step or dry-run mode.

#### 3. GET `/<user_id>/backup/validate`
**Description:** Validate backup JSON without importing.

**Request Body:** Backup JSON

**Response:**
```json
{
  "valid": true,
  "errors": [],
  "summary": {
    "habits": 5,
    "events": 120,
    "categories": 3
  }
}
```

---

## Data Models

### HabitData (Full Schema)

This is the complete schema that Habo expects for habits. Your backend should support storing and returning all these fields:

```python
{
    "id": int,                    # Primary key (auto-generated)
    "habit_name": str,            # Display name (maps to Habo's "title")
    "position": int,              # Display order (0-based)
    "twoDayRule": bool,           # Use two-day rule for streaks
    "cue": str,                   # Habit loop: cue
    "routine": str,               # Habit loop: routine
    "reward": str,                # Habit loop: reward
    "showReward": bool,           # Show reward notifications
    "advanced": bool,             # Advanced features enabled
    "notification": bool,          # Notifications enabled
    "notTime": str,               # Notification time "HH:MM"
    "sanction": str,              # Negative consequence text
    "showSanction": bool,         # Show sanction notifications
    "accountant": str,            # Accountability partner name
    "habitType": int,             # 0=boolean, 1=numeric
    "targetValue": float,         # Target for numeric habits
    "partialValue": float,        # Partial completion threshold
    "unit": str,                  # Unit label ("reps", "miles", etc.)
    "archived": bool,             # Hidden/archived status
    "streak": int,                # Current streak count (computed)
    "is_device": bool             # Device-backed habit flag (your existing field)
}
```

### Event (Full Schema)

```python
{
    "habitId": int,               # Foreign key to habit
    "date": str,                  # ISO 8601 date "YYYY-MM-DD"
    "dayType": int,               # 0=clear, 1=check, 2=fail, 3=skip, 4=progress
    "comment": str,                # Optional comment
    "progressValue": float        # Optional, only for DayType.progress
}
```

### Category (Full Schema)

```python
{
    "id": int,                    # Primary key
    "title": str,                 # Category name
    "iconCodePoint": int,         # Unicode code point for icon
    "fontFamily": str             # Optional font family (default: "MaterialIcons")
}
```

---

## Implementation Priority

### Phase 1: Basic Habits (Current)
✅ **DONE** - Basic habit CRUD with minimal fields
- GET `/habits`
- POST `/habits/add`
- POST `/habits/update`
- POST `/habits/delete`

**Next Steps:**
1. Extend `objects/habit.py` dataclass with all Habo fields
2. Update `POST /habits/add` to accept JSON body and return created habit
3. Add `PUT /habits/<id>` endpoint
4. Add `POST /habits/delete/<id>` endpoint

### Phase 2: Events (High Priority)
❌ **TODO** - Required for calendar view and streaks

**Tasks:**
1. Create `routes/events.py` blueprint
2. Create `objects/event.py` dataclass/model
3. Implement all 7 event endpoints
4. Update database schema to include events table
5. Update `RepositoryFactory` in Flutter to use `HttpEventRepository` when `useRemoteBackend = true`

### Phase 3: Categories (Medium Priority)
❌ **TODO** - Required for habit organization

**Tasks:**
1. Create `routes/categories.py` blueprint
2. Create `objects/category.py` dataclass/model
3. Implement all 9 category endpoints
4. Update database schema to include categories and habit_categories tables
5. Update `RepositoryFactory` in Flutter to use `HttpCategoryRepository`

### Phase 4: Enhanced Habits (Low Priority)
❌ **TODO** - Full Habo feature parity

**Tasks:**
1. Implement `POST /habits/reorder` endpoint
2. Ensure all Habo fields are persisted and returned
3. Add validation for habitType-specific fields (targetValue, etc.)

### Phase 5: Backup (Optional)
❌ **TODO** - Nice-to-have for data portability

**Tasks:**
1. Create `routes/backup.py` blueprint
2. Implement export/import endpoints
3. Create `HttpBackupRepository` in Flutter (or keep SQLite-only)

---

## Testing Checklist

When implementing each phase, test:

- [ ] All endpoints return correct HTTP status codes (200, 404, 400, 500)
- [ ] JSON responses match the specified schema
- [ ] Foreign key relationships are enforced (habits → events, habits → categories)
- [ ] CASCADE deletes work correctly (deleting habit deletes events)
- [ ] Date handling is consistent (ISO 8601 format)
- [ ] Error messages are informative
- [ ] Mobile app can successfully switch `useRemoteBackend = true` and use HTTP repositories

---

## Notes

- **User ID:** All routes are scoped by `user_id`. The mobile app currently uses `defaultUserId = 1` as a constant. In the future, you may want to add authentication and thread real user IDs.
- **Base URL:** The mobile app expects the Flask server at `http://192.168.2.19:5000` (see `backend/app.py`). Update `HttpHabitRepository._baseUrl` if you change this.
- **CORS:** If testing from a browser or different origin, add Flask-CORS middleware.
- **Backwards Compatibility:** Keep existing `/logs` and `/rules` endpoints for your IoT use case, even if Habo uses different endpoints (`/events`, etc.).

---

## References

- Flutter Repository Implementations:
  - `mobile/Habo/lib/repositories/http_habit_repository.dart`
  - `mobile/Habo/lib/repositories/http_event_repository.dart`
  - `mobile/Habo/lib/repositories/http_category_repository.dart`
  - `mobile/Habo/lib/repositories/repository_factory.dart`

- Backend Files to Modify:
  - `backend/objects/habit.py` - Extend dataclass
  - `backend/routes/habits.py` - Enhance endpoints
  - `backend/routes/events.py` - **Create new file**
  - `backend/routes/categories.py` - **Create new file**
  - `backend/app.py` - Register new blueprints
