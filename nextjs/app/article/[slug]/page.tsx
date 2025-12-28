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
      <div className="w-full">

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          <div className="lg:col-span-8 mt-12">
            <header className="mb-8 border-b border-slate-200 pb-8">
              <div className="flex items-center gap-3 mb-4">
                {article.categories.map((category) => (
                  <span
                    key={category.id}
                    className="text-xs font-semibold text-indigo-700 uppercase tracking-wide"
                  >
                    {category.name}
                  </span>
                ))}
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
