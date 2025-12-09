import { GetArticleResponse, PaginatedArticlesResponse } from "@/dtos";

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api';

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
export async function getArticles(cursor?: number, limit: number = 10): Promise<PaginatedArticlesResponse> {
    const params = new URLSearchParams({
        limit: limit.toString(),
        sort_field: 'published_at',
        sort_direction: 'desc',
    });
    
    if (cursor !== undefined) {
        params.append('cursor', cursor.toString());
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