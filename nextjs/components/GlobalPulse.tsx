'use client';

import React, { useEffect, useState } from 'react';
import { BarChart, Bar, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const data = [
  { name: 'TECH', volume: 850 },
  { name: 'POLITICS', volume: 620 },
  { name: 'FINANCE', volume: 480 },
  { name: 'CLIMATE', volume: 750 },
  { name: 'SPACE', volume: 320 },
];

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-900 border border-cyan-500/30 p-2 text-xs font-mono shadow-lg">
        <p className="text-cyan-400">{`${payload[0].payload.name}`}</p>
        <p className="text-slate-300">{`VOLUME: ${payload[0].value} stories`}</p>
      </div>
    );
  }
  return null;
};

const GlobalPulse: React.FC = () => {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <section className="w-full py-8 border-b border-slate-800 bg-slate-900/20">
        <div className="max-w-7xl mx-auto px-6">
            <div className="flex flex-col md:flex-row justify-between items-end mb-6">
                 <div>
                    <h2 className="text-sm font-mono text-slate-500 mb-1">CATEGORY DISTRIBUTION</h2>
                    <div className="text-3xl font-bold text-slate-100 font-sans">
                        Global Trend Volume
                    </div>
                 </div>
            </div>
            
            <div className="h-48 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                        <XAxis 
                            dataKey="name" 
                            tick={{fill: '#64748b', fontSize: 10, fontFamily: 'monospace'}} 
                            axisLine={false} 
                            tickLine={false} 
                            dy={10}
                        />
                        <YAxis 
                            tick={{fill: '#475569', fontSize: 10, fontFamily: 'monospace'}} 
                            axisLine={false}
                            tickLine={false}
                            hide={true}
                        />
                        <Tooltip cursor={{fill: 'rgba(6, 182, 212, 0.05)'}} content={<CustomTooltip />} />
                        <Bar 
                            dataKey="volume" 
                            fill="#06b6d4" 
                            radius={[4, 4, 0, 0]} 
                            barSize={60}
                            animationDuration={2000} 
                            className="opacity-80 hover:opacity-100 transition-opacity"
                        />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    </section>
  );
};

export default GlobalPulse;
