'use client';

import React from 'react';
import Link from 'next/link';
import { Calendar, TrendingUp } from 'lucide-react';

interface NavItem {
  label: string;
  href: string;
  icon?: React.ReactNode;
}

const navItems: NavItem[] = [
  { label: 'Markets & Economy', href: '/topic/economy' },
  { label: 'Crypto', href: '/topic/crypto' },
  { label: 'AI', href: '/topic/ai' },
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

const SubHeader: React.FC = () => {
  return (
    <nav className="fixed top-16 left-0 right-0 z-40 bg-slate-900 h-10 flex items-center">
      <div className="w-full px-4 md:px-8 lg:px-12 flex items-center">
        <div className="flex items-center gap-1">
          {navItems.map((item, index) => (
            <Link
              key={item.label}
              href={item.href}
              className={`
                flex items-center gap-1.5 px-4 py-2 text-[13px] font-medium tracking-wide
                text-white hover:text-slate-300 transition-colors duration-150
                ${index === 0 ? 'pl-0' : ''}
              `}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default SubHeader;
