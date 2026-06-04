from rich.console import Console

from mr_validator.domain.validation import CheckStatus, ValidationResult


class CliReportRenderer:
    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()

    def render(self, result: ValidationResult) -> None:
        self._console.print("MR Pre-Merge Validation")
        self._console.print()

        for check in result.checks:
            style = "green" if check.status == CheckStatus.PASS else "red"
            self._console.print(f"[{style}][{check.status.value}][/{style}] {check.name}")
            self._console.print(f"       {check.message}")
            self._console.print()

        result_style = "green" if result.passed else "red"
        result_text = "PASSED" if result.passed else "FAILED"
        self._console.print(f"Result: [{result_style}]{result_text}[/{result_style}]")