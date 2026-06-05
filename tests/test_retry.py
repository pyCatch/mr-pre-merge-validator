import httpx
import pytest

from mr_validator.services.retry import retryable_request


@pytest.mark.asyncio
async def test_retryable_request_succeeds_after_transient_connect_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure retry succeeds after a transient connection error."""
    sleep_calls: list[float] = []
    attempts = 0

    async def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr("mr_validator.services.retry.asyncio.sleep", fake_sleep)

    @retryable_request(attempts=3, backoff_seconds=0.5)
    async def unstable_operation() -> str:
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            raise httpx.ConnectError("Temporary connection error")

        return "ok"

    result = await unstable_operation()

    assert result == "ok"
    assert attempts == 2
    assert sleep_calls == [0.5]


@pytest.mark.asyncio
async def test_retryable_request_raises_after_attempts_are_exhausted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure retry raises the last error after all attempts are exhausted."""
    sleep_calls: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr("mr_validator.services.retry.asyncio.sleep", fake_sleep)

    @retryable_request(attempts=3, backoff_seconds=0.5)
    async def always_failing_operation() -> str:
        raise httpx.ConnectError("Connection failed")

    with pytest.raises(httpx.ConnectError):
        await always_failing_operation()

    assert sleep_calls == [0.5, 1.0]


@pytest.mark.asyncio
async def test_retryable_request_does_not_retry_non_retryable_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure retry does not retry non-transient HTTP errors."""
    sleep_calls: list[float] = []
    attempts = 0

    async def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr("mr_validator.services.retry.asyncio.sleep", fake_sleep)

    request = httpx.Request("GET", "http://example.com/issues/WMS-404")
    response = httpx.Response(status_code=404, request=request)

    @retryable_request(attempts=3, backoff_seconds=0.5)
    async def not_found_operation() -> str:
        nonlocal attempts
        attempts += 1
        raise httpx.HTTPStatusError("Not found", request=request, response=response)

    with pytest.raises(httpx.HTTPStatusError):
        await not_found_operation()

    assert attempts == 1
    assert sleep_calls == []


@pytest.mark.asyncio
async def test_retryable_request_retries_retryable_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure retry retries transient HTTP server errors."""
    sleep_calls: list[float] = []
    attempts = 0

    async def fake_sleep(seconds: float) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr("mr_validator.services.retry.asyncio.sleep", fake_sleep)

    request = httpx.Request("GET", "http://example.com/issues/WMS-1001")
    response = httpx.Response(status_code=500, request=request)

    @retryable_request(attempts=3, backoff_seconds=0.5)
    async def temporarily_failing_operation() -> str:
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            raise httpx.HTTPStatusError(
                "Server error",
                request=request,
                response=response,
            )

        return "ok"

    result = await temporarily_failing_operation()

    assert result == "ok"
    assert attempts == 2
    assert sleep_calls == [0.5]