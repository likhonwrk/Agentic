"""
Utility functions for GitHub MCP server
"""

import logging
import sys
from typing import Optional

def setup_logging(
    name: str,
    level: str = "INFO",
    fmt: Optional[str] = None
) -> logging.Logger:
    """Set up logging configuration
    
    Args:
        name: Logger name
        level: Log level
        fmt: Log format string
        
    Returns:
        Configured logger
    """
    if fmt is None:
        fmt = "[%(asctime)s] %(levelname)s [%(name)s] %(message)s"
        
    formatter = logging.Formatter(fmt)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())
    logger.addHandler(handler)
    
    return logger
