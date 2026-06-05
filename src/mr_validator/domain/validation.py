from dataclasses import dataclass
from enum import IntEnum, StrEnum


class CheckStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"


class ExitCode(IntEnum):
    SUCCESS = 0
    VALIDATION_FAILED = 1
    RUNTIME_ERROR = 2


@dataclass(frozen=True, slots=True)
class ValidationCheck:
    name: str
    status: CheckStatus
    message: str

    @property
    def passed(self) -> bool:
        return self.status == CheckStatus.PASS


@dataclass(frozen=True, slots=True)
class ValidationResult:
    checks: tuple[ValidationCheck, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def exit_code(self) -> int:
        return (
            ExitCode.SUCCESS
            if self.passed
            else ExitCode.VALIDATION_FAILED
    )