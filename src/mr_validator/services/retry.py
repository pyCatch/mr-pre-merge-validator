import asyncio
import functools
import logging
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

import httpx

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")

RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}


def retryable_request(
    *,
    attempts: int = 3,
    backoff_seconds: float = 0.5,
) -> Callable[
    [Callable[P, Awaitable[T]]],
    Callable[P, Awaitable[T]],
]:
    """
    Retry transient HTTP errors for async requests.

    Retries:
    - ConnectError
    - TimeoutException
    - HTTP 429
    - HTTP 500/502/503/504

    Does not retry:
    - HTTP 400
    - HTTP 401
    - HTTP 403
    - HTTP 404
    """

    def decorator(
        func: Callable[P, Awaitable[T]],
    ) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> T:
            last_error: Exception | None = None

            for attempt in range(1, attempts + 1):
                try:
                    logger.debug(
                        "Executing retryable request: function=%s attempt=%s/%s",
                        func.__name__,
                        attempt,
                        attempts,
                    )

                    return await func(*args, **kwargs)

                except (
                    httpx.ConnectError,
                    httpx.TimeoutException,
                ) as error:
                    last_error = error

                    logger.warning(
                        "Transient connection error: function=%s attempt=%s/%s error=%s",
                        func.__name__,
                        attempt,
                        attempts,
                        error,
                    )

                except httpx.HTTPStatusError as error:
                    status_code = error.response.status_code

                    if status_code not in RETRYABLE_STATUS_CODES:
                        raise

                    last_error = error

                    logger.warning(
                        (
                            "Retryable HTTP error: "
                            "function=%s attempt=%s/%s status_code=%s"
                        ),
                        func.__name__,
                        attempt,
                        attempts,
                        status_code,
                    )

                if attempt < attempts:
                    sleep_seconds = backoff_seconds * (2 ** (attempt - 1))

                    logger.info(
                        (
                            "Retrying request: "
                            "function=%s next_attempt=%s/%s sleep_seconds=%.2f"
                        ),
                        func.__name__,
                        attempt + 1,
                        attempts,
                        sleep_seconds,
                    )

                    await asyncio.sleep(sleep_seconds)

            logger.error(
                "Retry attempts exhausted: function=%s attempts=%s",
                func.__name__,
                attempts,
            )

            if last_error is None:
                raise RuntimeError(
                    f"Retry failed without captured error: {func.__name__}",
                )

            raise last_error

        return wrapper

    return decorator