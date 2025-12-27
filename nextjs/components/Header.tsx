'use client';

import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-slate-200 h-16 flex items-center px-6 justify-between isolate">
      <div className="flex items-center gap-3">
        <h1 className="text-xl font-bold tracking-wider text-slate-900">
          MT <span className="text-xs font-normal text-slate-700 tracking-widest ml-1">MACRO THREADS</span>
        </h1>
      </div>
    </header>
  );
};

export default Header;