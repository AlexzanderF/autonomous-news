'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Menu, Calendar, TrendingUp } from 'lucide-react';

interface NavItem {
  label: string;
  href: string;
  icon?: React.ReactNode;
}

const navItems: NavItem[] = [
  { label: 'Markets & Economy', href: '/topic/economy' },
  { label: 'Politics', href: '/topic/politics' },
  { label: 'Tech', href: '/topic/tech' },
  { label: 'Science', href: '/topic/science' },
  { label: 'Environment', href: '/topic/environment' },
  { 
    label: 'Analysis', 
    href: '/analysis',
    icon: <TrendingUp className="w-3.5 h-3.5" />
  },
  { 
    label: 'Economic Calendar', 
    href: '/economic-calendar',
    icon: <Calendar className="w-3.5 h-3.5" />
  },
];

const Navigation: React.FC = () => {
  return (
    <div className="sticky top-0 z-50">
      {/* Main Header */}
      <header className="bg-white border-b border-slate-200 h-16 flex items-center isolate">
        <div className="w-full px-4 md:px-8 lg:px-12 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/">
              <Image 
                src="/logo-white-background.svg" 
                alt="The Macronomics" 
                width={240} 
                height={56}
                className="h-24 w-auto -ml-5"
                priority
              />
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

      {/* Sub Navigation */}
      <nav className="bg-slate-900 h-10 flex items-center">
        <div className="w-full px-4 md:px-8 lg:px-12 flex items-center">
          <div className="flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className={`
                  group relative flex items-center gap-1.5 mr-4 py-1.5 text-[14px] font-bold tracking-wide
                  text-white transition-all duration-150
                `}
              >
                {item.icon}
                <span>{item.label}</span>
                <span className="absolute left-0 bottom-[-5px] w-0 h-[5px] bg-white group-hover:w-full transition-all duration-200" />
              </Link>
            ))}
          </div>
        </div>
      </nav>
    </div>
  );
};

export default Navigation;
