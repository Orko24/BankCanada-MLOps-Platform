"""
Logging configuration for the application
"""

import logging
import logging.config
import sys
from pathlib import Path

def setup_logging():
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    # Logging configuration
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
            }
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
                'stream': sys.stdout
            },
            'file': {
                'level': 'DEBUG',
                'formatter': 'detailed',
                'class': 'logging.FileHandler',
                'filename': 'logs/api.log',
                'mode': 'a',
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['default', 'file'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
    logger = logging.getLogger(__name__)
    logger.info("Logging configuration initialized")
