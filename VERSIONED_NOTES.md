# Versioned Learning Notes

This file records major refactor / learning notes by **version**.

---

## v1.0

### Overview
This version marks the first major cleanup and engineering-oriented refactor of the backup project.

### Key Improvements

#### 1. Configuration refactor
- Removed the old `config.ini`-driven approach
- Switched to `.env` / environment-variable-based configuration
- Centralized config loading in `settings.py`

**Why it matters:**
- A single config source is easier to maintain
- Better aligned with deployment, Docker, and automation
- Safer handling of sensitive data

#### 2. Database structure redesign
- Moved away from storing phone lists in a JSON-like text field
- Introduced normalized tables:
  - `users`
  - `user_phones`
  - `cookies`
- Added `init_db.py` and `migrate_phones.py`

**Why it matters:**
- Better relational design
- Easier querying and future extension
- Cleaner add/update/delete operations

#### 3. Layered project structure
- Introduced clearer separation of responsibilities:
  - `main.py` for request handling
  - `user_service.py` for business logic
  - `repository.py` for data access
  - `database.py` for connection lifecycle

**Why it matters:**
- Better maintainability
- Easier future testing and expansion
- Clearer responsibility boundaries

#### 4. Logging refactor
- Replaced `loguru` with Python standard `logging`
- Unified logging setup in `logging_config.py`
- Added rotating file logs and console logs
- Improved exception logging with traceback support

**Why it matters:**
- Fewer third-party dependencies
- More standard production-friendly logging
- Easier integration with deployment environments

#### 5. Cleanup of legacy files
Removed multiple old or duplicate files that were no longer part of the main flow, including outdated experimental or backup-style scripts.

**Why it matters:**
- Reduces maintenance confusion
- Prevents future developers from editing the wrong file
- Makes the project easier to understand

### Summary
v1.0 is the point where the project moved from a loosely organized script collection toward a more maintainable backend service structure.
