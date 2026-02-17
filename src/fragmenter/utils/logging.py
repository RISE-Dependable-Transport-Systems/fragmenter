import sys
from pathlib import Path

from loguru import logger


def setup_logging(
    logs_dir: Path | None = None,
    log_file_name: str = "fragmenter.log",
    level: str = "DEBUG",
    rotation: str = "10 MB",
    retention: str = "1 month",
):
    """
    Configure the centralized logger.

    Args:
        logs_dir: Directory to store logs. Defaults to ./logs if None.
        log_file_name: Name of the log file.
        level: Logging level.
        rotation: Loguru rotation policy.
        retention: Loguru retention policy.
    """
    # Default to local 'logs' dir if nothing is passed
    if logs_dir is None:
        logs_dir = Path.cwd() / "logs"

    log_file = logs_dir / log_file_name

    # Ensure the logs directory exists
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # Fallback to stderr only if we can't write to disk
        logger.remove()
        logger.add(sys.stderr, level="WARNING")
        logger.warning(
            f"Cannot create log directory at {logs_dir}. File logging disabled."
        )
        return

    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stderr,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        level="INFO",
    )

    # Add file handler with rotation and retention
    logger.add(
        log_file,
        rotation=rotation,
        retention=retention,
        level=level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} - {message}"
        ),
    )

    logger.info(f"Logging configured. Logs will be saved to {log_file}")
