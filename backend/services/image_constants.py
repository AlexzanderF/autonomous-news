# Image processing configuration constants

import os

# Maximum width for thumbnails - images larger than this will be resized
THUMBNAIL_MAX_WIDTH = int(os.getenv('THUMBNAIL_MAX_WIDTH', 1024))

# AVIF compression quality (0-100)
AVIF_QUALITY = int(os.getenv('AVIF_QUALITY', 100))
