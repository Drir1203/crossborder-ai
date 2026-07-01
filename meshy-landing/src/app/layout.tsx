import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Meshy Copy - AI-Powered Writing Assistant",
  description:
    "Write like a pro with AI. Meshy Copy helps you craft clear, compelling content in seconds — from emails to blog posts.",
  openGraph: {
    title: "Meshy Copy - AI-Powered Writing Assistant",
    description:
      "Write like a pro with AI. Meshy Copy helps you craft clear, compelling content in seconds — from emails to blog posts.",
    url: "https://meshy.ai",
    siteName: "Meshy Copy",
    type: "website",
    locale: "en_US",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
