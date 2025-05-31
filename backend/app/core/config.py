import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, '.env')

if os.path.exists(ENV_PATH):
    load_dotenv(dotenv_path=ENV_PATH)
    logger.info(f".env file loaded from {ENV_PATH}")
else:
    logger.warning(f".env file not found at {ENV_PATH}. Environment variables should be set externally.")


class Config:
    """Base configuration class. Contains default settings."""

    DEBUG = False
    TESTING = False
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ENV = os.getenv('FLASK_ENV', 'development').lower()
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    CHROMA_PERSIST_DIRECTORY = os.getenv('CHROMA_PERSIST_DIRECTORY', os.path.join(BASE_DIR, 'chroma_db_prod'))
    POLICIES_DIRECTORY = os.getenv('POLICIES_DIRECTORY', os.path.join(BASE_DIR, 'policies'))

    if not OPENAI_API_KEY:
        logger.critical("CRITICAL: OPENAI_API_KEY is not set in environment variables or .env file.")
        raise ValueError("OPENAI_API_KEY is not set. The application cannot start.")


class DevelopmentConfig(Config):
    """Development specific configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Testing specific configuration."""
    TESTING = True
    LOG_LEVEL = 'DEBUG'
    CHROMA_PERSIST_DIRECTORY = os.path.join(Config.CHROMA_PERSIST_DIRECTORY, 'testing')


class ProductionConfig(Config):
    """Production-specific configuration."""
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()


def get_config():
    env = os.getenv('FLASK_ENV', 'development').lower()
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    return DevelopmentConfig

AppConfig = get_config()

logging.basicConfig(level=AppConfig.LOG_LEVEL,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.info(f"Application running with {AppConfig.__name__}")
if AppConfig.DEBUG:
    logger.warning("Application is running in DEBUG mode. Do not use in production.")

