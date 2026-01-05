import type { Metadata } from "next";
import { Archivo_Narrow } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import Footer from "@/components/Footer";
import AdSense from "@/components/AdSense";
import Navigation from "@/components/Navigation";
import { SITE_NAME, SITE_DESCRIPTION } from "@/constants";

const archivoNarrow = Archivo_Narrow({
  variable: "--font-archivo-narrow",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: SITE_NAME,
  description: SITE_DESCRIPTION,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* Google AdSense Script */}
        <Script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5508175880003857"
          crossOrigin="anonymous"
          strategy="afterInteractive"
        />
      </head>
      <body
        className={`${archivoNarrow.variable} antialiased min-h-screen bg-slate-50 text-slate-800 selection:bg-indigo-500/30 selection:text-indigo-900`}
      >
        {/* Full-width top ad banner - hidden on mobile, scrolls with content */}
        <div className="hidden md:block w-full bg-slate-100 border-b border-slate-200">
          <div className="max-w-4xl mx-auto px-4 py-3">
            <AdSense format="horizontal" fullWidth />
          </div>
        </div>
        
        <Navigation />
        <div className="w-full container-padding">
          {children}
        </div>
        <Footer />
      </body>
    </html>
  );
}
