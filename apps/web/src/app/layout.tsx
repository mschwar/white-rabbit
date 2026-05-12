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

const metadataBase = new URL(process.env.NEXT_PUBLIC_SITE_URL ?? 'https://white-rabbit-ten.vercel.app');

export const metadata: Metadata = {
  metadataBase,
  title: {
    default: 'White Rabbit',
    template: '%s | White Rabbit',
  },
  description: 'Evidence-backed prospect categorization.',
  manifest: '/site.webmanifest',
  icons: {
    icon: [{ url: '/favicon.ico' }],
    apple: [{ url: '/apple-touch-icon.png' }],
  },
  openGraph: {
    title: 'White Rabbit',
    description: 'Evidence-backed prospect categorization.',
    images: [
      {
        url: '/brand/white-rabbit-og-light.png',
        width: 1200,
        height: 630,
        alt: 'White Rabbit',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'White Rabbit',
    description: 'Evidence-backed prospect categorization.',
    images: ['/brand/white-rabbit-og-light.png'],
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
