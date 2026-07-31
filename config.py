import os

from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()


class Config:
    """Centralized configuration for the API Test Automation Framework."""

    BASE_URL: str = os.getenv("BASE_URL", "https://jsonplaceholder.typicode.com")
    TIMEOUT: int = int(os.getenv("TIMEOUT", "10"))
    RETRIES: int = int(os.getenv("RETRIES", "3"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

    # Define log directory relative to this config file
    LOG_DIR: str = os.path.join(os.path.dirname(__file__), "logs")


# Instantiate a global config object to be imported elsewhere
config = Config()
