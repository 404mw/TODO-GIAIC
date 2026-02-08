/**
 * Public Pages Layout (T151)
 * Phase 13 - Public Pages
 *
 * Shared layout for all public (marketing) pages:
 * - Landing page
 * - Pricing page
 * - Contact page
 * - About page
 *
 * Includes shared navigation header and footer.
 * Updated with mobile menu support.
 */

'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Footer } from '@/components/public/Footer'
import { MobileMenu } from '@/components/public/MobileMenu'

interface PublicLayoutProps {
  children: React.ReactNode
}

export default function PublicLayout({ children }: PublicLayoutProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Navigation Header */}
      <nav className="fixed top-0 z-50 w-full border-b border-white/10 bg-gray-950/80 backdrop-blur-md">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
                <span className="text-lg font-bold text-white">P</span>
              </div>
              <span className="text-xl font-bold text-white">
                Perpetua
              </span>
            </Link>

            {/* Navigation Links */}
            <div className="hidden items-center gap-8 md:flex">
              <Link
                href="/"
                className="text-sm font-medium text-gray-400 transition-colors hover:text-white"
              >
                Home
              </Link>
              <Link
                href="/pricing"
                className="text-sm font-medium text-gray-400 transition-colors hover:text-white"
              >
                Pricing
              </Link>
              <Link
                href="/about"
                className="text-sm font-medium text-gray-400 transition-colors hover:text-white"
              >
                About
              </Link>
              <Link
                href="/contact"
                className="text-sm font-medium text-gray-400 transition-colors hover:text-white"
              >
                Contact
              </Link>
            </div>

            {/* Mobile Hamburger + CTA Button */}
            <div className="flex items-center gap-4">
              {/* Hamburger button - visible on mobile only */}
              <button
                onClick={() => setIsMobileMenuOpen(true)}
                className="md:hidden rounded-md p-2 text-gray-400 hover:text-white transition-colors"
                aria-label="Open menu"
              >
                <svg
                  className="h-6 w-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              </button>

              {/* Get Started CTA Button */}
              <Link
                href="/dashboard"
                className="rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 px-4 py-2 text-sm font-medium text-white transition-all hover:from-blue-600 hover:to-purple-700"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content - add padding for fixed nav */}
      <main className="pt-16">
        {children}
      </main>

      {/* Footer */}
      <Footer />

      {/* Mobile Menu */}
      <MobileMenu
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />
    </div>
  )
}
