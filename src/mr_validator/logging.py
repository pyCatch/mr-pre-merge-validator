import logging

THIRD_PARTY_LOGGERS = (
    "httpx",
    "httpcore",
)


def configure_logging(log_level: str = "INFO") -> None:
    logging.basicConfig(
        level=log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    for logger_name in THIRD_PARTY_LOGGERS:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
