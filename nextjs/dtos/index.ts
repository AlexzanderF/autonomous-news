
export interface NewsItem {
  id: string;
  slug: string; // URL-friendly identifier (unique in DB)
  headline: string;
  summary: string;
  category: string; // Category name from API
  timestamp: string; // ISO string
  imageUrl: string;
}

export interface CategoryDTO {
  id: number;
  name: string;
}
export interface SourceDTO {
  id: number;
  url: string;
  domain: string;
}

export interface GetArticleResponse {
  id: number;
  title: string;
  slug: string;
  excerpt: string | null;
  content: string;
  thumbnail: string | null;
  // Thumbnail attribution for Creative Commons compliance
  thumbnail_attribution: {
    license: string | null;
    license_url: string | null;
    author: string | null;
    image_page_url: string | null;
    source: string | null;
  } | null;
  status: string;
  article_type: string;
  created_at: string;
  updated_at: string;
  published_at: string;
  categories: CategoryDTO[];
  sources: SourceDTO[];
  key_points: string[] | null;
}

export interface ArticleListItemDTO {
  id: number;
  title: string;
  slug: string;
  excerpt: string | null;
  thumbnail: string | null;
  published_at: string;
  categories: CategoryDTO[];
  key_points: string[] | null;
  is_featured: boolean;
}

export interface PaginatedArticlesResponse {
  items: ArticleListItemDTO[];
  has_more: boolean;
  next_cursor: number | null;
  page_size: number;
}