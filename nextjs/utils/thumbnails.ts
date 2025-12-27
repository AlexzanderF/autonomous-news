/**
 * Utility functions for handling thumbnail images.
 */

import { THUMBNAIL_BASE_PATH, FALLBACK_IMAGE_URL } from '@/constants';

/**
 * Constructs the full URL for a thumbnail image.
 * 
 * @param thumbnailFilename - The filename stored in database (e.g., 'article_123_abc.jpg')
 *                            or a full external URL (for legacy/external images)
 * @param articleId - Optional article ID for generating fallback image
 * @returns Full URL to the thumbnail image
 * 
 * @example
 * getThumbnailUrl('article_123_abc.jpg') // returns '/thumbnails/article_123_abc.jpg'
 * getThumbnailUrl('https://example.com/image.jpg') // returns 'https://example.com/image.jpg'
 * getThumbnailUrl(null, 123) // returns 'https://picsum.photos/800/600?random=123'
 */
export function getThumbnailUrl(thumbnailFilename: string | null | undefined, articleId?: number): string {
    // No thumbnail - return fallback
    if (!thumbnailFilename) {
        return articleId 
            ? `${FALLBACK_IMAGE_URL}?random=${articleId}`
            : FALLBACK_IMAGE_URL;
    }
    
    // Already a full URL (external image or legacy data) - return as-is
    if (thumbnailFilename.startsWith('http://') || thumbnailFilename.startsWith('https://')) {
        return thumbnailFilename;
    }
    
    // Local filename - construct path for Nginx
    return `${THUMBNAIL_BASE_PATH}/${thumbnailFilename}`;
}
