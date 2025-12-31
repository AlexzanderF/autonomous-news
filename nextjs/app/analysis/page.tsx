'use client';

import { useState, useEffect } from 'react';
import { Clock, ImageOff } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import { getThumbnailUrl } from '@/utils/thumbnails';
import { getArticles, ArticleType } from '@/services/article-service';
import { ArticleListItemDTO } from '@/dtos';
import AdSense from '@/components/AdSense';

const ARTICLES_PER_PAGE = 12;

export default function AnalysisListPage() {
  const [articles, setArticles] = useState<ArticleListItemDTO[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [loadingMore, setLoadingMore] = useState<boolean>(false);
  const [cursor, setCursor] = useState<number | null>(null);
  const [hasMore, setHasMore] = useState<boolean>(false);

  // Initial load
  useEffect(() => {
    const loadArticles = async () => {
      setLoading(true);
      try {
        const response = await getArticles({ limit: ARTICLES_PER_PAGE, articleType: ArticleType.EDITORIAL });
        setArticles(response.items);
        setCursor(response.next_cursor);
        setHasMore(response.has_more);
      } catch (error) {
        console.error("Failed to load articles:", error);
      } finally {
        setLoading(false);
      }
    };

    loadArticles();
  }, []);

  // Load more handler
  const loadMore = async () => {
    if (loadingMore || !hasMore || cursor === null) return;

    setLoadingMore(true);
    try {
      const response = await getArticles({ cursor, limit: ARTICLES_PER_PAGE, articleType: ArticleType.EDITORIAL });
      setArticles(prev => [...prev, ...response.items]);
      setCursor(response.next_cursor);
      setHasMore(response.has_more);
    } catch (error) {
      console.error("Failed to load more articles:", error);
    } finally {
      setLoadingMore(false);
    }
  };

  return (
    <main>
      <section className="w-full py-6 lg:py-12">
        <header className="mb-6 lg:mb-10">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            Financial Analysis
          </h1>
          <p className="text-lg text-slate-600">
            In-depth market analysis and investment outlooks (powered by AI and experts)
          </p>
        </header>

        {/* Main Content Grid with Sidebar */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-12">
          {/* Articles Area - Left Side */}
          <div className="lg:col-span-9">

            {loading ? (
              <div className="flex flex-col items-center justify-center gap-4 text-slate-600 py-12">
                <div className="w-px h-16 bg-gradient-to-b from-transparent via-slate-400 to-transparent"></div>
                <span className="text-[10px] font-mono tracking-widest opacity-70">LOADING...</span>
              </div>
            ) : articles.length > 0 ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {articles.map((article) => (
                    <Link
                      key={article.id}
                      href={`/analysis/${article.slug}`}
                      className="group flex flex-col h-full bg-white border border-slate-200 rounded-xl overflow-hidden hover:border-emerald-300 hover:shadow-lg transition-all duration-200"
                    >
                      {/* Thumbnail */}
                      <div className="relative aspect-[16/9] w-full bg-slate-100">
                        {article.thumbnail ? (
                          <Image
                            src={getThumbnailUrl(article.thumbnail)}
                            alt={article.title}
                            fill
                            className="object-cover transition-transform duration-300"
                            sizes="(max-width: 768px) 100vw, (max-width: 1280px) 50vw, 33vw"
                          />
                        ) : (
                          <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-slate-100 to-slate-200">
                            <ImageOff className="w-12 h-12 text-slate-300 mb-2" />
                            <span className="text-xs text-slate-400 font-mono">No image</span>
                          </div>
                        )}
                      </div>

                      {/* Content */}
                      <div className="p-6 flex flex-col flex-grow">
                        <div className="flex items-center gap-2 mb-3">
                          {article.categories?.slice(0, 2).map((category, index) => (
                            <span
                              key={index}
                              className="bg-emerald-100 text-emerald-700 border border-emerald-200 text-[10px] font-mono px-2 py-0.5 rounded uppercase tracking-wider"
                            >
                              {category.name}
                            </span>
                          ))}
                        </div>

                        <h2 className="text-xl font-semibold text-slate-900 group-hover:text-emerald-700 transition-colors mb-3 line-clamp-2">
                          {article.title}
                        </h2>

                        <div className="flex items-center gap-4 text-sm text-slate-500 mt-auto">
                          <span className="flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5" />
                            {new Date(article.published_at).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric'
                            })}
                          </span>
                        </div>
                      </div>
                    </Link>
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
                <p className="text-slate-500 text-lg">No analysis articles found.</p>
              </div>
            )}
          </div>

          {/* Sidebar - Right Side */}
          <div className="lg:col-span-3 mt-6 lg:mt-0">
            <div className="sticky top-32">
              <AdSense format="rectangle" />
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

