'use client';

import React from 'react';
import Link from 'next/link';
import { Calendar } from 'lucide-react';

interface NavItem {
  label: string;
  href: string;
  icon?: React.ReactNode;
}

const navItems: NavItem[] = [
  { label: 'Politics', href: '/?category=politics' },
  { label: 'Economy', href: '/?category=economy' },
  { label: 'Tech', href: '/?category=tech' },
  { label: 'Science', href: '/?category=science' },
  { label: 'Environment', href: '/?category=environment' },
  { 
    label: 'Economic Calendar', 
    href: '/economic-calendar',
    icon: <Calendar className="w-3.5 h-3.5" />
  },
];

const SubHeader: React.FC = () => {
  return (
    <nav className="fixed top-16 left-0 right-0 z-40 bg-slate-900 h-10 flex items-center px-12">
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
    </nav>
  );
};

export default SubHeader;
