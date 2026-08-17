import logging
import subprocess

logging.basicConfig(level=logging.INFO)


def run_fixers():
    try:
        logging.info("Running ruff fixes...")
        subprocess.run(["ruff", "check", "--fix", "."], check=False)
        logging.info("Running ruff format...")
        subprocess.run(["ruff", "format", "."], check=False)
    except Exception as e:
        logging.warning(f"Failed to run fixers: {e}")


if __name__ == "__main__":
    run_fixers()
