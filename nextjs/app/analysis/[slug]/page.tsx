import { notFound } from 'next/navigation';
import { getFinancialAnalysisBySlug } from '@/services/financial-analysis-service';
import { Clock, User } from 'lucide-react';
import TableOfContents from '@/components/TableOfContents';
import AdPlaceholder from '@/components/AdPlaceholder';
import ArticleContent from '@/components/ArticleContent';

interface AnalysisPageProps {
  params: Promise<{ slug: string }>;
}

export default async function AnalysisPage({ params }: AnalysisPageProps) {
  const { slug } = await params;
  const article = await getFinancialAnalysisBySlug(slug);

  if (!article) {
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

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          <div className="lg:col-span-8 mt-12">
            <header className="mb-8 border-b border-slate-200 pb-8">
              <div className="flex items-center gap-3 mb-4">
                {article.tags?.map((tag, index) => (
                  <span
                    key={index}
                    className="bg-emerald-100 text-emerald-700 border border-emerald-200 text-[10px] font-mono px-2 py-1 rounded uppercase tracking-wider"
                  >
                    {tag}
                  </span>
                ))}
                <span className="flex items-center gap-1 text-slate-600 text-xs font-mono">
                  <Clock className="w-3 h-3" />
                  {new Date(article.published_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </span>
              </div>

              <h1 className="md:text-5xl text-slate-900 leading-tight mb-6 font-sans">
                {article.title}
              </h1>

              {article.author && (
                <div className="flex items-center gap-3 mt-6">
                  <div className="w-10 h-10 rounded-full bg-emerald-100 border-2 border-emerald-200 flex items-center justify-center">
                    <User className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <span className="text-slate-900 font-medium block">
                      {article.author}
                    </span>
                    <span className="text-slate-500 text-sm">
                      Financial Analyst
                    </span>
                  </div>
                </div>
              )}
            </header>

            <ArticleContent content={article.content} />

          </div>

          <div className="lg:col-span-4 mt-12">
            <div className="sticky top-32 space-y-6">
              {/* Table of Contents */}
              <TableOfContents headings={headings} />

              {/* Advertisement */}
              {/* <AdPlaceholder width={250} height={600} /> */}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
