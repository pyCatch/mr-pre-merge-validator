#!/usr/bin/env bash

set -uo pipefail

PROJECT="sztomi/mr-validator-homework"

echo "Starting MR smoke test..."

for i in {1..100}; do
  echo
  echo "=================================================="
  echo "MR $i"
  echo "=================================================="

  poetry run mr-validator validate \
    --project "$PROJECT" \
    --mr-iid "$i"

  exit_code=$?

  echo
  echo "exit_code=$exit_code"

  if [ "$exit_code" -eq 2 ]; then
    echo
    echo "Runtime error detected while validating MR $i."
    echo "Stopping smoke test because exit code 2 means the tool could not complete validation."
    echo "Possible reasons: merge request does not exist, GitLab is unavailable, or Jira is unavailable."
    exit 2
  fi
done

echo
echo "Smoke test completed."