export enum Sentiment {
  POSITIVE = 'POSITIVE',
  NEGATIVE = 'NEGATIVE',
  NEUTRAL = 'NEUTRAL',
  CONTROVERSIAL = 'CONTROVERSIAL'
}

export enum NewsCategory {
  TECH = 'TECHNOLOGY',
  GEOPOLITICS = 'GEOPOLITICS',
  FINANCE = 'FINANCE',
  ENVIRONMENT = 'ENVIRONMENT',
  SPACE = 'SPACE'
}

export interface NewsItem {
  id: string;
  slug: string; // URL-friendly identifier (unique in DB)
  headline: string;
  summary: string;
  category: NewsCategory;
  timestamp: string; // ISO string
  imageUrl: string;
  sentimentScore: number; // 0 to 100
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
  thumbnail_url: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  published_at: string;
  categories: CategoryDTO[];
  sources: SourceDTO[];
  sentiment_score: number;
}

export interface ArticleListItemDTO {
  id: number;
  title: string;
  slug: string;
  excerpt: string | null;
  thumbnail_url: string | null;
  published_at: string;
  categories: CategoryDTO[];
  sentiment_score: number;
}

export interface PaginatedArticlesResponse {
  items: ArticleListItemDTO[];
  has_more: boolean;
  next_cursor: number | null;
  page_size: number;
}

export interface FinancialAnalysisArticle {
  id: string;
  slug: string;
  title: string;
  content: string; // Markdown content
  author?: string;
  published_at: string;
  updated_at?: string;
  tags?: string[];
  thumbnail_url?: string;
}