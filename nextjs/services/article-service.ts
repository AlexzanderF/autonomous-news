import { GetArticleResponse, PaginatedArticlesResponse } from "@/dtos";
import { getApiBaseUrl } from "@/utils/api";

const API_BASE_URL = getApiBaseUrl();

/**
 * Fetch an article by its slug from the Python API
 */
export async function getArticleBySlug(slug: string): Promise<GetArticleResponse> {
    const url = `${API_BASE_URL}/articles/${slug}`;

    const res = await fetch(url, {
        next: { revalidate: 60 }, // Revalidate every 60 seconds
    });

    if (!res.ok) {
        if (res.status === 404) {
            throw new Error('Article not found');
        }
        throw new Error(`Failed to fetch article: ${res.statusText}`);
    }

    return res.json();
}

/**
 * Fetch paginated articles from the Python API
 */
export async function getArticles(cursor?: number, limit: number = 10, category?: string): Promise<PaginatedArticlesResponse> {
    const params = new URLSearchParams({
        limit: limit.toString(),
        sort_field: 'published_at',
        sort_direction: 'desc',
    });
    
    if (cursor !== undefined) {
        params.append('cursor', cursor.toString());
    }

    if (category) {
        params.append('category', category);
    }

    const url = `${API_BASE_URL}/articles/?${params.toString()}`;

    const res = await fetch(url, {
        next: { revalidate: 30 }, 
    });

    if (!res.ok) {
        throw new Error(`Failed to fetch articles: ${res.statusText}`);
    }

    return res.json();
}