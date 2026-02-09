import type { Metadata } from 'next'
import { metadata as termsMetadata } from './metadata'

export const metadata: Metadata = termsMetadata

export default function TermsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return children
}
