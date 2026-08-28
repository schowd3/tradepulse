# TradePulse Agent Rules & Guidelines

This document outlines the coding standards, repository structure, and rules for AI agents modifying the TradePulse codebase.

## 🛠️ Tech Stack & Conventions
* **Language:** Python 3.12+
* **Framework:** FastAPI
* **Database:** PostgreSQL (SQLAlchemy ORM)
* **Event Broker:** Redis (Streams)
* **Metrics:** Prometheus (`prometheus_client`)

## 📂 Directory Structure
* `app/` - Application source code.
  * `routers/` - API endpoints grouped logically.
  * `main.py` - Application entry point.
  * `models.py` - SQLAlchemy database models.
  * `schemas.py` - Pydantic models for validation.
  * `database.py` - Session management & DB connections.
  * `metrics.py` - Telemetry/Prometheus metrics setup.
  * `simulator.py` - Simulated trading flows.
* `tests/` - Test suite.
  * `conftest.py` - Shared fixtures (mock DB, mock Redis).

## ⚠️ Hard Rules
1. **Never commit duplicate files** (e.g. double extension `.py.py` or backup files).
2. **Type Hints:** Use type hints for all function arguments and return types.
3. **No Raw DB Queries:** Always use SQLAlchemy ORM methods or Pydantic serialization.
4. **Best-Effort Redis:** If Redis fails, log a warning but do NOT crash the API. Orders must still be saved to the database.
5. **No Placeholders:** All code changes must be complete and fully functional.
6. **Linting and Format:** Follow PEP 8 guidelines.

## 🧪 Testing Guidelines
* Write tests *before* or *alongside* new feature implementation.
* Always use a mocked database session (SQLite in-memory) and a mocked Redis client for tests to ensure they are fast, isolated, and do not modify external state.
