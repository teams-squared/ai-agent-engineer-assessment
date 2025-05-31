import os
import logging
from app import create_app
from app.core.config import AppConfig

logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    logger.info("Starting Flask development server...")
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=AppConfig.DEBUG)

