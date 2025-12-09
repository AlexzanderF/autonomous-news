'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import NewsCard from '@/components/NewsCard';
import { RefreshCw } from 'lucide-react';
import { getArticles } from '@/services/article-service';
import { ArticleListItemDTO, NewsItem, NewsCategory } from '@/dtos';

function mapArticleToNewsItem(article: ArticleListItemDTO): NewsItem {
    // Category mapping (take first or default)
    let category = NewsCategory.TECH; // Default
    if (article.categories.length > 0) {
        const catName = article.categories[0].name.toUpperCase();
        // Simple mapping attempt
        if (catName.includes('TECH')) category = NewsCategory.TECH;
        else if (catName.includes('POLITIC') || catName.includes('GEO')) category = NewsCategory.GEOPOLITICS;
        else if (catName.includes('FINANCE') || catName.includes('ECONOMY')) category = NewsCategory.FINANCE;
        else if (catName.includes('ENV') || catName.includes('CLIMATE')) category = NewsCategory.ENVIRONMENT;
        else if (catName.includes('SPACE')) category = NewsCategory.SPACE;
    }

    return {
        id: article.id.toString(),
        slug: article.slug,
        headline: article.title,
        summary: article.excerpt || '',
        category: category,
        timestamp: article.published_at,
        imageUrl: article.thumbnail_url || `https://picsum.photos/800/600?random=${article.id}`,
        sentimentScore: article.sentiment_score
    };
}

export default function Home() {
  const [articles, setArticles] = useState<NewsItem[]>([]);
  const [cursor, setCursor] = useState<number | undefined>(undefined);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const loadingRef = useRef<boolean>(false);
  const observerTarget = useRef<HTMLDivElement>(null);
  const initialLoadDone = useRef(false);

  const loadArticles = useCallback(async (reset = false) => {
      if (loadingRef.current) return;
      if (!reset && !hasMore) return;

      setLoading(true);
      loadingRef.current = true;
      try {
          const currentCursor = reset ? undefined : cursor;
          const response = await getArticles(currentCursor, 12);
          
          const newNewsItems = response.items.map(mapArticleToNewsItem);
          
          if (reset) {
              setArticles(newNewsItems);
          } else {
              setArticles(prev => {
                  // Deduplicate just in case
                  const existingIds = new Set(prev.map(item => item.id));
                  const uniqueNewItems = newNewsItems.filter(item => !existingIds.has(item.id));
                  return [...prev, ...uniqueNewItems];
              });
          }
          
          setCursor(response.next_cursor ?? undefined);
          setHasMore(newNewsItems.length >= response.page_size);
      } catch (error) {
          console.error("Failed to load articles:", error);
      } finally {
          setLoading(false);
          loadingRef.current = false;
      }
  }, [cursor, hasMore]); // Removed loading from dependency since we use ref

  // Initial load
  useEffect(() => {
      if (!initialLoadDone.current) {
          loadArticles(true);
          initialLoadDone.current = true;
      }
  }, [loadArticles]);

  // Infinite scroll observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && hasMore && !loading) {
          loadArticles();
        }
      },
      { threshold: 0.1 } // Trigger when 10% of the sentinel is visible
    );

    const currentTarget = observerTarget.current;
    if (currentTarget) {
      observer.observe(currentTarget);
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [loadArticles, hasMore, loading]);


  const handleRefresh = () => {
      setCursor(undefined);
      setHasMore(true);
      loadArticles(true);
  };

  return (
    <main className="pt-16">
      {/* Hero / Stats Section */}
      {/* <GlobalPulse /> */}

      {/* Main Content Area */}
      <section className="max-w-7xl mx-auto px-6 py-8">
         <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
            <div className="flex items-end gap-4">
                <h2 className="text-2xl font-bold text-white">Latest News</h2>
            </div>
            
            <div className="flex items-center gap-3">
                <button 
                    onClick={handleRefresh}
                    className="p-2 bg-slate-900 border border-slate-800 rounded hover:border-cyan-500/50 hover:text-cyan-400 transition-colors text-slate-400"
                >
                    <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </div>
         </div>

         {/* Masonry Grid Simulation */}
         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map((news) => (
                <div key={news.id} className="h-full">
                    <NewsCard item={news} />
                </div>
            ))}
         </div>
         
         {/* Feed End / Loading Sentinel */}
         <div 
            ref={observerTarget}
            className="mt-16 mb-12 flex flex-col items-center justify-center gap-4 text-slate-600 h-20"
         >
             {loading && (
                 <>
                    <div className="w-px h-16 bg-gradient-to-b from-transparent via-slate-800 to-transparent"></div>
                    <span className="text-[10px] font-mono tracking-widest opacity-50">LOADING ARTICLES...</span>
                 </>
             )}
             {!hasMore && articles.length > 0 && (
                 <span className="text-[10px] font-mono tracking-widest opacity-30">END OF STREAM</span>
             )}
         </div>
      </section>
    </main>
  );
}
