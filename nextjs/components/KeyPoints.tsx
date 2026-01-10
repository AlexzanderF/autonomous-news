'use client';

import React from 'react';
import { Sparkles } from 'lucide-react';

interface KeyPointsProps {
  keyPoints: string[] | null;
}

export default function KeyPoints({ keyPoints }: KeyPointsProps) {
  if (!keyPoints || keyPoints.length === 0) {
    return null;
  }

  return (
    <div className="bg-slate-50 border-l-4 border-indigo-600 p-6 mb-8">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-5 h-5 text-indigo-600" />
        <h2 className="text-sm font-bold text-indigo-700 uppercase tracking-wider">
          Key Points
        </h2>
      </div>
      <ul className="space-y-3">
        {keyPoints.map((point, index) => (
          <li key={index} className="flex items-start gap-3">
            <span className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-slate-800 mt-2.5" />
            <span className="text-slate-800 text-base leading-relaxed">
              {point}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
