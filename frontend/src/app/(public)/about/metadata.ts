import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'About - Perpetua Flow | Our Mission & Values',
  description:
    'Learn about Perpetua Flow and our mission to help people build lasting productivity habits through simplicity, habit science, and privacy-first design.',
  keywords: [
    'about perpetua',
    'productivity mission',
    'company values',
    'habit science',
    'privacy first',
  ],
  openGraph: {
    title: 'About - Perpetua Flow',
    description:
      'Our mission is to help people build lasting productivity habits through simplicity and habit science.',
    type: 'website',
    locale: 'en_US',
    siteName: 'Perpetua Flow',
    images: [
      {
        url: '/og-about.png',
        width: 1200,
        height: 630,
        alt: 'About Perpetua Flow',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'About - Perpetua Flow',
    description: 'Learn about our mission to help people build lasting productivity habits.',
    images: ['/og-about.png'],
  },
}
