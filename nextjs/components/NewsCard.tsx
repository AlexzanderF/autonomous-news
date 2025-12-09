'use client';

import React from 'react';
import Link from 'next/link';
import { NewsItem } from '@/dtos';
import { FileText, Clock } from 'lucide-react';
import Image from 'next/image';

function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'JUST NOW';
  
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}M AGO`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h AGO`;

  const days = Math.floor(hours / 24);
  return `${days}d AGO`;
}

interface NewsCardProps {
  item: NewsItem;
}

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
           <Image
              src={item.imageUrl} 
              alt={item.headline} 
              className="w-full h-full object-cover" 
              fill
           />
        </div>

        {/* Content */}
        <div className="relative z-20 p-5 flex flex-col flex-grow">
          <div className="flex justify-between items-start mb-3">
               <span className="text-[10px] font-mono text-cyan-500 tracking-widest border-b border-cyan-500/30 pb-0.5">
                  {item.category}
               </span>
          </div>
          
          <h3 className="text-lg font-bold leading-tight mb-3 text-slate-100 group-hover:text-cyan-50 transition-colors font-sans">
            {item.headline}
          </h3>
          
          <p className="text-sm text-slate-400 line-clamp-3 mb-4 font-light leading-relaxed">
            {item.summary}
          </p>

          <div className="mt-auto pt-4 border-t border-slate-800/50 flex items-center justify-between text-xs text-slate-500 font-mono">
             <div className="flex items-center gap-4">
                <div className="flex items-center gap-1" title="Published">
                   <Clock className="w-3 h-3" />
                   <span>{formatTimeAgo(item.timestamp)}</span>
                </div>
             </div>
          </div>
        </div>
      </article>
    </Link>
  );
};

export default NewsCard;
