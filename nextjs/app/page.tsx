import Image from 'next/image';
import NewsCard from '@/components/NewsCard';
import AdPlaceholder from '@/components/AdPlaceholder';
import { getArticles, ArticleType } from '@/services/article-service';
import { mapArticleToNewsItem } from '@/utils/article-mapper';
import { getThumbnailUrl } from '@/utils/thumbnails';

// Force dynamic rendering to prevent API calls during build time
export const dynamic = 'force-dynamic';

export default async function Home() {
  // Fetch data on the server for SEO
  const [articlesResponse, analysisResponse] = await Promise.all([
    getArticles({ limit: 7, articleType: ArticleType.NEWS }), // Fetch 7 news articles (3 for hero + 4 for row)
    getArticles({ limit: 2, articleType: ArticleType.EDITORIAL }) // Fetch 2 editorial articles for analysis sections
  ]);
  
  const articles = articlesResponse.items.map(mapArticleToNewsItem);
  const analysisArticles = analysisResponse.items;


  return (
    <main>
      {/* Hero / Stats Section */}

      {/* Main Content Area */}
      <section className="w-full py-12">

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
                     className="object-cover object-top transition-transform duration-300"
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
                      className="object-cover object-top transition-transform duration-300"
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
                      className="object-cover object-top transition-transform duration-300"
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
              <div className="lg:col-span-3 flex flex-col">
                {/* Latest Analysis Header + Title */}
                <div className="border-t-2 border-emerald-500 pt-3">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wide">
                      Latest Analysis
                    </span>
                    {analysisArticles[0] && (
                      <span className="text-xs text-slate-400">
                        | {new Date(analysisArticles[0].published_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </span>
                    )}
                  </div>
                  {analysisArticles[0] ? (
                    <a href={`/analysis/${analysisArticles[0].slug}`} className="block group">
                      <h4 className="text-base font-bold text-slate-900 leading-snug group-hover:text-emerald-700 transition-colors mb-2">
                        {analysisArticles[0].title}
                      </h4>
                      <div className="flex flex-wrap gap-1">
                        {analysisArticles[0].categories?.slice(0, 2).map((category) => (
                          <span
                            key={category.id}
                            className="bg-emerald-100 text-emerald-700 border border-emerald-200 text-[10px] font-mono px-2 py-0.5 rounded uppercase tracking-wider"
                          >
                            {category.name}
                          </span>
                        ))}
                      </div>
                    </a>
                  ) : (
                    <p className="text-slate-400 text-sm">Loading...</p>
                  )}
                </div>

                {/* Thumbnail + Ad pushed to bottom */}
                <div className="mt-auto flex flex-col gap-4">
                  {analysisArticles[0]?.thumbnail && (
                    <a href={`/analysis/${analysisArticles[0].slug}`} className="block group">
                      <div className="relative aspect-[16/9] overflow-hidden rounded-lg">
                        <Image 
                          src={getThumbnailUrl(analysisArticles[0].thumbnail, analysisArticles[0].id)} 
                          alt={analysisArticles[0].title}
                          fill
                          className="object-cover transition-transform duration-300"
                        />
                      </div>
                    </a>
                  )}
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

          {/* View Latest News Link */}
          <div className="mt-8 pt-6 border-t border-slate-200">
            <a 
              href="/latest" 
              className="inline-flex items-center gap-2 text-indigo-700 hover:text-indigo-600 font-medium transition-colors group"
            >
              <span>View Latest News</span>
              <span className="group-hover:translate-x-1 transition-transform">→</span>
            </a>
          </div>
      </section>

      {/* Featured Analysis Section - Dark Background */}
      {analysisArticles[1] && (
        <section className="-mx-4 md:-mx-8 lg:-mx-12 px-4 md:px-8 lg:px-12 py-12 bg-slate-900">
          <a href={`/analysis/${analysisArticles[1].slug}`} className="block group">
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
                  {analysisArticles[1].title}
                </h2>
                
                {/* Excerpt/Subtitle */}
                {analysisArticles[1].excerpt && (
                  <p className="text-slate-400 text-lg leading-relaxed">
                    {analysisArticles[1].excerpt}
                  </p>
                )}
              </div>
              
              {/* Right Column - Thumbnail */}
              <div className="order-1 lg:order-2">
                {analysisArticles[1].thumbnail && (
                  <div className="relative aspect-[16/9] overflow-hidden rounded-lg">
                    <Image 
                      src={getThumbnailUrl(analysisArticles[1].thumbnail, analysisArticles[1].id)} 
                      alt={analysisArticles[1].title}
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
