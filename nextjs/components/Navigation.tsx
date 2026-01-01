'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Menu, X, Calendar, TrendingUp, User } from 'lucide-react';

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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [headerVisible, setHeaderVisible] = useState(true);
  const scrollPositionRef = useRef(0);
  const lastScrollYRef = useRef(0);

  // Handle menu close with animation
  const closeMenu = () => {
    setIsClosing(true);
    setTimeout(() => {
      setMobileMenuOpen(false);
      setIsClosing(false);
    }, 280); // Slightly less than animation duration to feel snappy
  };

  // Hide header on scroll down, show on scroll up (mobile only)
  useEffect(() => {
    const SCROLL_THRESHOLD = 20; // Minimum scroll distance to trigger hide/show

    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const scrollDelta = currentScrollY - lastScrollYRef.current;

      // Only trigger if scroll distance exceeds threshold
      if (Math.abs(scrollDelta) >= SCROLL_THRESHOLD) {
        if (scrollDelta > 0 && currentScrollY > 100) {
          // Scrolling down & past initial area - hide header
          setHeaderVisible(false);
        } else if (scrollDelta < 0) {
          // Scrolling up - show header
          setHeaderVisible(true);
        }
        lastScrollYRef.current = currentScrollY;
      }

      // Always show header at top of page
      if (currentScrollY < 100) {
        setHeaderVisible(true);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Lock body scroll when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      // Store current scroll position in ref before locking
      scrollPositionRef.current = window.scrollY;
      document.body.style.position = 'fixed';
      document.body.style.top = `-${scrollPositionRef.current}px`;
      document.body.style.left = '0';
      document.body.style.right = '0';
      document.body.style.overflow = 'hidden';
    } else {
      // Restore scroll position from ref
      document.body.style.position = '';
      document.body.style.top = '';
      document.body.style.left = '';
      document.body.style.right = '';
      document.body.style.overflow = '';
      window.scrollTo(0, scrollPositionRef.current);
    }
    return () => {
      document.body.style.position = '';
      document.body.style.top = '';
      document.body.style.left = '';
      document.body.style.right = '';
      document.body.style.overflow = '';
    };
  }, [mobileMenuOpen]);

  return (
    <div 
      className={`sticky top-0 z-50 transition-transform duration-500 md:translate-y-0 ${
        headerVisible ? 'translate-y-0' : '-translate-y-full'
      }`}
    >
      {/* Main Header */}
      <header className="bg-white border-b border-slate-200 h-14 md:h-16 flex items-center isolate">
        <div className="w-full px-4 md:px-8 lg:px-12 flex items-center justify-between">
          <div className="flex items-center gap-3 min-w-0 flex-shrink">
            <Link href="/">
              <Image
                src="/logo-white-background.svg"
                alt="The Macronomics"
                width={240}
                height={56}
                // className="h-18 md:h-24 w-auto -ml-3 md:-ml-5"
                priority
              />
            </Link>
          </div>

          <div className="flex items-center gap-3 md:gap-6 flex-shrink-0">
            <Link
              href="/wip"
              className="px-3 md:px-5 py-1.5 md:py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-[10px] md:text-[11px] font-black rounded-full transition-all shadow-md hover:shadow-lg active:scale-95 tracking-widest uppercase inline-block text-center"
            >
              Subscribe
            </Link>

            <div className="h-4 w-px bg-slate-200" />

            <Link
              href="/wip"
              className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
            >
              <User className="w-4 h-4" />
              <span className="hidden md:inline">Sign in</span>
            </Link>

            <div className="h-4 w-px bg-slate-200" />

            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="flex items-center gap-1.5 md:gap-2 text-slate-600 group transition-colors hover:text-slate-900"
            >
              {mobileMenuOpen ? (
                <X className="w-5 h-5 text-slate-500 group-hover:text-slate-900" />
              ) : (
                <Menu className="w-5 h-5 text-slate-500 group-hover:text-slate-900" />
              )}
              <span className="hidden md:inline text-sm font-medium uppercase tracking-wider">Menu</span>
            </button>
          </div>
        </div>
      </header>

      {/* Sub Navigation - Horizontally scrollable on mobile */}
      <nav className="bg-slate-900 h-10 flex items-center overflow-hidden relative">
        <div className="w-full px-4 md:px-8 lg:px-12 overflow-x-auto scrollbar-hide">
          <div className="flex items-center gap-1 w-max md:w-auto">
            {navItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className={`
                  group relative flex items-center gap-1.5 mr-4 py-1.5 text-[13px] md:text-[14px] font-bold tracking-wide
                  text-white transition-all duration-150 whitespace-nowrap
                `}
              >
                {item.icon}
                <span>{item.label}</span>
                <span className="absolute left-0 bottom-[-5px] w-0 h-[5px] bg-white group-hover:w-full transition-all duration-200" />
              </Link>
            ))}
          </div>
        </div>
        {/* Gradient fade indicator for mobile */}
        <div className="md:hidden absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-slate-900 to-transparent pointer-events-none" />
      </nav>

      {/* Mobile Menu Overlay - Full Screen with Slide Animation */}
      {mobileMenuOpen && (
        <div className={`md:hidden fixed inset-0 bg-slate-900 z-[100] overflow-y-auto ${isClosing ? 'animate-slide-out-right' : 'animate-slide-in-right'}`}>
          {/* Menu Header with Close Button */}
          <div className="flex items-center justify-between px-4 border-b border-slate-700">
            <Link href="/" onClick={closeMenu}>
              <Image
                src="/logo-white-background.svg"
                alt="The Macronomics"
                width={240}
                height={56}
                className="h-18 w-auto -ml-3 invert"
                priority
              />
            </Link>
            <button
              onClick={closeMenu}
              className="p-2 text-white hover:text-indigo-300 transition-colors"
              aria-label="Close menu"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Menu Content */}
          <div className="px-6 py-6">
            {/* Subscribe and Sign in row */}
            <div className="flex items-center justify-between pb-6 border-b border-slate-700">
              <Link
                href="/wip"
                onClick={closeMenu}
                className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-[10px] font-black rounded-full transition-all shadow-md hover:shadow-lg active:scale-95 tracking-widest uppercase"
              >
                Subscribe
              </Link>
              <Link
                href="/wip"
                onClick={closeMenu}
                className="flex items-center gap-2 text-base font-medium text-white hover:text-indigo-300 transition-colors"
              >
                <User className="w-5 h-5" />
                Sign in
              </Link>
            </div>

            <div className="pt-6">
              <p className="text-xs text-slate-400 uppercase tracking-widest mb-4">Topics</p>
              <div className="flex flex-col gap-1">
                {navItems.map((item) => (
                  <Link
                    key={item.label}
                    href={item.href}
                    onClick={closeMenu}
                    className="flex items-center gap-3 text-lg font-semibold text-white hover:text-indigo-300 py-3 transition-colors border-b border-slate-800"
                  >
                    {item.icon}
                    <span>{item.label}</span>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Navigation;
