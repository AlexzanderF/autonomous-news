/**
 * Get the base URL for API calls.
 * - Server-side (SSR): uses internal Docker network URL
 * - Client-side (browser): uses relative path through Nginx
 */
export function getApiBaseUrl(): string {
    if (typeof window === 'undefined') {
        // Server-side: use internal Docker URL (container-to-container)
        // INTERNAL_API_BASE_URL is a server-only env var (no NEXT_PUBLIC_ prefix)
        return process.env.INTERNAL_API_BASE_URL || 'http://fastapi:8000/api';
    }
    // Client-side: use relative path (goes through Nginx)
    return process.env.NEXT_PUBLIC_API_BASE_URL || '/api';
}
