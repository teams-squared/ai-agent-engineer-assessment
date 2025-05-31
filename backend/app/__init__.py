import logging
from flask import Flask
from flask_cors import CORS
from .core.config import AppConfig

logger = logging.getLogger(__name__)

def create_app(config_object=None):
    """
    Application factory function to create and configure the Flask app.

    Args:
        config_object: Optional configuration object. Defaults to AppConfig from core.config.

    Returns:
        Flask: The configured Flask application instance.

    """
    app = Flask(__name__)

    if config_object is None:
        app.config.from_object(AppConfig)
    else:
        app.config.from_object(config_object)

    logger.info(f"Flask App '{__name__}' created with config: {app.config['ENV']}")
    if app.config.get('OPENAI_API_KEY') is None:
        logger.warning("OPENAI_API_KEY is not configured in the Flask app. OpenAI calls will fail.")

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    logger.info("CORS initialized for /api/* routes.")

    from .api.routes import api_blueprint
    app.register_blueprint(api_blueprint)
    logger.info("API blueprint registered.")

    @app.route('/')
    def index():
        logger.debug("Root path '/' accessed.")
        return "Policy Assistant API is running. Go to /api/health for status."

    return app
