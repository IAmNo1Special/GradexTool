# TODO List

## Critical Bug Fixes & Improvements

- [ ] **Fix Database Connection Exhaustion**
  - **Issue**: `utils/helpers.py` instantiates `UsersTable()` on every `user_check` call, potentially exhausting database connections.
  - **Goal**: Implement a Singleton pattern or connection pool for `UsersTable`.

- [ ] **Fix Fragile Data Indexing**
  - **Issue**: `utils/helpers.py` accesses database results using hardcoded indices (e.g., `current_user[4]`), which will break if the schema changes.
  - **Goal**: Update the database layer to return rows as dictionaries or named tuples.

- [ ] **Optimize Command Syncing**
  - **Issue**: `main.py` syncs all application commands in `on_ready`, which can lead to Discord API rate limiting.
  - **Goal**: Move command synchronization to a manual owner-only command.
