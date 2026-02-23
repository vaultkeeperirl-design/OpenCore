## 2025-02-19 - Centralized Configuration Logic

**Learning:** Configuration logic, especially string normalization or correction, tends to get duplicated across read (loading env) and write (updating env) operations.
**Action:** Extract such logic into constant dictionaries or helper methods within the `Settings` class to ensure consistency and single source of truth.
