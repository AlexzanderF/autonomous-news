import { getFinancialAnalysisArticles } from '@/services/financial-analysis-service';
import { Clock, ImageOff } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';
import { getThumbnailUrl } from '@/utils/thumbnails';

export default async function AnalysisListPage() {
  const articles = await getFinancialAnalysisArticles();

  return (
    <main className="pt-28">
      <section className="max-w-7xl mx-auto px-4 md:px-6 py-12">
        <header className="mb-10">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            Financial Analysis
          </h1>
          <p className="text-lg text-slate-600">
            In-depth market analysis and investment outlooks (powered by AI and experts)
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {articles.map((article) => (
            <Link
              key={article.id}
              href={`/analysis/${article.slug}`}
              className="group block bg-white border border-slate-200 rounded-xl overflow-hidden hover:border-emerald-300 hover:shadow-lg transition-all duration-200"
            >
              {/* Thumbnail */}
              <div className="relative aspect-[16/9] w-full bg-slate-100">
                {article.thumbnail_url ? (
                  <Image
                    src={getThumbnailUrl(article.thumbnail_url)}
                    alt={article.title}
                    fill
                    className="object-cover group-hover:scale-105 transition-transform duration-300"
                    sizes="(max-width: 768px) 100vw, 50vw"
                  />
                ) : (
                  <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-slate-100 to-slate-200">
                    <ImageOff className="w-12 h-12 text-slate-300 mb-2" />
                    <span className="text-xs text-slate-400 font-mono">No image</span>
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="p-6">
                <div className="flex items-center gap-2 mb-3">
                  {article.tags?.slice(0, 2).map((tag, index) => (
                    <span
                      key={index}
                      className="bg-emerald-100 text-emerald-700 border border-emerald-200 text-[10px] font-mono px-2 py-0.5 rounded uppercase tracking-wider"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                <h2 className="text-xl font-semibold text-slate-900 group-hover:text-emerald-700 transition-colors mb-3 line-clamp-2">
                  {article.title}
                </h2>

                <div className="flex items-center gap-4 text-sm text-slate-500">
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
      </section>
    </main>
  );
}

