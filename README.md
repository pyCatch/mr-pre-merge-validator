# MR Pre-Merge Validator

CLI tool for validating GitLab Merge Requests before merge using GitLab and Jira integration.

The validator checks merge request readiness using GitLab and Jira integration and returns a clear validation report suitable for local development and CI pipelines.

## Features

- Validate that Merge Request is not Draft
- Extract Jira tickets from:
  - Merge Request title
  - Merge Request description
  - Branch name
  - Commit messages
- Verify Jira ticket existence
- Validate Jira ticket status
- Structured logging (`ERROR` / `INFO` / `DEBUG`)
- Human-readable CLI report
- Async architecture using `httpx`
- Test coverage with `pytest`

## Validation Rules

The validator performs the following checks:

### 1. Merge Request is not Draft

Draft merge requests cannot be merged.

### 2. Jira ticket is referenced

At least one Jira ticket must be referenced.

The validator searches Jira ticket keys in:

- Merge Request title
- Merge Request description
- Source branch
- Commit messages

Example Jira ticket:

```txt
WMS-1001
```

### 3. Jira ticket exists in Jira

Referenced Jira tickets must exist.

### 4. Jira ticket has mergeable status

Allowed statuses:

- `In Review`
- `Done`

## Requirements

- Python 3.11
- Poetry (recommended) or Python virtual environment (`venv`)

## Quick Start

### Option 1: Poetry (recommended)

Clone repository:

```bash
git clone <repository-url>
cd mr-pre-merge-validator
```

Install dependencies:

```bash
poetry install
```

Configure environment:

```bash
cp .env.example .env
```

Start local mock Jira:

```bash
python3 mock_jira.py
```

Run validator:

```bash
poetry run mr-validator validate \
  --project sztomi/mr-validator-homework \
  --mr-iid 1
```

### Option 2: Python venv

Clone repository:

```bash
git clone <repository-url>
cd mr-pre-merge-validator
```

Create virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install dependencies and the current project:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

Configure environment:

```bash
cp .env.example .env
```

Start local mock Jira:

```bash
python3 mock_jira.py
```

Run validator:

```bash
mr-validator validate \
  --project sztomi/mr-validator-homework \
  --mr-iid 1
```

## Installation

Clone repository:

```bash
git clone <repository-url>
cd mr-pre-merge-validator
```

### Setup with Poetry (recommended)

Install dependencies:

```bash
poetry install
```

### Setup with venv

Create virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install runtime dependencies:

```bash
pip install -r requirements.txt
```

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Install the current project in editable mode:

```bash
pip install -e .
```

Run tests:

```bash
pytest
```

Run static checks:

```bash
ruff check .
mypy src
```

## Configuration

Copy environment template:

```bash
cp .env.example .env
```

Update values if needed:

```env
GITLAB_BASE_URL=https://gitlab.com
JIRA_BASE_URL=http://localhost:8080
JIRA_TOKEN=dummy-token
REQUEST_TIMEOUT_SECONDS=10
LOG_LEVEL=INFO
```

## Local Mock Jira Setup

For local homework setup, start mock Jira server:

```bash
python3 mock_jira.py
```

The server will be available at:

```txt
http://localhost:8080
```

If you are using a real Jira instance, update `JIRA_BASE_URL` in `.env` and skip this step.

## Usage

### Run with Poetry

Run validator:

```bash
poetry run mr-validator validate \
  --project sztomi/mr-validator-homework \
  --mr-iid 1
```

Run tests:

```bash
poetry run ruff check .
poetry run mypy src
poetry run pytest
```

### Run with venv

Run validator:

```bash
mr-validator validate \
  --project sztomi/mr-validator-homework \
  --mr-iid 1
```

Run tests:

```bash
ruff check .
mypy src
pytest
```

## Example Output

Successful validation:

```txt
────────────── MR Pre-Merge Validation ──────────────

[PASS] MR is not Draft
       Merge request is ready for review.

[PASS] Jira tickets referenced
       Found Jira ticket(s): WMS-1001

[PASS] WMS-1001 exists in Jira
       WMS-1001 exists.

[PASS] WMS-1001 has mergeable status
       WMS-1001 status is In Review.

Result: PASSED
```

Failed validation:

```txt
────────────── MR Pre-Merge Validation ──────────────

[FAIL] MR is not Draft
       Merge request is draft.

Result: FAILED
```

## Logging

Default logging level:

```txt
INFO
```

Enable debug logs:

```bash
LOG_LEVEL=DEBUG poetry run mr-validator validate \
  --project sztomi/mr-validator-homework \
  --mr-iid 1
```

## Manual Smoke Test
The repository includes a helper script for manually validating multiple Merge Requests from the provided homework repository.

The script runs validation against fixture Merge Requests and helps verify different scenarios, including:

- Successful validation
- Draft Merge Requests
- Missing Jira tickets
- Invalid Jira statuses
- Multiple Jira tickets
- Missing Merge Requests


Make script executable:

```bash
chmod +x scripts/smoke_test.sh
```

Run smoke test:

```bash
./scripts/smoke_test.sh
```

The script stops automatically when a runtime error occurs (for example, when a Merge Request no longer exists).

## Project Structure

```txt
src/mr_validator/
├── application/
├── clients/
├── domain/
├── interfaces/
├── services/
└── logging.py
```

## Architecture

The project follows a layered architecture:

- `application` — use cases
- `clients` — external API integrations
- `domain` — business models and validation entities
- `interfaces` — CLI entrypoint
- `services` — helper services

## Future Improvements

- Configurable mergeable Jira statuses
- Docker support
- Additional validation rules