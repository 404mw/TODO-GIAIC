import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Privacy Policy - Perpetua Flow | Data Protection & GDPR Compliance',
  description:
    'Learn how Perpetua Flow collects, uses, and protects your personal data. GDPR compliant privacy policy with transparency about data practices.',
  keywords: [
    'privacy policy',
    'data protection',
    'GDPR',
    'data privacy',
    'Perpetua Flow',
    'personal data',
    'data security',
    'user privacy',
  ],
  openGraph: {
    title: 'Privacy Policy - Perpetua Flow',
    description:
      'Transparent privacy policy explaining how we protect your data and respect your privacy rights.',
    type: 'website',
    locale: 'en_US',
    siteName: 'Perpetua Flow',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Perpetua Flow - Privacy Policy',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Privacy Policy - Perpetua Flow',
    description:
      'Learn how we collect, use, and protect your personal data with full GDPR compliance.',
    images: ['/og-image.png'],
  },
}
