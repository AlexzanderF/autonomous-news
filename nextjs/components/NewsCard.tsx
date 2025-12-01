'use client';

import React from 'react';
import Link from 'next/link';
import { NewsItem, Sentiment } from '@/types';
import { Globe, BarChart2, FileText } from 'lucide-react';

interface NewsCardProps {
  item: NewsItem;
}

const SentimentBadge: React.FC<{ sentiment: Sentiment }> = ({ sentiment }) => {
  const colors = {
    [Sentiment.POSITIVE]: 'text-emerald-400 border-emerald-400/30 bg-emerald-400/10',
    [Sentiment.NEGATIVE]: 'text-rose-400 border-rose-400/30 bg-rose-400/10',
    [Sentiment.NEUTRAL]: 'text-blue-400 border-blue-400/30 bg-blue-400/10',
    [Sentiment.CONTROVERSIAL]: 'text-amber-400 border-amber-400/30 bg-amber-400/10',
  };

  return (
    <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${colors[sentiment]}`}>
      {sentiment}
    </span>
  );
};

const NewsCard: React.FC<NewsCardProps> = ({ item }) => {
  return (
    <Link href={`/article/${item.slug}`}>
      <article 
        className="group relative bg-slate-900/50 border border-slate-800 hover:border-cyan-500/50 transition-all duration-300 overflow-hidden hover:shadow-[0_0_20px_rgba(6,182,212,0.1)] cursor-pointer flex flex-col h-full"
      >
        {/* Image Overlay Gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/80 to-slate-950 z-10 pointer-events-none" />
        
        {/* Image */}
        <div className="h-48 w-full overflow-hidden relative z-0">
           <img 
              src={item.imageUrl} 
              alt={item.headline} 
              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105 grayscale group-hover:grayscale-0 opacity-80 group-hover:opacity-100" 
              loading="lazy"
           />
        </div>

        {/* Content */}
        <div className="relative z-20 p-5 flex flex-col flex-grow">
          <div className="flex justify-between items-start mb-3">
               <span className="text-[10px] font-mono text-cyan-500 tracking-widest border-b border-cyan-500/30 pb-0.5">
                  {item.category}
               </span>
               <SentimentBadge sentiment={item.sentiment} />
          </div>
          
          <h3 className="text-lg font-bold leading-tight mb-3 text-slate-100 group-hover:text-cyan-50 transition-colors font-sans">
            {item.headline}
          </h3>
          
          <p className="text-sm text-slate-400 line-clamp-3 mb-4 font-light leading-relaxed">
            {item.summary}
          </p>

          <div className="mt-auto pt-4 border-t border-slate-800/50 flex items-center justify-between text-xs text-slate-500 font-mono">
             <div className="flex items-center gap-4">
                <div className="flex items-center gap-1" title="Sources Analyzed">
                   <Globe className="w-3 h-3" />
                   <span>{item.sourceCount}</span>
                </div>
                <div className="flex items-center gap-1" title="Reliability Score">
                   <BarChart2 className="w-3 h-3" />
                   <span>{item.sentimentScore}%</span>
                </div>
             </div>
             <div className="opacity-0 group-hover:opacity-100 transition-opacity text-cyan-400 flex items-center gap-1">
                <span>FULL REPORT</span>
                <FileText className="w-3 h-3" />
             </div>
          </div>
        </div>
      </article>
    </Link>
  );
};

export default NewsCard;
