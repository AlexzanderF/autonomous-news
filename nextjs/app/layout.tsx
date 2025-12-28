import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Footer from "@/components/Footer";
import AdPlaceholder from "@/components/AdPlaceholder";
import Navigation from "@/components/Navigation";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MT - Macro Threads",
  description: "Financial and macroeconomic news and analysis",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-slate-50 text-slate-800 font-sans selection:bg-indigo-500/30 selection:text-indigo-900`}
      >
        {/* Full-width top ad banner - scrolls with content */}
        <div className="w-full bg-slate-100 border-b border-slate-200">
          <div className="max-w-4xl mx-auto px-4 py-3">
            <AdPlaceholder width={728} height={250} />
          </div>
        </div>
        
        <Navigation />
        <div className="w-full px-4 md:px-8 lg:px-12">
          {children}
        </div>
        <Footer />
      </body>
    </html>
  );
}
