'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Linkedin, Facebook, Instagram, ChevronDown } from 'lucide-react';
import { SITE_NAME } from '@/constants';

// Custom X (Twitter) icon component
const XIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
  </svg>
);

interface FooterLink {
  label: string;
  href: string;
}

const navigationLinks: FooterLink[] = [
  { label: 'Markets & Economy', href: '/topic/economy' },
  { label: 'Politics', href: '/topic/politics' },
  { label: 'Tech', href: '/topic/tech' },
  { label: 'Science', href: '/topic/science' },
  { label: 'Environment', href: '/topic/environment' },
  { label: 'Analysis', href: '/analysis' },
  { label: 'Economic Calendar', href: '/economic-calendar' },
];

const resourceLinks: FooterLink[] = [
  { label: 'About Us', href: '/about' },
  { label: 'Subscribe', href: '/subscribe' },
  { label: 'Contact', href: '/contact' },
  { label: 'Advertise', href: '/advertise' },
];

const legalLinks: FooterLink[] = [
  { label: 'Terms of Use', href: '/terms' },
  { label: 'Privacy', href: '/privacy' },
  { label: 'Cookie Policy', href: '/cookies' },
  { label: 'Accessibility', href: '/accessibility' },
];

const socialLinks = [
  { icon: Linkedin, href: '#', label: 'LinkedIn' },
  { icon: XIcon, href: '#', label: 'X' },
  { icon: Facebook, href: '#', label: 'Facebook' },
  { icon: Instagram, href: '#', label: 'Instagram' },
];

// Accordion Section Component for Mobile
interface AccordionSectionProps {
  title: string;
  links: FooterLink[];
  isOpen: boolean;
  onToggle: () => void;
}

const AccordionSection: React.FC<AccordionSectionProps> = ({ title, links, isOpen, onToggle }) => (
  <div className="border-b border-slate-700/50">
    {/* Mobile: Clickable header */}
    <button
      onClick={onToggle}
      className="w-full flex items-center justify-between py-4 text-left"
    >
      <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400">
        {title}
      </h3>
      <ChevronDown 
        className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} 
      />
    </button>
    
    {/* Links - collapsible */}
    <ul className={`list-none space-y-2.5 overflow-hidden transition-all duration-200 ${
      isOpen ? 'max-h-96 pb-4' : 'max-h-0'
    }`}>
      {links.map((link) => (
        <li key={link.label}>
          <Link
            href={link.href}
            className="text-sm font-bold text-slate-300 hover:text-white transition-colors duration-150"
          >
            {link.label}
          </Link>
        </li>
      ))}
    </ul>
  </div>
);

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();
  const [openSection, setOpenSection] = useState<string | null>(null);

  const toggleSection = (section: string) => {
    setOpenSection(openSection === section ? null : section);
  };

  return (
    <footer className="bg-slate-900 text-slate-300 mt-16">
      {/* Social Bar */}
      <div className="border-b border-slate-700/50">
        <div className="w-full container-padding py-5 flex items-center">
          <div className="flex items-center gap-3">
            {socialLinks.map(({ icon: Icon, href, label }) => (
              <a
                key={label}
                href={href}
                aria-label={label}
                className="p-2 text-white hover:text-indigo-400 hover:bg-slate-700/50 rounded-full transition-all duration-200"
              >
                <Icon className="w-5 h-5" />
              </a>
            ))}
          </div>
        </div>
      </div>

      {/* Main Footer Content */}
      <div className="w-full container-padding py-6 md:py-10">
        {/* Desktop: Original 4-column grid */}
        <div className="hidden md:grid md:grid-cols-4 gap-8">
          {/* Topics Column */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">
              Topics
            </h3>
            <ul className="list-none space-y-2.5">
              {navigationLinks.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-sm font-bold text-slate-300 hover:text-white transition-colors duration-150"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources Column */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">
              Resources
            </h3>
            <ul className="list-none space-y-2.5">
              {resourceLinks.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-sm font-bold text-slate-300 hover:text-white transition-colors duration-150"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal Column */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">
              Legal
            </h3>
            <ul className="list-none space-y-2.5">
              {legalLinks.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-sm font-bold text-slate-300 hover:text-white transition-colors duration-150"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Newsletter / Brand Column */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-4">
              Stay Informed
            </h3>
            <p className="text-sm text-slate-400 mb-4 leading-relaxed">
              Get the latest macroeconomic insights and market analysis delivered directly to your inbox.
            </p>
            <div className="flex">
              <input
                type="email"
                placeholder="Your email"
                className="flex-1 px-3 py-2 bg-slate-800 border border-slate-700 rounded-l text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
              />
              <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-r transition-colors">
                Subscribe
              </button>
            </div>
          </div>
        </div>

        {/* Mobile: Accordion sections */}
        <div className="md:hidden">
          <AccordionSection
            title="Topics"
            links={navigationLinks}
            isOpen={openSection === 'topics'}
            onToggle={() => toggleSection('topics')}
          />
          <AccordionSection
            title="Resources"
            links={resourceLinks}
            isOpen={openSection === 'resources'}
            onToggle={() => toggleSection('resources')}
          />
          <AccordionSection
            title="Legal"
            links={legalLinks}
            isOpen={openSection === 'legal'}
            onToggle={() => toggleSection('legal')}
          />

          {/* Newsletter at the end on mobile */}
          <div className="pt-6">
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3">
              Stay Informed
            </h3>
            <p className="text-sm text-slate-400 mb-4 leading-relaxed">
              Get the latest insights delivered to your inbox.
            </p>
            <div className="flex">
              <input
                type="email"
                placeholder="Your email"
                className="flex-1 px-3 py-2 bg-slate-800 border border-slate-700 rounded-l text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
              />
              <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-r transition-colors">
                Subscribe
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-slate-700/50">
        <div className="w-full container-padding py-5">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            {/* Legal Links Row */}
            <div className="flex flex-wrap items-center justify-center gap-4 text-xs">
              {legalLinks.map((link, index) => (
                <React.Fragment key={link.label}>
                  <Link
                    href={link.href}
                    className="text-slate-400 hover:text-white underline transition-colors"
                  >
                    {link.label}
                  </Link>
                  {index < legalLinks.length - 1 && (
                    <span className="text-slate-600 hidden sm:inline">|</span>
                  )}
                </React.Fragment>
              ))}
            </div>

            {/* Copyright */}
            <div className="text-xs text-slate-500 text-center md:text-right">
              <p>© {SITE_NAME} {currentYear}. All rights reserved.</p>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
