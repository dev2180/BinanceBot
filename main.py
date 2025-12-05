import logging
from config import validate_config, LOG_FILE_PATH
from ui import TradingCLI


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE_PATH),
            logging.StreamHandler()
        ]
    )


def main():
    # Setup logging first
    setup_logging()

    # Validate that API keys and core settings are correct
    validate_config()

    # Start the CLI application
    app = TradingCLI()
    app.run()


if __name__ == "__main__":
    main()
