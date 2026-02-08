import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Terms of Service - Perpetua Flow | Task Management Platform',
  description:
    'Read the terms of service and user agreement for Perpetua Flow, a productivity and task management platform with AI-powered features.',
  keywords: [
    'terms of service',
    'user agreement',
    'legal',
    'terms and conditions',
    'Perpetua Flow',
    'task management',
    'productivity app',
  ],
  openGraph: {
    title: 'Terms of Service - Perpetua Flow',
    description:
      'Read our terms of service and user agreement for using Perpetua Flow task management platform.',
    type: 'website',
    locale: 'en_US',
    siteName: 'Perpetua Flow',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Perpetua Flow - Terms of Service',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Terms of Service - Perpetua Flow',
    description:
      'Read our terms of service and user agreement for using Perpetua Flow.',
    images: ['/og-image.png'],
  },
}
