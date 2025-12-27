'use client';

import React from 'react';

interface AdPlaceholderProps {
  width?: number;
  height?: number;
}

const AdPlaceholder: React.FC<AdPlaceholderProps> = ({ width = 300, height = 250 }) => {
  const dimensions = `${width} × ${height}`;
  
  return (
    <div 
      className="bg-slate-100 border border-slate-200 rounded-lg flex items-center justify-center h-full"
      style={{ minHeight: `${height}px` }}
    >
      <div className="text-center p-4">
        <div className="w-12 h-12 mx-auto mb-3 bg-slate-200 rounded-lg flex items-center justify-center">
          <span className="text-slate-400 text-xs font-bold">AD</span>
        </div>
        <p className="text-xs text-slate-400 font-mono tracking-wide">ADVERTISEMENT</p>
        <p className="text-[10px] text-slate-300 mt-1">{dimensions}</p>
      </div>
    </div>
  );
};

export default AdPlaceholder;
