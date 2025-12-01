'use client';

import React from 'react';
import { Radio } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-slate-800 h-16 flex items-center px-6 justify-between">
      <div className="flex items-center gap-3">
        <div className="relative">
            <div className="absolute inset-0 bg-cyan-500 blur-md opacity-40 animate-pulse-slow"></div>
            <Radio className="w-6 h-6 text-cyan-400 relative z-10" />
        </div>
        <h1 className="text-xl font-bold tracking-wider text-white">
          ANI <span className="text-xs font-normal text-slate-400 tracking-widest ml-1 opacity-70">AUTONOMOUS NEWS</span>
        </h1>
      </div>

      <div className="text-xs font-mono text-slate-500">
        v2.5.0-alpha
      </div>
    </header>
  );
};

export default Header;
