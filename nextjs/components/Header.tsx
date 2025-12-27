'use client';

import React from 'react';
import { Menu } from 'lucide-react';
import Link from 'next/link';

const Header: React.FC = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-slate-200 h-16 flex items-center isolate">
      <div className="max-w-7xl mx-auto w-full px-4 md:px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
        <Link href="/">
          <h1 className="text-xl font-bold tracking-wider text-slate-900 flex items-center">
            MT <span className="text-[10px] font-normal text-slate-500 tracking-[0.2em] ml-2 mt-1 whitespace-nowrap">MACRO THREADS</span>
          </h1>
        </Link>
      </div>

      <div className="flex items-center gap-6">
        <button className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-[11px] font-black rounded-full transition-all shadow-md hover:shadow-lg active:scale-95 tracking-widest uppercase">
          Subscribe
        </button>

        <div className="h-4 w-px bg-slate-200" />

        <button className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">
          Sign in
        </button>
        
        <div className="h-4 w-px bg-slate-200" />

        <button className="flex items-center gap-2 text-slate-600 group transition-colors hover:text-slate-900">
          <Menu className="w-5 h-5 text-slate-500 group-hover:text-slate-900" />
          <span className="text-sm font-medium uppercase tracking-wider">Menu</span>
        </button>
        </div>
      </div>
    </header>
  );
};

export default Header;