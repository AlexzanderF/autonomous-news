'use client';

import React from 'react';
import Link from 'next/link';
import { NewsItem } from '@/dtos';

import Image from 'next/image';
import { formatTimeAgo } from '@/utils/date';

interface NewsCardProps {
  item: NewsItem;
}

const NewsCard: React.FC<NewsCardProps> = ({ item }) => {
  return (
    <Link href={`/article/${item.slug}`}>
      <article className="group relative bg-white border border-slate-200 hover:border-indigo-500/50 transition-all duration-300 overflow-hidden hover:shadow-lg hover:shadow-indigo-500/10 cursor-pointer h-full rounded-lg flex flex-col">
        {/* Image */}
        <div className="h-48 w-full overflow-hidden relative z-0 flex-shrink-0">
          <Image
            src={item.imageUrl}
            alt={item.headline}
            className="w-full h-full object-cover object-top"
            fill
            sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
          />
        </div>

        {/* Content */}
        <div className="relative z-20 p-5 flex flex-col flex-grow">
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs font-semibold text-indigo-700 uppercase tracking-wide">
              {item.category}
            </span>
          </div>

          <h3 className="font-bold leading-tight mb-3 text-slate-900 group-hover:text-indigo-700 transition-colors font-sans text-lg">
            {item.headline}
          </h3>

          <p className="text-slate-700 mb-4 font-light leading-relaxed text-sm line-clamp-3">
            {item.summary}
          </p>

          <div className="mt-auto">
            <span className="text-xs text-slate-400">{formatTimeAgo(item.timestamp)}</span>
          </div>
        </div>
      </article>
    </Link>
  );
};

export default NewsCard;
