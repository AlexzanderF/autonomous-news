import type { Metadata } from "next";
import { Archivo_Narrow } from "next/font/google";
import "./globals.css";
import Footer from "@/components/Footer";
import AdPlaceholder from "@/components/AdPlaceholder";
import Navigation from "@/components/Navigation";

const archivoNarrow = Archivo_Narrow({
  variable: "--font-archivo-narrow",
  subsets: ["latin"],
  display: "swap",
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
        className={`${archivoNarrow.variable} antialiased min-h-screen bg-slate-50 text-slate-800 selection:bg-indigo-500/30 selection:text-indigo-900`}
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
