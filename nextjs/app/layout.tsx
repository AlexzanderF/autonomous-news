import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Header from "@/components/Header";
import SubHeader from "@/components/SubHeader";
import Footer from "@/components/Footer";

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
        <Header />
        <SubHeader />
        <div className="w-full px-4 md:px-8 lg:px-12">
          {children}
        </div>
        <Footer />
      </body>
    </html>
  );
}
