'use client';

import { useState } from 'react';
import GlobalPulse from '@/components/GlobalPulse';
import NewsCard from '@/components/NewsCard';
import { MOCK_NEWS } from '@/constants';
import { Filter, RefreshCw } from 'lucide-react';

export default function Home() {
  const [filter, setFilter] = useState<string>('ALL');

  return (
    <main className="pt-16">
      {/* Hero / Stats Section */}
      <GlobalPulse />

      {/* Main Content Area */}
      <section className="max-w-7xl mx-auto px-6 py-8">
         <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
            <div className="flex items-end gap-4">
                <h2 className="text-2xl font-bold text-white">Inbound Streams</h2>
                <span className="text-xs font-mono text-cyan-500 mb-1 animate-pulse">● LIVE</span>
            </div>
            
            <div className="flex items-center gap-3">
                <button className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 rounded hover:border-slate-600 transition-colors text-xs font-mono text-slate-400">
                    <Filter className="w-3 h-3" />
                    <span>FILTER: {filter}</span>
                </button>
                <button className="p-2 bg-slate-900 border border-slate-800 rounded hover:border-cyan-500/50 hover:text-cyan-400 transition-colors text-slate-400">
                    <RefreshCw className="w-3 h-3" />
                </button>
            </div>
         </div>

         {/* Masonry Grid Simulation */}
         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {MOCK_NEWS.map((news) => (
                <div key={news.id} className="h-full">
                    <NewsCard item={news} />
                </div>
            ))}
         </div>
         
         {/* Feed End */}
         <div className="mt-16 mb-12 flex flex-col items-center justify-center gap-4 text-slate-600">
             <div className="w-px h-16 bg-gradient-to-b from-transparent via-slate-800 to-transparent"></div>
             <span className="text-[10px] font-mono tracking-widest opacity-50">AWAITING NEW SIGNALS...</span>
         </div>
      </section>
    </main>
  );
}
