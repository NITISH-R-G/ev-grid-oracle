import subprocess  # nosec B404
import logging

logger = logging.getLogger(__name__)


def run_fixers():
    try:
        logger.info("Running ruff fixes...")
        subprocess.run(["ruff", "check", "--fix", "."], check=False)  # nosec B603 B607
        logger.info("Running ruff format...")
        subprocess.run(["ruff", "format", "."], check=False)  # nosec B603 B607
    except Exception as e:
        logger.warning(f"Failed to run fixers: {e}")


if __name__ == "__main__":
    run_fixers()
