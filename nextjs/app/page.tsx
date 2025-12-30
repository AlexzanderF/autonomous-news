import Image from 'next/image';
import NewsCard from '@/components/NewsCard';

import { getArticles, ArticleType } from '@/services/article-service';
import { mapArticleToNewsItem } from '@/utils/article-mapper';
import { getThumbnailUrl } from '@/utils/thumbnails';

// Force dynamic rendering to prevent API calls during build time
export const dynamic = 'force-dynamic';

export default async function Home() {
  // Fetch featured articles, editorial articles, and featured editorial in parallel
  const [featuredResponse, analysisResponse, featuredAnalysisResponse] = await Promise.all([
    getArticles({ limit: 7, articleType: ArticleType.NEWS, isFeatured: true }), // Try to get 7 featured news articles
    getArticles({ limit: 2, articleType: ArticleType.EDITORIAL, isFeatured: false }), // Fetch 2 non-featured editorial articles for sidebar
    getArticles({ limit: 1, articleType: ArticleType.EDITORIAL, isFeatured: true }) // Fetch 1 featured editorial for hero section
  ]);
  
  let newsArticles = featuredResponse.items;
  
  // If we have fewer than 7 featured articles, fill the rest with newest non-featured articles
  if (newsArticles.length < 7) {
    const neededCount = 7 - newsArticles.length;
    const featuredIds = new Set(newsArticles.map(a => a.id));
    
    const newestResponse = await getArticles({ 
      limit: neededCount + 5, // Fetch extra in case some overlap
      articleType: ArticleType.NEWS,
      isFeatured: false 
    });
    
    // Add non-featured articles that aren't already in our list
    const additionalArticles = newestResponse.items
      .filter(a => !featuredIds.has(a.id))
      .slice(0, neededCount);
    
    newsArticles = [...newsArticles, ...additionalArticles];
  }
  
  const articles = newsArticles.map(mapArticleToNewsItem);
  const analysisArticles = analysisResponse.items;
  // Use featured editorial if available, otherwise fall back to first analysis article
  const featuredAnalysisArticle = featuredAnalysisResponse.items[0] || analysisArticles[0];


  return (
    <main>
      {/* Hero / Stats Section */}

      {/* Main Content Area */}
      <section className="w-full py-12">

         {/* Hero Section - 3 Column Layout */}
         {articles.length >= 3 && (
           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-4 pb-8 mb-8 border-b border-slate-300">
              {/* Left Column - 2 Stacked Articles */}
              <div className="lg:col-span-4 flex flex-col gap-6 lg:border-r lg:border-slate-300 lg:pr-6">
                {/* First stacked article with image */}
                <a href={`/article/${articles[1].slug}`} className="block group">
                  <div className="relative aspect-[2/1] mb-3 overflow-hidden">
                    <Image 
                      src={articles[1].imageUrl || '/placeholder-news.jpg'} 
                      alt={articles[1].headline}
                      fill
                      sizes="(max-width: 768px) 100vw, 50vw"
                      className="object-cover object-top transition-transform duration-300"
                    />
                  </div>
                  <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wide">
                    {articles[1].category}
                  </span>
                  <h3 className="text-2xl font-bold text-slate-900 mt-1 mb-2 leading-tight group-hover:text-indigo-700 transition-colors">
                    {articles[1].headline}
                  </h3>
                </a>

                {/* Second stacked article with image */}
                <a href={`/article/${articles[2].slug}`} className="block group">
                  <div className="relative aspect-[2/1] mb-3 overflow-hidden">
                    <Image 
                      src={articles[2].imageUrl || '/placeholder-news.jpg'} 
                      alt={articles[2].headline}
                      fill
                      sizes="(max-width: 768px) 100vw, 50vw"
                      className="object-cover object-top transition-transform duration-300"
                    />
                  </div>
                  <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wide">
                    {articles[2].category}
                  </span>
                  <h3 className="text-2xl font-bold text-slate-900 mt-1 mb-2 leading-tight group-hover:text-indigo-700 transition-colors">
                    {articles[2].headline}
                  </h3>
                </a>
              </div>

              {/* Middle Column - Main Featured Article */}
              <div className="lg:col-span-5 lg:border-r lg:border-slate-300 lg:pr-6">
                <a href={`/article/${articles[0].slug}`} className="block group">
                  <div className="relative aspect-[16/10] mb-3 overflow-hidden">
                    <Image 
                      src={articles[0].imageUrl || '/placeholder-news.jpg'} 
                      alt={articles[0].headline}
                      fill
                      sizes="(max-width: 768px) 100vw, 50vw"
                      className="object-cover object-top transition-transform duration-300"
                    />
                  </div>
                  <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wide">
                    {articles[0].category}
                  </span>
                  <h2 className="text-4xl font-bold text-slate-900 mt-2 mb-3 leading-tight group-hover:text-indigo-700 transition-colors">
                    {articles[0].headline}
                  </h2>
                  <p className="text-slate-600 text-sm leading-relaxed line-clamp-3">
                    {articles[0].summary}
                  </p>
                </a>
              </div>

               {/* Right Column - Latest Analysis */}
               <div className="lg:col-span-3">
                 {/* Latest Analysis Header */}
                 <div className="border-t-2 border-emerald-500 pt-3">
                   <div className="flex items-center gap-2 mb-3">
                     <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wide">
                       Latest Analysis
                     </span>
                   </div>
                   {/* Show 3 Latest Analysis Articles */}
                   <div className="flex flex-col">
                     {analysisArticles.slice(0, 2).map((article, index) => (
                       <div key={article.id}>
                         <a href={`/analysis/${article.slug}`} className="block group py-3">
                           {article.thumbnail && (
                             <div className="relative aspect-[16/9] overflow-hidden rounded-lg mb-2">
                               <Image 
                                 src={getThumbnailUrl(article.thumbnail, article.id)} 
                                 alt={article.title}
                                 fill
                                 className="object-cover transition-transform duration-300"
                               />
                             </div>
                           )}
                           <h4 className="text-base font-bold text-slate-900 leading-snug group-hover:text-emerald-700 transition-colors mb-1">
                             {article.title}
                           </h4>
                           <div className="flex items-center gap-2">
                             <span className="text-xs text-slate-400">
                               {new Date(article.published_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                             </span>
                             {article.categories?.slice(0, 1).map((category) => (
                               <span
                                 key={category.id}
                                 className="bg-emerald-100 text-emerald-700 border border-emerald-200 text-[10px] font-mono px-2 py-0.5 rounded uppercase tracking-wider"
                               >
                                 {category.name}
                               </span>
                             ))}
                           </div>
                         </a>
                         {index < 1 && (
                           <div className="border-b border-slate-300 mt-3" />
                         )}
                       </div>
                     ))}
                     {analysisArticles.length === 0 && (
                       <p className="text-slate-400 text-sm py-3">No analysis available</p>
                     )}
                   </div>
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

      </section>

      {/* Featured Analysis Section - Dark Background */}
      {featuredAnalysisArticle && (
        <section className="-mx-4 md:-mx-8 lg:-mx-12 px-4 md:px-8 lg:px-12 py-12 bg-slate-900">
          <a href={`/analysis/${featuredAnalysisArticle.slug}`} className="block group">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              {/* Left Column - Text Content */}
              <div className="order-2 lg:order-1">
                {/* Featured Analysis Badge */}
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-1 h-6 bg-emerald-500 rounded-full"></div>
                  <span className="text-xs font-semibold text-emerald-400 uppercase tracking-widest">
                    Featured Analysis
                  </span>
                </div>
                
                {/* Title */}
                <h2 className="text-3xl md:text-4xl font-bold text-white leading-tight mt-3 mb-4 group-hover:text-emerald-400 transition-colors">
                  {featuredAnalysisArticle.title}
                </h2>
                
                {/* Excerpt/Subtitle */}
                {featuredAnalysisArticle.excerpt && (
                  <p className="text-slate-400 text-lg leading-relaxed">
                    {featuredAnalysisArticle.excerpt}
                  </p>
                )}
              </div>
              
              {/* Right Column - Thumbnail */}
              <div className="order-1 lg:order-2">
                {featuredAnalysisArticle.thumbnail && (
                  <div className="relative aspect-[16/9] overflow-hidden rounded-lg">
                    <Image 
                      src={getThumbnailUrl(featuredAnalysisArticle.thumbnail, featuredAnalysisArticle.id)} 
                      alt={featuredAnalysisArticle.title}
                      fill
                      className="object-cover transition-transform duration-300"
                    />
                  </div>
                )}
              </div>
            </div>
          </a>
          
          {/* View All Analysis Link */}
          <div className="mt-8 pt-6 border-t border-slate-700">
            <a 
              href="/analysis" 
              className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 font-medium transition-colors group"
            >
              <span>View All Analysis</span>
              <span className="group-hover:translate-x-1 transition-transform">→</span>
            </a>
          </div>
        </section>
      )}

    </main>
  );
}
