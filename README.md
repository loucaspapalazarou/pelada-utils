# Pelada System Tests

Automated system tests for the Pelada backend.

## Overview

This package is **self-contained** - it automatically clones the required repositories (`pelada-backend` and `pelada-common`) and keeps them up to date.

## Requirements

- Python 3.10+
- Go 1.21+ (for running the backend)
- Git

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run tests with populated database

```bash
python main.py
```

This will:
1. Clone/pull the latest `pelada-backend` and `pelada-common` repos
2. Start a fresh PocketBase server
3. Populate the database with test data
4. Keep the server running

### Populate database only

```bash
python main.py --mode populate
```

Populates the database and exits (useful for manual testing).

## Project Structure

```
pelada-system-tests/
├── main.py          # Entry point
├── server.py        # PocketBase server management
├── orchestrator.py  # Test orchestration
├── actor.py         # User simulation
├── const.py         # Configuration and repo setup
├── constants.py     # Schema constants (from pelada-common)
├── models.py        # Data models
└── repos/           # Auto-cloned repositories (gitignored)
    ├── pelada-backend/
    └── pelada-common/
```
