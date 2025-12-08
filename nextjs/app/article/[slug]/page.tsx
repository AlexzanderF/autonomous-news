import { notFound } from 'next/navigation';
import { getArticleBySlug } from '@/services/article-service';
import { ArrowLeft, Share2, Clock } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import ReactMarkdown from 'react-markdown';
import TableOfContents from '@/components/TableOfContents';

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
  const widthPercentage = Math.abs(sentimentScore - 50);

  // Extract section headings from markdown for table of contents
  // Looking for lines that start with ### (h3 headers) which are section titles
  const headings = article.content
    .split('\n')
    .filter(line => line.trim().startsWith('### '))
    .map(line => line.trim().replace(/^(### )|(\*\*)/g, ''))
    .filter(heading => heading.length > 0);


  return (
    <div className="min-h-screen bg-slate-950 pt-20 pb-12 px-4 md:px-8">
      <div className="max-w-7xl mx-auto">
        <Link
          href="/"
          className="group flex items-center gap-2 text-slate-400 hover:text-cyan-400 transition-colors mb-8 font-mono text-sm inline-flex"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          <span>RETURN TO FEED</span>
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          <div className="lg:col-span-8">
            <header className="mb-8 border-b border-slate-800 pb-8">
              <div className="flex items-center gap-3 mb-4">
                {article.categories.map((category) => (
                  <span
                    key={category.id}
                    className="bg-cyan-950/30 text-cyan-400 border border-cyan-900/50 text-[10px] font-mono px-2 py-1 rounded uppercase tracking-wider"
                  >
                    {category.name}
                  </span>
                ))}
                <span className="flex items-center gap-1 text-slate-400 text-xs font-mono">
                  <Clock className="w-3 h-3" />
                  {new Date(article.published_at).toLocaleTimeString()}
                </span>
              </div>

              <h1 className="md:text-5xl text-slate-100 leading-tight mb-6 font-sans">
                {article.title}
              </h1>

              {article.excerpt && (
                <p className="text-xl text-gray-300 font-light border-l-2 border-blue-500 pl-4">
                  {article.excerpt}
                </p>
              )}

              <div className="flex items-center justify-between mt-6">
                <div className="flex items-center gap-4">
                  <div className="flex -space-x-2">
                    {[1, 2, 3].map((i) => (
                      <div
                        key={i}
                        className="w-8 h-8 rounded-full bg-slate-800 border-2 border-slate-950 flex items-center justify-center text-[10px] text-slate-400"
                      >
                        AF
                      </div>
                    ))}
                  </div>
                  <span className="text-slate-400 text-sm">
                    Synthesized by Gemini
                  </span>
                </div>
                <div className="flex gap-2">
                  <button className="p-2 rounded-full bg-slate-900 hover:bg-slate-800 text-slate-400 transition-colors">
                    <Share2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </header>

            {article.thumbnail_url && (
              <div className="relative aspect-video w-full rounded-xl overflow-hidden mb-10 border border-slate-800">
                <Image
                  src={article.thumbnail_url}
                  alt={article.title}
                  fill
                  className="object-cover opacity-80"
                  priority
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent" />
              </div>
            )}

            <article className="max-w-none">
              <div className="article-content text-slate-200 leading-relaxed">
                <ReactMarkdown
                  components={{
                    h3: ({ node: _node, ...props }) => <h2 className="font-bold text-slate-100 mt-6 mb-6" {...props} />,
                    p: ({ node: _node, ...props }) => <p className="mt-4" {...props} />
                  }}
                >
                  {article.content}
                </ReactMarkdown>
              </div>
            </article>

          </div>

          <div className="lg:col-span-4">
            <div className="sticky top-24 space-y-6">
              {/* Table of Contents */}
              <TableOfContents headings={headings} />

              {/* Sentiment Analysis */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 backdrop-blur-sm">
                <div className="flex items-center gap-2 text-slate-400 mb-4">
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                  </svg>
                  <span className="font-mono font-bold tracking-wider text-sm uppercase">AI Sentiment Analysis</span>
                </div>

                <div className="mb-2">
                  <div className="flex justify-between text-xs text-slate-400 mb-2 font-mono w-full px-1">
                    <span>Negative</span>
                    <span>Serious</span>
                    <span>Neutral</span>
                    <span>Optimistic</span>
                    <span>Positive</span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden relative">
                    <div
                      className="absolute top-0 h-full overflow-hidden rounded-full"
                      style={{
                        left: sentimentScore > 50 ? '50%' : `${50 - widthPercentage}%`,
                        width: `${widthPercentage}%`,
                      }}
                    >
                      <div
                        className={`absolute top-0 h-full ${sentimentScore > 50
                          ? 'left-0 bg-gradient-to-r from-slate-500 to-green-500'
                          : 'right-0 bg-gradient-to-r from-red-500 to-slate-500'
                          }`}
                        style={{
                          width: widthPercentage > 0 ? `${(50 / widthPercentage) * 100}%` : '0px',
                        }}
                      />
                    </div>
                  </div>
                </div>

                <div className="flex justify-between items-center mt-2 px-1">
                  <span className="text-xs font-mono text-slate-600 font-bold">0</span>
                  <div className="text-center font-mono text-l font-bold text-slate-200">
                    {sentimentScore}
                  </div>
                  <span className="text-xs font-mono text-slate-600 font-bold">100</span>
                </div>

                <div className="mt-4 pt-4 border-t border-slate-800">
                  <p className="text-[10px] text-slate-600 font-mono leading-relaxed uppercase">
                    Reflects the overall direction and mood of the article.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
