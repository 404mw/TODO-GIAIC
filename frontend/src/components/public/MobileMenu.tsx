/**
 * Mobile Menu Component
 *
 * Responsive slide-in menu for mobile navigation on public pages.
 * Features:
 * - Slide-in animation from right
 * - Semi-transparent backdrop overlay
 * - Click-to-dismiss (backdrop or close button)
 * - Escape key handler
 * - Body scroll lock when open
 * - Full keyboard navigation support
 * - ARIA labels for accessibility
 */

'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'

interface MobileMenuProps {
  isOpen: boolean
  onClose: () => void
}

export function MobileMenu({ isOpen, onClose }: MobileMenuProps) {
  // Escape key handler
  useEffect(() => {
    if (!isOpen) return

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  // Body scroll lock
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }

    return () => {
      document.body.style.overflow = ''
    }
  }, [isOpen])

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
            aria-hidden="true"
          />

          {/* Menu panel */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed right-0 top-0 z-50 h-full w-64 border-l border-white/10 bg-gray-950 shadow-xl"
            role="dialog"
            aria-modal="true"
            aria-label="Mobile navigation menu"
          >
            {/* Header with close button */}
            <div className="flex items-center justify-between border-b border-white/10 p-4">
              <span className="text-lg font-bold text-white">Menu</span>
              <button
                onClick={onClose}
                className="rounded-md p-2 text-gray-400 transition-colors hover:bg-white/5 hover:text-white"
                aria-label="Close menu"
              >
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>

            {/* Navigation links */}
            <nav className="flex flex-col gap-1 p-4">
              <Link
                href="/"
                onClick={onClose}
                className="block rounded-lg px-4 py-3 text-sm font-medium text-gray-300 transition-colors hover:bg-white/5 hover:text-white"
              >
                Home
              </Link>
              <Link
                href="/pricing"
                onClick={onClose}
                className="block rounded-lg px-4 py-3 text-sm font-medium text-gray-300 transition-colors hover:bg-white/5 hover:text-white"
              >
                Pricing
              </Link>
              <Link
                href="/about"
                onClick={onClose}
                className="block rounded-lg px-4 py-3 text-sm font-medium text-gray-300 transition-colors hover:bg-white/5 hover:text-white"
              >
                About
              </Link>
              <Link
                href="/contact"
                onClick={onClose}
                className="block rounded-lg px-4 py-3 text-sm font-medium text-gray-300 transition-colors hover:bg-white/5 hover:text-white"
              >
                Contact
              </Link>

              {/* Divider */}
              <div className="my-2 border-t border-white/10" />

              {/* Get Started CTA */}
              <Link
                href="/dashboard"
                onClick={onClose}
                className="block rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 px-4 py-3 text-center text-sm font-medium text-white transition-all hover:from-blue-600 hover:to-purple-700"
              >
                Get Started
              </Link>
            </nav>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
