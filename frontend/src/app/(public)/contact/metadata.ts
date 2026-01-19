import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Contact Us - Perpetua Flow | Get in Touch',
  description:
    'Have questions or feedback? Contact the Perpetua Flow team. We are here to help you get the most out of your productivity journey.',
  keywords: ['contact', 'support', 'feedback', 'help', 'customer service'],
  openGraph: {
    title: 'Contact Us - Perpetua Flow',
    description: 'Have questions or feedback? Get in touch with the Perpetua Flow team.',
    type: 'website',
    locale: 'en_US',
    siteName: 'Perpetua Flow',
    images: [
      {
        url: '/og-contact.png',
        width: 1200,
        height: 630,
        alt: 'Contact Perpetua Flow',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Contact Us - Perpetua Flow',
    description: 'Get in touch with the Perpetua Flow team.',
    images: ['/og-contact.png'],
  },
}
