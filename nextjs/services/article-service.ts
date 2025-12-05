// API client for fetching data from Python backend

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api';

export interface CategoryDTO {
    id: number;
    name: string;
}

export interface SourceDTO {
    id: number;
    url: string;
    domain: string;
}

export interface ArticleApiResponse {
    id: number;
    title: string;
    slug: string;
    excerpt: string | null;
    content: string;
    thumbnail_url: string | null;
    status: string;
    ai_model_used: string | null;
    created_at: string;
    updated_at: string;
    published_at: string;
    categories: CategoryDTO[];
    sources: SourceDTO[];
}

/**
 * Fetch an article by its slug from the Python API
 */
export async function getArticleBySlug(slug: string): Promise<ArticleApiResponse> {
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