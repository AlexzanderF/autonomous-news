/**
 * Application constants
 */

/**
 * Base path for thumbnail images served by Nginx.
 * Thumbnails are stored as filenames in the database (e.g., 'article_123_abc.jpg')
 * and served at /thumbnails/{filename} by Nginx.
 */
export const THUMBNAIL_BASE_PATH = '/thumbnails';

/**
 * Fallback image URL when no thumbnail is available
 */
export const FALLBACK_IMAGE_URL = 'https://picsum.photos/800/600';
