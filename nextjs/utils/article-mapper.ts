import { ArticleListItemDTO, NewsItem } from '@/dtos';
import { getThumbnailUrl } from '@/utils/thumbnails';

/**
 * Maps an ArticleListItemDTO to a NewsItem for use in NewsCard components
 */
export function mapArticleToNewsItem(article: ArticleListItemDTO): NewsItem {
  return {
    id: article.id.toString(),
    slug: article.slug,
    headline: article.title,
    summary: article.excerpt || '',
    category: article.categories.length > 0 ? article.categories[0].name : 'General',
    timestamp: article.published_at,
    imageUrl: getThumbnailUrl(article.thumbnail, article.id),
    sentimentScore: article.sentiment_score
  };
}
