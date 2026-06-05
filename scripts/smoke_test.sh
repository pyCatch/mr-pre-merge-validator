#!/usr/bin/env bash

set -uo pipefail


PROJECT="sztomi/mr-validator-homework"

if command -v poetry >/dev/null 2>&1; then
  VALIDATOR_CMD=(poetry run mr-validator)
else
  VALIDATOR_CMD=(mr-validator)
fi


echo "Starting MR smoke test..."
echo "Project: $PROJECT"
echo "Validator command: ${VALIDATOR_CMD[*]}"

for i in {1..100}; do
  echo
  echo "=================================================="
  echo "MR $i"
  echo "=================================================="

  "${VALIDATOR_CMD[@]}" validate \
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