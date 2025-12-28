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

  if (seconds < 60) return 'Just Now';

  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}M ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

interface NewsCardProps {
  item: NewsItem;
  isFeature?: boolean;
}

const NewsCard: React.FC<NewsCardProps> = ({ item, isFeature = false }) => {
  return (
    <Link href={`/article/${item.slug}`}>
      <article
        className={`group relative bg-white border border-slate-200 hover:border-indigo-500/50 transition-all duration-300 overflow-hidden hover:shadow-lg hover:shadow-indigo-500/10 cursor-pointer h-full rounded-lg ${isFeature ? 'flex flex-col md:flex-row' : 'flex flex-col'
          }`}
      >
        {/* Image */}
        <div className={`${isFeature ? 'h-64 md:h-auto md:w-1/2' : 'h-48 w-full'} overflow-hidden relative z-0 flex-shrink-0`}>
          <Image
            src={item.imageUrl}
            alt={item.headline}
            className="w-full h-full object-cover"
            fill
            sizes={isFeature ? "(max-width: 768px) 100vw, 50vw" : "(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"}
          />
        </div>

        {/* Content */}
        <div className={`relative z-20 p-5 flex flex-col flex-grow ${isFeature ? 'md:w-1/2 md:p-8' : ''}`}>
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wide">
              {item.category}
            </span>
          </div>

          <h3 className={`font-bold leading-tight mb-3 text-slate-900 group-hover:text-indigo-700 transition-colors font-sans ${isFeature ? 'text-xl md:text-2xl' : 'text-lg'}`}>
            {item.headline}
          </h3>

          <p className={`text-slate-700 mb-4 font-light leading-relaxed ${isFeature ? 'text-base line-clamp-4 md:line-clamp-5' : 'text-sm line-clamp-3'}`}>
            {item.summary}
          </p>

          <div className="mt-auto pt-4 border-t border-slate-200 flex items-center justify-between text-xs text-slate-600 font-mono">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1">
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
