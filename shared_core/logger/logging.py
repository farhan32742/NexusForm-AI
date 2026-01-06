import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Custom Handler to prevent UnicodeEncodeError on Windows
class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            # Safely encode/decode to ensure compatibility with stream encoding
            try:
                encoding = getattr(stream, 'encoding', 'utf-8') or 'utf-8'
                # Encode with 'replace' to handle unsupported chars (e.g. emojis on cp1252)
                clean_msg = (msg + self.terminator).encode(encoding, errors='replace').decode(encoding)
                stream.write(clean_msg)
                self.flush()
            except Exception:
                # If all else fails, handle it gracefully
                self.handleError(record)
        except Exception:
            self.handleError(record)

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(__file__), '../../..', 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
log = logging.getLogger('Agentic AI project')
log.setLevel(logging.DEBUG)
log.propagate = False  # Prevent propagation to root logger which might have unsafe handlers

# Create formatters
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# File handler with rotation
log_file = os.path.join(logs_dir, 'app.log')
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10485760,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Console handler (Using SafeStreamHandler)
console_handler = SafeStreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Add handlers to logger
log.addHandler(file_handler)
log.addHandler(console_handler)

__all__ = ['log']
