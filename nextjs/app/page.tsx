'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import NewsCard from '@/components/NewsCard';
import AdPlaceholder from '@/components/AdPlaceholder';
import { getArticles } from '@/services/article-service';
import { getFinancialAnalysisArticles } from '@/services/financial-analysis-service';
import { ArticleListItemDTO, NewsItem, FinancialAnalysisArticle } from '@/dtos';
import { getThumbnailUrl } from '@/utils/thumbnails';

function mapArticleToNewsItem(article: ArticleListItemDTO): NewsItem {
    return {
        id: article.id.toString(),
        slug: article.slug,
        headline: article.title,
        summary: article.excerpt || '',
        category: article.categories.length > 0 ? article.categories[0].name : 'Tech',
        timestamp: article.published_at,
        imageUrl: getThumbnailUrl(article.thumbnail, article.id),
        sentimentScore: article.sentiment_score
    };
}

export default function Home() {
  const [articles, setArticles] = useState<NewsItem[]>([]);
  const [latestAnalysis, setLatestAnalysis] = useState<FinancialAnalysisArticle | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      try {
        const [articlesResponse, analysisArticles] = await Promise.all([
          getArticles(undefined, 7), // Fetch 7 articles (3 for hero + 4 for row)
          getFinancialAnalysisArticles()
        ]);
        
        setArticles(articlesResponse.items.map(mapArticleToNewsItem));
        if (analysisArticles.length > 0) {
          setLatestAnalysis(analysisArticles[0]);
        }
      } catch (error) {
        console.error("Failed to load data:", error);
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, []);


  return (
    <main className="pt-20">
      {/* Hero / Stats Section */}

      {/* Main Content Area */}
      <section className="w-full px-4 md:px-8 lg:px-12 py-12">

         {/* Hero Section - 3 Column Layout */}
         {articles.length >= 3 && (
           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-4 pb-8 mb-8 border-b border-slate-200">
             {/* Left Column - Main Featured Article */}
             <div className="lg:col-span-5 lg:border-r lg:border-slate-200 lg:pr-6">
               <a href={`/article/${articles[0].slug}`} className="block group">
                 <div className="relative aspect-[16/10] mb-3 overflow-hidden">
                   <Image 
                     src={articles[0].imageUrl || '/placeholder-news.jpg'} 
                     alt={articles[0].headline}
                     fill
                      sizes="(max-width: 768px) 100vw, 50vw"
                      className="object-cover transition-transform duration-300 group-hover:scale-105"
                   />
                 </div>
                 <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wide">
                   {articles[0].category}
                 </span>
                 <h2 className="text-2xl font-bold text-slate-900 mt-2 mb-3 leading-tight group-hover:text-indigo-700 transition-colors">
                   {articles[0].headline}
                 </h2>
                 <p className="text-slate-600 text-sm leading-relaxed line-clamp-3">
                   {articles[0].summary}
                 </p>
               </a>
             </div>

             {/* Middle Column - 2 Stacked Articles */}
             <div className="lg:col-span-4 flex flex-col gap-6 lg:border-r lg:border-slate-200 lg:pr-6">
               {/* First middle article with image */}
               <a href={`/article/${articles[1].slug}`} className="block group">
                 <div className="relative aspect-[2/1] mb-3 overflow-hidden">
                   <Image 
                     src={articles[1].imageUrl || '/placeholder-news.jpg'} 
                     alt={articles[1].headline}
                     fill
                      sizes="(max-width: 768px) 100vw, 50vw"
                      className="object-cover transition-transform duration-300 group-hover:scale-105"
                   />
                 </div>
                 <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wide">
                   {articles[1].category}
                 </span>
                 <h3 className="text-lg font-bold text-slate-900 mt-1 mb-2 leading-tight group-hover:text-indigo-700 transition-colors">
                   {articles[1].headline}
                 </h3>
               </a>

               {/* Second middle article with image */}
               <a href={`/article/${articles[2].slug}`} className="block group">
                 <div className="relative aspect-[2/1] mb-3 overflow-hidden">
                   <Image 
                     src={articles[2].imageUrl || '/placeholder-news.jpg'} 
                     alt={articles[2].headline}
                     fill
                      sizes="(max-width: 768px) 100vw, 50vw"
                      className="object-cover transition-transform duration-300 group-hover:scale-105"
                   />
                 </div>
                 <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wide">
                   {articles[2].category}
                 </span>
                 <h3 className="text-lg font-bold text-slate-900 mt-1 mb-2 leading-tight group-hover:text-indigo-700 transition-colors">
                   {articles[2].headline}
                 </h3>
               </a>
             </div>

              {/* Right Column - Latest Analysis + Ad */}
              <div className="lg:col-span-3 flex flex-col gap-4">
                {/* Latest Analysis Section */}
                <div className="border-t-2 border-emerald-500 pt-3">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wide">
                      Latest Analysis
                    </span>
                    {latestAnalysis && (
                      <span className="text-xs text-slate-400">
                        | {new Date(latestAnalysis.published_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </span>
                    )}
                  </div>
                  {latestAnalysis ? (
                    <a href={`/analysis/${latestAnalysis.slug}`} className="block group">
                      <h4 className="text-base font-bold text-slate-900 leading-snug group-hover:text-emerald-700 transition-colors mb-2">
                        {latestAnalysis.title}
                      </h4>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {latestAnalysis.tags?.slice(0, 2).map((tag, index) => (
                          <span
                            key={index}
                            className="bg-emerald-100 text-emerald-700 border border-emerald-200 text-[10px] font-mono px-2 py-0.5 rounded uppercase tracking-wider"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </a>
                  ) : (
                    <p className="text-slate-400 text-sm">Loading...</p>
                  )}
                </div>

                {/* Advertisement */}
                <div className="mt-auto">
                  <AdPlaceholder />
                </div>
              </div>
           </div>
         )}

         {/* Row of 4 News Cards */}
         {articles.length >= 7 && (
           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
             {articles.slice(3, 7).map((article) => (
               <div key={article.id} className="h-full">
                 <NewsCard item={article} />
               </div>
             ))}
           </div>
         )}

         {/* Loading State */}
         {loading && (
           <div className="flex flex-col items-center justify-center gap-4 text-slate-600 py-12">
             <div className="w-px h-16 bg-gradient-to-b from-transparent via-slate-400 to-transparent"></div>
             <span className="text-[10px] font-mono tracking-widest opacity-70">LOADING...</span>
           </div>
         )}
      </section>
    </main>
  );
}
