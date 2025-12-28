import { notFound } from 'next/navigation';
import { getArticleBySlug } from '@/services/article-service';
import { ArrowLeft, Share2, Clock } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import ReactMarkdown from 'react-markdown';
import TableOfContents from '@/components/TableOfContents';
import AdPlaceholder from '@/components/AdPlaceholder';
import SentimentAnalysis from '@/components/SentimentAnalysis';
import { getThumbnailUrl } from '@/utils/thumbnails';

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

  // Extract section headings from markdown for table of contents
  // Looking for lines that start with ### (h3 headers) which are section titles
  const headings = article.content
    .split('\n')
    .filter(line => line.trim().startsWith('### '))
    .map(line => line.trim().replace(/^(### )|(\*\*)/g, ''))
    .filter(heading => heading.length > 0);


  return (
    <div className="min-h-screen pt-28 pb-12">
      <div className="max-w-7xl mx-auto px-4 md:px-6">

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          <div className="lg:col-span-8 mt-12">
            <header className="mb-8 border-b border-slate-200 pb-8">
              <div className="flex items-center gap-3 mb-4">
                {article.categories.map((category) => (
                  <span
                    key={category.id}
                    className="bg-indigo-100 text-indigo-700 border border-indigo-200 text-[10px] font-mono px-2 py-1 rounded uppercase tracking-wider"
                  >
                    {category.name}
                  </span>
                ))}
                <span className="flex items-center gap-1 text-slate-600 text-xs font-mono">
                  <Clock className="w-3 h-3" />
                  {new Date(article.published_at).toLocaleTimeString()}
                </span>
              </div>

              <h1 className="md:text-5xl text-slate-900 leading-tight mb-6 font-sans">
                {article.title}
              </h1>

              {article.excerpt && (
                <p className="text-xl text-slate-700 font-light border-l-2 border-indigo-500 pl-4">
                  {article.excerpt}
                </p>
              )}

              <div className="flex items-center justify-between mt-6">
                <div className="flex items-center gap-4">
                  <div className="flex -space-x-2">
                    {[1, 2, 3].map((i) => (
                      <div
                        key={i}
                        className="w-8 h-8 rounded-full bg-slate-200 border-2 border-slate-50 flex items-center justify-center text-[10px] text-slate-600"
                      >
                        AF
                      </div>
                    ))}
                  </div>
                  <span className="text-slate-600 text-sm">
                    Synthesized by Gemini
                  </span>
                </div>
                <div className="flex gap-2">
                  <button className="p-2 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-600 transition-colors">
                    <Share2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </header>

            {article.thumbnail && (
              <div className="relative aspect-video w-full rounded-xl overflow-hidden mb-10 border border-slate-200 shadow-sm">
                <Image
                  src={getThumbnailUrl(article.thumbnail, article.id)}
                  alt={article.title}
                  fill
                  className="object-cover"
                  priority
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 80vw, 1200px"
                />
              </div>
            )}

            <article className="max-w-none">
              <div className="article-content text-slate-900 leading-relaxed">
                <ReactMarkdown
                  components={{
                    h3: ({ node: _node, ...props }) => <h2 className="font-bold text-slate-900 mt-6 mb-6" {...props} />,
                    p: ({ node: _node, ...props }) => <p className="mt-4" {...props} />
                  }}
                >
                  {article.content}
                </ReactMarkdown>
              </div>
            </article>

          </div>

          <div className="lg:col-span-4 mt-12">
            <div className="sticky top-32 space-y-6">
              {/* Table of Contents */}
              <TableOfContents headings={headings} />

              {/* Sentiment Analysis */}
              <SentimentAnalysis score={sentimentScore} />

              {/* Advertisement */}
              <AdPlaceholder width={250} height={600} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
