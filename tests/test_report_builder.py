from rich.console import Console

from mr_validator.domain.validation import CheckStatus, ValidationCheck, ValidationResult
from mr_validator.services.report_builder import CliReportRenderer


def test_cli_report_renderer_outputs_validation_result() -> None:
    """Ensure CLI report renderer outputs validation results correctly."""
    console = Console(record=True, force_terminal=False, width=120)
    renderer = CliReportRenderer(console=console)

    result = ValidationResult(
        checks=(
            ValidationCheck(
                name="Example check",
                status=CheckStatus.PASS,
                message="Everything is fine.",
            ),
        )
    )

    renderer.render(result)

    output = console.export_text()

    assert "MR Pre-Merge Validation" in output
    assert "Example check" in output
    assert "Everything is fine." in output
    assert "Result: PASSED" in output