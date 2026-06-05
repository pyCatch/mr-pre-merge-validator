# MR Pre-Merge Validator

CLI tool for validating GitLab Merge Requests before merge.

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
- Structured logging (`INFO` / `DEBUG`)
- Human-readable CLI report
- Async architecture using `httpx`
- Test coverage with `pytest`

## Validation Rules

The validator performs the following checks:

### 1. Merge Request is not Draft

Draft merge requests cannot be merged.

### 2. Jira ticket exists

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

- Python 3.11+
- Poetry

## Installation

Clone repository:

```bash
git clone <repository-url>
cd mr-pre-merge-validator
```

Install dependencies:

```bash
poetry install
```

## Configuration

Create `.env` file:

```env
GITLAB_BASE_URL=https://gitlab.com
JIRA_BASE_URL=http://localhost:8080

LOG_LEVEL=INFO
HTTP_TIMEOUT=10
```

## Run Mock Jira Server

Start mock Jira server:

```bash
python mock_jira.py
```

The server will be available at:

```txt
http://localhost:8080
```

## Usage

Run validator:

```bash
poetry run mr-validator validate \
  --project sztomi/mr-validator-homework \
  --mr-iid 1
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

## Run Tests

Run all checks:

```bash
poetry run ruff check .
poetry run mypy src
poetry run pytest
```

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

- Better runtime error handling
- CI integration examples
- Configurable mergeable Jira statuses
- Docker support
- More validation rules