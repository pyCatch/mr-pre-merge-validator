from mr_validator.domain.validation import CheckStatus, ExitCode, ValidationCheck, ValidationResult


def test_validation_check_passed_returns_true_for_pass_status() -> None:
    """Ensure validation check is passed when status is PASS."""
    check = ValidationCheck(
        name="Example check",
        status=CheckStatus.PASS,
        message="Everything is fine.",
    )

    assert check.passed is True


def test_validation_check_passed_returns_false_for_fail_status() -> None:
    """Ensure validation check is not passed when status is FAIL."""
    check = ValidationCheck(
        name="Example check",
        status=CheckStatus.FAIL,
        message="Something is wrong.",
    )

    assert check.passed is False


def test_validation_result_passes_when_all_checks_pass() -> None:
    """Ensure validation result passes when all checks pass."""
    result = ValidationResult(
        checks=(
            ValidationCheck(
                name="First check",
                status=CheckStatus.PASS,
                message="OK.",
            ),
            ValidationCheck(
                name="Second check",
                status=CheckStatus.PASS,
                message="OK.",
            ),
        )
    )

    assert result.passed is True
    assert result.exit_code == ExitCode.SUCCESS


def test_validation_result_fails_when_any_check_fails() -> None:
    """Ensure validation result fails when any check fails."""
    result = ValidationResult(
        checks=(
            ValidationCheck(
                name="First check",
                status=CheckStatus.PASS,
                message="OK.",
            ),
            ValidationCheck(
                name="Second check",
                status=CheckStatus.FAIL,
                message="Failed.",
            ),
        )
    )

    assert result.passed is False
    assert result.exit_code == ExitCode.VALIDATION_FAILED