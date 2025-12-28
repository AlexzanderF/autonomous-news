'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import NewsCard from '@/components/NewsCard';
import AdPlaceholder from '@/components/AdPlaceholder';
import { getArticles } from '@/services/article-service';
import { NewsItem } from '@/dtos';
import { mapArticleToNewsItem } from '@/utils/article-mapper';

const ARTICLES_PER_PAGE = 12;

// Map URL slugs to category names and display titles
const topicConfig: Record<string, { categoryName: string; displayTitle: string }> = {
  'economy': { categoryName: 'Markets & Economy', displayTitle: 'Markets & Economy' },
  'crypto': { categoryName: 'Crypto', displayTitle: 'Cryptocurrency' },
  'ai': { categoryName: 'AI', displayTitle: 'Artificial Intelligence' },
  'politics': { categoryName: 'Politics', displayTitle: 'Politics' },
  'tech': { categoryName: 'Tech', displayTitle: 'Technology' },
  'science': { categoryName: 'Science', displayTitle: 'Science' },
  'environment': { categoryName: 'Environment', displayTitle: 'Environment' },
};

export default function TopicPage() {
  const params = useParams();
  const slug = params.slug as string;
  
  const [articles, setArticles] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [loadingMore, setLoadingMore] = useState<boolean>(false);
  const [cursor, setCursor] = useState<number | null>(null);
  const [hasMore, setHasMore] = useState<boolean>(false);

  const config = topicConfig[slug] || { 
    categoryName: slug, 
    displayTitle: slug.charAt(0).toUpperCase() + slug.slice(1) 
  };

  // Initial load
  useEffect(() => {
    const loadArticles = async () => {
      setLoading(true);
      setArticles([]);
      setCursor(null);
      try {
        const response = await getArticles(undefined, ARTICLES_PER_PAGE, config.categoryName);
        setArticles(response.items.map(mapArticleToNewsItem));
        setCursor(response.next_cursor);
        setHasMore(response.has_more);
      } catch (error) {
        console.error("Failed to load articles:", error);
      } finally {
        setLoading(false);
      }
    };
    
    loadArticles();
  }, [config.categoryName]);

  // Load more handler
  const loadMore = async () => {
    if (loadingMore || !hasMore || cursor === null) return;
    
    setLoadingMore(true);
    try {
      const response = await getArticles(cursor, ARTICLES_PER_PAGE, config.categoryName);
      setArticles(prev => [...prev, ...response.items.map(mapArticleToNewsItem)]);
      setCursor(response.next_cursor);
      setHasMore(response.has_more);
    } catch (error) {
      console.error("Failed to load more articles:", error);
    } finally {
      setLoadingMore(false);
    }
  };

  return (
    <main className="pt-28 pb-12">
      <div className="w-full py-12">
        {/* Page Header */}
        <header className="mb-10">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            {config.displayTitle}
          </h1>
          <p className="text-lg text-slate-600">
            Latest news and updates in {config.displayTitle.toLowerCase()}
          </p>
        </header>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Articles Grid - Left Side */}
          <div className="lg:col-span-9 lg:border-r lg:border-slate-200 lg:pr-8">
            {loading ? (
              <div className="flex flex-col items-center justify-center gap-4 text-slate-600 py-12">
                <div className="w-px h-16 bg-gradient-to-b from-transparent via-slate-400 to-transparent"></div>
                <span className="text-[10px] font-mono tracking-widest opacity-70">LOADING...</span>
              </div>
            ) : articles.length > 0 ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {articles.map((article) => (
                    <div key={article.id} className="h-full">
                      <NewsCard item={article} />
                    </div>
                  ))}
                </div>
                
                {/* Load More Button */}
                {hasMore && (
                  <div className="mt-10 flex justify-center">
                    <button
                      onClick={loadMore}
                      disabled={loadingMore}
                      className="px-8 py-3 bg-slate-900 text-white font-medium rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {loadingMore ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                          <span>Loading...</span>
                        </>
                      ) : (
                        <span>Load More</span>
                      )}
                    </button>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-12">
                <p className="text-slate-500 text-lg">No articles found in this category.</p>
              </div>
            )}
          </div>

          {/* Sidebar - Right Side */}
          <div className="lg:col-span-3">
            <div className="sticky top-32">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest mb-4 block">
                Advertisement
              </span>
              <AdPlaceholder width={250} height={600} />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

