/**
 * Application constants
 */

/**
 * Site identity - centralized for easy updates
 */
export const SITE_NAME = "MacroGlance";
export const SITE_DESCRIPTION = "Financial and macroeconomic news and analysis";

/**
 * Base URL for thumbnail images.
 * 
 * In production (Docker): Uses relative path '/thumbnails' (Nginx serves them)
 * In development (local): Set NEXT_PUBLIC_THUMBNAIL_BASE_URL to your VM URL
 * 
 * Example .env.local for development:
 *   NEXT_PUBLIC_THUMBNAIL_BASE_URL=http://your-vm-ip/thumbnails
 */
export const THUMBNAIL_BASE_URL = process.env.NEXT_PUBLIC_THUMBNAIL_BASE_URL || '/thumbnails';

/**
 * Fallback image URL when no thumbnail is available
 */
export const FALLBACK_IMAGE_URL = 'https://picsum.photos/800/600';
