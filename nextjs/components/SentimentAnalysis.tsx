'use client';

import React, { useState } from 'react';
import { ChevronDown, Activity } from 'lucide-react';

interface SentimentAnalysisProps {
  score: number;
}

export default function SentimentAnalysis({ score }: SentimentAnalysisProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const widthPercentage = Math.abs(score - 50);

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm transition-all duration-300">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 px-5 hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-2 text-slate-700">
          <Activity className="w-4 h-4 text-indigo-500" />
          <span className="font-mono font-bold tracking-wider text-sm uppercase">AI Sentiment Analysis</span>
        </div>
        <div className="flex items-center gap-3">
          {!isExpanded && (
            <span className="text-sm font-mono font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded shadow-sm">
              {score}
            </span>
          )}
          <ChevronDown 
            className={`w-4 h-4 text-slate-400 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`} 
          />
        </div>
      </button>

      <div 
        className={`transition-all duration-300 ease-in-out ${
          isExpanded ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'
        } overflow-hidden`}
      >
        <div className="px-6 pb-6 pt-0">
          <div className="mb-2">
            <div className="flex justify-between text-xs text-slate-600 mb-2 font-mono w-full px-1">
              <span>Negative</span>
              <span>Serious</span>
              <span>Neutral</span>
              <span>Optimistic</span>
              <span>Positive</span>
            </div>
            <div className="h-2 bg-slate-200 rounded-full overflow-hidden relative">
              <div
                className="absolute top-0 h-full overflow-hidden rounded-full"
                style={{
                  left: score > 50 ? '50%' : `${50 - widthPercentage}%`,
                  width: `${widthPercentage}%`,
                }}
              >
                <div
                  className={`absolute top-0 h-full ${score > 50
                    ? 'left-0 bg-gradient-to-r from-slate-400 to-green-500'
                    : 'right-0 bg-gradient-to-r from-red-500 to-slate-400'
                    }`}
                  style={{
                    width: widthPercentage > 0 ? `${(50 / widthPercentage) * 100}%` : '0px',
                  }}
                />
              </div>
            </div>
          </div>

          <div className="flex justify-between items-center mt-2 px-1">
            <span className="text-xs font-mono text-slate-500 font-bold">0</span>
            <div className="text-center font-mono text-l font-bold text-slate-900">
              {score}
            </div>
            <span className="text-xs font-mono text-slate-500 font-bold">100</span>
          </div>

          <div className="mt-4 pt-4 border-t border-slate-200">
            <p className="text-[10px] text-slate-600 font-mono leading-relaxed uppercase">
              Reflects the overall direction and mood of the article.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
