'use client';

import React from 'react';

interface KeyPointsProps {
  keyPoints: string[] | null;
}

export default function KeyPoints({ keyPoints }: KeyPointsProps) {
  if (!keyPoints || keyPoints.length === 0) {
    return null;
  }

  return (
    <div className="bg-slate-50 border-l-4 border-indigo-500 py-2 px-6 mb-10">
      <div className="flex items-center gap-2 mb-3">
        <h2 className="text-lg font-bold text-indigo-500 uppercase tracking-wider">
          Key Points
        </h2>
      </div>
      <ul className="space-y-3">
        {keyPoints.map((point, index) => (
          <li key={index} className="flex items-start gap-3">
            <span className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-indigo-700 mt-3" />
            <span className="text-slate-800 text-lg leading-relaxed">
              {point}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
