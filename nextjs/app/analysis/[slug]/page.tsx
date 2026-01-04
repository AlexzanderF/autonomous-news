import { notFound } from 'next/navigation';
import { getArticleBySlug, ArticleType } from '@/services/article-service';
import { Clock, Share2 } from 'lucide-react';
import SmartImage from '@/components/SmartImage';
import TableOfContents from '@/components/TableOfContents';
import ArticleContent from '@/components/ArticleContent';
import AdSense from '@/components/AdSense';
import ImageAttribution from '@/components/ImageAttribution';
import { getThumbnailUrl } from '@/utils/thumbnails';

// Force dynamic rendering to prevent API calls during build time
export const dynamic = 'force-dynamic';

interface AnalysisPageProps {
  params: Promise<{ slug: string }>;
}

export default async function AnalysisPage({ params }: AnalysisPageProps) {
  const { slug } = await params;
  let article;

  try {
    // Fetch only editorial articles for the analysis page
    article = await getArticleBySlug(slug, ArticleType.EDITORIAL);
  } catch {
    notFound();
  }

  // Extract section headings from markdown for table of contents
  // Looking for lines that start with ### (h3 headers) which are section titles
  const headings = article.content
    .split('\n')
    .filter(line => line.trim().startsWith('### '))
    .map(line => line.trim().replace(/^(### )|(\*\*)/g, ''))
    .filter(heading => heading.length > 0);

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
                    className="bg-emerald-100 text-emerald-700 border border-emerald-200 text-[10px] font-mono px-2 py-1 rounded uppercase tracking-wider"
                  >
                    {category.name}
                  </span>
                ))}
              </div>

              <h1 className="md:text-5xl text-slate-900 leading-tight mb-6 font-sans">
                {article.title}
              </h1>

              {article.excerpt && (
                <p className="text-xl text-slate-700 font-light border-l-2 border-emerald-500 pl-4">
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

            {article.thumbnail && (
              <figure className="relative w-full mb-10">
                <div className="relative aspect-video w-full overflow-hidden border border-slate-200 shadow-sm bg-slate-100">
                  <SmartImage
                    src={getThumbnailUrl(article.thumbnail, article.id)}
                    alt={article.title}
                    fill
                    priority
                    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
                  />
                </div>
                <ImageAttribution attribution={article.thumbnail_attribution} className="mt-2" />
              </figure>
            )}

            <ArticleContent content={article.content} />

          </div>

          <div className="lg:col-span-4 mt-4 lg:mt-12">
            <div className="sticky top-32 space-y-6">
              {/* Table of Contents - hidden on mobile */}
              <div className="hidden lg:block">
                <TableOfContents headings={headings} />
              </div>

              {/* Advertisement */}
              <AdSense format="rectangle" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
