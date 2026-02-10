import type { Metadata } from 'next'
import { metadata as privacyMetadata } from './metadata'

export const metadata: Metadata = privacyMetadata

export default function PrivacyLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
