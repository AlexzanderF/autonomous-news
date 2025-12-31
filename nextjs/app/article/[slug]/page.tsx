import { notFound } from 'next/navigation';
import { getArticleBySlug, getArticles, ArticleType } from '@/services/article-service';
import { Share2, Clock } from 'lucide-react';
import SmartImage from '@/components/SmartImage';
import TableOfContents from '@/components/TableOfContents';
import ArticleContent from '@/components/ArticleContent';
import AdPlaceholder from '@/components/AdPlaceholder';
import SentimentAnalysis from '@/components/SentimentAnalysis';
import { getThumbnailUrl } from '@/utils/thumbnails';
import { NewsItem } from '@/dtos';
import NewsCard from '@/components/NewsCard';
import { mapArticleToNewsItem } from '@/utils/article-mapper';

// Force dynamic rendering to prevent API calls during build time
export const dynamic = 'force-dynamic';

interface ArticlePageProps {
  params: Promise<{ slug: string }>;
}

export default async function ArticlePage({ params }: ArticlePageProps) {
  const { slug } = await params;
  let article;

  try {
    article = await getArticleBySlug(slug);
  } catch {
    notFound();
  }

  // Calculate sentiment score for display
  const sentimentScore = article.sentiment_score;

  // Extract section headings from markdown for table of contents
  // Looking for lines that start with ### (h3 headers) which are section titles
  const headings = article.content
    .split('\n')
    .filter(line => line.trim().startsWith('### '))
    .map(line => line.trim().replace(/^(### )|(\*\*)/g, ''))
    .filter(heading => heading.length > 0);

  // Fetch related articles from the same category
  let relatedArticles: NewsItem[] = [];
  if (article.categories.length > 0) {
    try {
      const categoryName = article.categories[0].name;
      const relatedResponse = await getArticles({ limit: 5, category: categoryName, articleType: ArticleType.NEWS });
      // Filter out the current article and take up to 4
      relatedArticles = relatedResponse.items
        .filter(item => item.slug !== slug)
        .slice(0, 4)
        .map(mapArticleToNewsItem);
    } catch (error) {
      console.error('Failed to fetch related articles:', error);
    }
  }


  return (
    <div className="min-h-screen pb-12">
      <div className="w-full">

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-12">
          <div className="lg:col-span-8 mt-12">
            <header className="mb-4 lg:mb-8 border-b border-slate-200 pb-4 lg:pb-8">
              <div className="flex items-center gap-3 mb-4">
                {article.categories.map((category) => (
                  <span
                    key={category.id}
                    className="text-xs font-semibold text-indigo-700 uppercase tracking-wide"
                  >
                    {category.name}
                  </span>
                ))}
              </div>

              <h1 className="md:text-5xl text-slate-900 leading-tight mb-6 font-sans">
                {article.title}
              </h1>

              {article.excerpt && (
                <p className="text-xl text-slate-700 font-light border-l-2 border-indigo-500 pl-4">
                  {article.excerpt}
                </p>
              )}

              <div className="flex items-center justify-between mt-6">
                <span className="flex items-center gap-1.5 text-slate-500 text-sm">
                  <Clock className="w-4 h-4" />
                  {new Date(article.published_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </span>
                
                <button className="p-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors">
                  <Share2 className="w-4 h-4" />
                </button>
              </div>
            </header>

            {/* Mobile-only Sentiment Analysis - shown at the beginning on mobile */}
            <div className="lg:hidden mb-4">
              <SentimentAnalysis score={sentimentScore} />
            </div>

            {article.thumbnail && (
              <div className="relative aspect-video w-full rounded-xl overflow-hidden mb-10 border border-slate-200 shadow-sm bg-slate-100">
                <SmartImage
                  src={getThumbnailUrl(article.thumbnail, article.id)}
                  alt={article.title}
                  fill
                  priority
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
                />
              </div>
            )}

            <ArticleContent content={article.content} />

          </div>

          <div className="lg:col-span-4 mt-4 lg:mt-12">
            <div className="sticky top-32 space-y-6">
              {/* Table of Contents - hidden on mobile */}
              <div className="hidden lg:block">
                <TableOfContents headings={headings} />
              </div>

              {/* Sentiment Analysis - hidden on mobile (shown at beginning instead) */}
              <div className="hidden lg:block">
                <SentimentAnalysis score={sentimentScore} />
              </div>

              {/* Advertisement */}
              <AdPlaceholder width={250} height={250} />
            </div>
          </div>
        </div>

        {/* Related Articles Section */}
        {relatedArticles.length > 0 && (
          <div className="mt-16 pt-12 border-t border-slate-200">
            <h2 className="text-2xl font-bold text-slate-900 mb-8">More in {article.categories[0]?.name}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {relatedArticles.map((relatedArticle) => (
                <div key={relatedArticle.id} className="h-full">
                  <NewsCard item={relatedArticle} />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
