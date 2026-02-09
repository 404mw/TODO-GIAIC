import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Pricing - Perpetua Flow | Free & Pro Plans',
  description:
    'Choose the perfect plan for your productivity needs. Start free with up to 50 tasks, or upgrade to Pro for unlimited tasks and AI-powered features.',
  keywords: [
    'pricing',
    'free plan',
    'pro plan',
    'productivity app pricing',
    'task management pricing',
    'subscription',
  ],
  openGraph: {
    title: 'Pricing - Perpetua Flow',
    description:
      'Choose the perfect plan for your productivity needs. Start free or upgrade to Pro.',
    type: 'website',
    locale: 'en_US',
    siteName: 'Perpetua Flow',
    images: [
      {
        url: '/og-pricing.png',
        width: 1200,
        height: 630,
        alt: 'Perpetua Flow Pricing Plans',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Pricing - Perpetua Flow',
    description: 'Start free or upgrade to Pro for unlimited productivity.',
    images: ['/og-pricing.png'],
  },
}
