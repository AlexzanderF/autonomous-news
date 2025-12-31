'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft, Construction } from 'lucide-react';

const WorkInProgressPage = () => {
  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center p-6 bg-white relative overflow-hidden">
      {/* Background Decor */}
      <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-indigo-50 rounded-full blur-[100px] opacity-60 pointer-events-none" />
      <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-slate-50 rounded-full blur-[100px] opacity-60 pointer-events-none" />
      
      <div className="max-w-2xl w-full text-center relative z-10">
        <div className="mb-8 inline-flex items-center justify-center w-24 h-24 rounded-3xl bg-slate-900 shadow-xl shadow-slate-200 animate-bounce-slow">
          <Construction className="w-10 h-10 text-white" />
        </div>
        
        <h1 className="text-4xl md:text-5xl font-black text-slate-900 mb-4 tracking-tight">
          Work in Progress
        </h1>
        
        <p className="text-lg md:text-xl text-slate-600 mb-12 font-medium leading-relaxed">
          This feature is currently under development and will be available soon.
        </p>
        
        <Link 
          href="/"
          className="inline-flex items-center gap-2 px-8 py-4 bg-slate-900 text-white font-bold rounded-full transition-all hover:bg-slate-800 hover:shadow-xl active:scale-95 group"
        >
          <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          Back to Homepage
        </Link>
      </div>
      
      <style jsx global>{`
        @keyframes bounce-slow {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-10px);
          }
        }
        .animate-bounce-slow {
          animation: bounce-slow 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};

export default WorkInProgressPage;
