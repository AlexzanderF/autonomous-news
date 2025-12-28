'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import NewsCard from '@/components/NewsCard';
import AdPlaceholder from '@/components/AdPlaceholder';
import { getArticles } from '@/services/article-service';
import { ArticleListItemDTO, NewsItem, NewsCategory } from '@/dtos';
import { getThumbnailUrl } from '@/utils/thumbnails';

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
        imageUrl: getThumbnailUrl(article.thumbnail, article.id),
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


  return (
    <main className="pt-28">
      {/* Hero / Stats Section */}

      {/* Main Content Area */}
      <section className="max-w-7xl mx-auto px-4 md:px-6 py-12">
         <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
            <div className="flex items-end gap-4">
                <h2 className="text-2xl font-bold text-slate-900">Latest News</h2>
            </div>
         </div>

         {/* Masonry Grid Simulation */}
         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {(() => {
              const elements: React.ReactNode[] = [];
              let articleIndex = 0;
              let rowIndex = 0;

              // First article is always feature (full width)
              if (articles.length > 0) {
                elements.push(
                  <div key={articles[0].id} className="md:col-span-2 lg:col-span-3 h-full">
                    <NewsCard item={articles[0]} isFeature={true} />
                  </div>
                );
                articleIndex = 1;
                rowIndex = 1;
              }

              // Process remaining articles in alternating row pattern
              let adRowCount = 0; // Track ad row count for alternating positions
              while (articleIndex < articles.length) {
                const isAdRow = rowIndex % 2 === 0; // Every second row after feature

                if (isAdRow) {
                  // Ad row: 1 article (2 cols) + 1 ad placeholder (1 col)
                  // Alternate: odd adRowCount = ad left, even = ad right
                  const adOnLeft = adRowCount % 2 === 0;
                  
                  if (articleIndex < articles.length) {
                    const article = articles[articleIndex];
                    
                    if (adOnLeft) {
                      // Ad first (left), then article (right)
                      elements.push(
                        <div key={`ad-${rowIndex}`} className="h-full">
                          <AdPlaceholder />
                        </div>
                      );
                      elements.push(
                        <div key={article.id} className="md:col-span-2 lg:col-span-2 h-full">
                          <NewsCard item={article} isFeature={true} />
                        </div>
                      );
                    } else {
                      // Article first (left), then ad (right)
                      elements.push(
                        <div key={article.id} className="md:col-span-2 lg:col-span-2 h-full">
                          <NewsCard item={article} isFeature={true} />
                        </div>
                      );
                      elements.push(
                        <div key={`ad-${rowIndex}`} className="h-full">
                          <AdPlaceholder />
                        </div>
                      );
                    }
                    articleIndex++;
                  }
                  adRowCount++;
                } else {
                  // Normal row: 3 articles (1 col each)
                  for (let i = 0; i < 3 && articleIndex < articles.length; i++) {
                    const article = articles[articleIndex];
                    elements.push(
                      <div key={article.id} className="h-full">
                        <NewsCard item={article} />
                      </div>
                    );
                    articleIndex++;
                  }
                }
                rowIndex++;
              }

              return elements;
            })()}
         </div>
         
         {/* Feed End / Loading Sentinel */}
         <div 
            ref={observerTarget}
            className="mt-16 mb-12 flex flex-col items-center justify-center gap-4 text-slate-600 h-20"
         >
             {loading && (
                 <>
                    <div className="w-px h-16 bg-gradient-to-b from-transparent via-slate-400 to-transparent"></div>
                    <span className="text-[10px] font-mono tracking-widest opacity-70">LOADING ARTICLES...</span>
                 </>
             )}
             {!hasMore && articles.length > 0 && (
                 <span className="text-[10px] font-mono tracking-widest opacity-50">END OF STREAM</span>
             )}
         </div>
      </section>
    </main>
  );
}
