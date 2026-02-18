/**
 * Landing Page (Root)
 *
 * Marketing landing page at localhost:3000 featuring:
 * - Hero section with animated gradient mesh
 * - Features overview with glassmorphic cards
 * - CTA sections
 * - Public navigation header and footer
 */

'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { FeatureCard } from '@/components/public/FeatureCard'
import { Footer } from '@/components/public/Footer'
import { useReducedMotion } from '@/lib/hooks/useReducedMotion'
import {
  staggerContainer,
  DEFAULT_GRADIENT_BLOBS,
  createBlobTransition,
} from '@/lib/utils/animations'

const FEATURES = [
  {
    title: 'Smart Task Management',
    message:
      'Organize tasks with priorities, due dates, and recurring schedules. Sub-tasks help break down complex projects.',
    iconBgColor: 'from-blue-500/20 to-blue-600/10',
    icon: (
      <svg
        className="h-6 w-6 text-blue-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
        />
      </svg>
    ),
  },
  {
    title: 'Consistency Streaks',
    message:
      'Build lasting habits with streak tracking. Grace days forgive the occasional miss without breaking your momentum.',
    iconBgColor: 'from-orange-500/20 to-orange-600/10',
    icon: (
      <svg
        className="h-6 w-6 text-orange-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"
        />
      </svg>
    ),
  },
  {
    title: 'Focus Mode',
    message:
      'Eliminate distractions with dedicated focus sessions. Timer, notifications, and progress tracking included.',
    iconBgColor: 'from-purple-500/20 to-purple-600/10',
    icon: (
      <svg
        className="h-6 w-6 text-purple-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
  },
  {
    title: 'Smart Reminders',
    message:
      'Never miss a deadline with browser notifications. Customizable sounds and timing keep you informed without disruption.',
    iconBgColor: 'from-green-500/20 to-green-600/10',
    icon: (
      <svg
        className="h-6 w-6 text-green-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>
    ),
  },
  {
    title: 'Quick Notes',
    message:
      'Capture ideas instantly with quick notes. Convert them to tasks when you are ready to take action.',
    iconBgColor: 'from-yellow-500/20 to-yellow-600/10',
    icon: (
      <svg
        className="h-6 w-6 text-yellow-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
        />
      </svg>
    ),
  },
  {
    title: 'Achievements',
    message:
      'Celebrate milestones and track your progress. Earn achievements for completing high-priority tasks and maintaining streaks.',
    iconBgColor: 'from-red-500/20 to-red-600/10',
    icon: (
      <svg
        className="h-6 w-6 text-red-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
        />
      </svg>
    ),
  },
]

export default function LandingPage() {
  const shouldReduceMotion = useReducedMotion()

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

            {/* CTA Buttons */}
            <div className="flex items-center gap-4">
              <Link
                href="/login"
                className="text-sm font-medium text-gray-400 transition-colors hover:text-white"
              >
                Login
              </Link>
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

      {/* Main Content */}
      <main className="pt-16">
        <div className="relative">
          {/* Animated Gradient Mesh Background */}
          <div className="pointer-events-none fixed inset-0 overflow-hidden">
            {!shouldReduceMotion &&
              DEFAULT_GRADIENT_BLOBS.map((blob) => (
                <motion.div
                  key={blob.id}
                  className={`absolute rounded-full bg-gradient-to-br ${blob.color} blur-3xl`}
                  style={{
                    width: `clamp(200px, 30vw, ${blob.size}px)`,
                    height: `clamp(200px, 30vw, ${blob.size}px)`,
                  }}
                  initial={{
                    x: blob.initialX,
                    y: blob.initialY,
                  }}
                  animate={{
                    x: blob.animateX,
                    y: blob.animateY,
                  }}
                  transition={createBlobTransition(blob.duration)}
                />
              ))}
          </div>

          {/* Hero Section */}
          <section className="relative overflow-hidden px-4 py-24 sm:px-6 lg:px-8">
            <div className="relative mx-auto max-w-7xl text-center">
              <motion.h1
                initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                className="text-4xl font-bold tracking-tight text-white sm:text-6xl"
              >
                Stay productive,
                <span className="block bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  every single day
                </span>
              </motion.h1>
              <motion.p
                initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.1 }}
                className="mx-auto mt-6 max-w-2xl text-lg text-gray-400"
              >
                Perpetua helps you build lasting productivity habits with smart task
                management, focus sessions, and achievement tracking. Completely free to start — no credit card required.
              </motion.p>
              <motion.div
                initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.2 }}
                className="mt-10 flex flex-wrap justify-center gap-4"
              >
                <Link
                  href="/dashboard"
                  className="rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-3 text-base font-medium text-white shadow-lg shadow-blue-500/25 transition-all hover:from-blue-600 hover:to-purple-700 hover:shadow-blue-500/40"
                >
                  Start Free Now
                </Link>
                <Link
                  href="#features"
                  className="rounded-lg border border-white/20 bg-white/5 px-6 py-3 text-base font-medium text-white backdrop-blur-sm transition-colors hover:bg-white/10"
                >
                  Learn More
                </Link>
              </motion.div>
            </div>
          </section>

          {/* Free Tier Highlight Section */}
          <section className="relative border-t border-white/10 py-16">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <motion.div
                initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                viewport={{ once: true }}
                className="overflow-hidden rounded-2xl bg-gradient-to-br from-green-500/10 to-emerald-500/10 px-8 py-12 text-center backdrop-blur-sm border border-green-500/20"
              >
                <div className="mx-auto max-w-3xl">
                  <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-green-500/20 px-4 py-1.5 text-sm font-medium text-green-400 border border-green-500/30">
                    <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" />
                    </svg>
                    <span>Start Free - No Credit Card Required</span>
                  </div>
                  <h2 className="text-3xl font-bold text-white mb-4">
                    Everything You Need, Absolutely Free
                  </h2>
                  <p className="text-gray-300 mb-8 text-lg">
                    Get started with Perpetua's powerful core features at zero cost. No trials, no hidden fees.
                  </p>

                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 text-left">
                    <div className="flex items-start gap-3 rounded-lg bg-gray-900/50 p-4 backdrop-blur-sm border border-white/5">
                      <svg className="h-5 w-5 text-green-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <div>
                        <h3 className="font-semibold text-white text-sm">Active Tasks</h3>
                        <p className="text-xs text-gray-400 mt-1">Organize your work effectively</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3 rounded-lg bg-gray-900/50 p-4 backdrop-blur-sm border border-white/5">
                      <svg className="h-5 w-5 text-green-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <div>
                        <h3 className="font-semibold text-white text-sm">Streak Tracking</h3>
                        <p className="text-xs text-gray-400 mt-1">Build consistent habits</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3 rounded-lg bg-gray-900/50 p-4 backdrop-blur-sm border border-white/5">
                      <svg className="h-5 w-5 text-green-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <div>
                        <h3 className="font-semibold text-white text-sm">Quick Notes</h3>
                        <p className="text-xs text-gray-400 mt-1">Capture ideas instantly</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3 rounded-lg bg-gray-900/50 p-4 backdrop-blur-sm border border-white/5">
                      <svg className="h-5 w-5 text-green-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <div>
                        <h3 className="font-semibold text-white text-sm">Focus Mode</h3>
                        <p className="text-xs text-gray-400 mt-1">Eliminate distractions</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3 rounded-lg bg-gray-900/50 p-4 backdrop-blur-sm border border-white/5">
                      <svg className="h-5 w-5 text-green-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <div>
                        <h3 className="font-semibold text-white text-sm">Smart Notifications</h3>
                        <p className="text-xs text-gray-400 mt-1">Never miss a deadline</p>
                      </div>
                    </div>

                    <div className="flex items-start gap-3 rounded-lg bg-gray-900/50 p-4 backdrop-blur-sm border border-white/5">
                      <svg className="h-5 w-5 text-green-400 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <div>
                        <h3 className="font-semibold text-white text-sm">Achievements</h3>
                        <p className="text-xs text-gray-400 mt-1">Track your progress</p>
                      </div>
                    </div>
                  </div>

                  <Link
                    href="/dashboard"
                    className="mt-8 inline-block rounded-lg bg-gradient-to-r from-green-500 to-emerald-600 px-8 py-3 text-base font-medium text-white shadow-lg shadow-green-500/25 transition-all hover:from-green-600 hover:to-emerald-700 hover:shadow-green-500/40"
                  >
                    Start Using Perpetua Free
                  </Link>
                </div>
              </motion.div>
            </div>
          </section>

          {/* Features Section */}
          <section id="features" className="relative border-t border-white/10 py-24">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <motion.div
                initial={shouldReduceMotion ? {} : { opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <h2 className="text-3xl font-bold text-white">
                  Everything you need to stay on track
                </h2>
                <p className="mx-auto mt-4 max-w-2xl text-gray-400">
                  Built with productivity science in mind, Perpetua gives you the
                  tools to build and maintain productive habits.
                </p>
              </motion.div>

              <motion.div
                variants={shouldReduceMotion ? {} : staggerContainer}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: '-100px' }}
                className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
              >
                {FEATURES.map((feature, index) => (
                  <FeatureCard
                    key={feature.title}
                    icon={feature.icon}
                    title={feature.title}
                    message={feature.message}
                    iconBgColor={feature.iconBgColor}
                    index={index}
                  />
                ))}
              </motion.div>
            </div>
          </section>

          {/* CTA Section */}
          <section className="relative px-4 py-24 sm:px-6 lg:px-8">
            <div className="mx-auto max-w-7xl">
              <motion.div
                initial={shouldReduceMotion ? {} : { opacity: 0, scale: 0.98 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4 }}
                viewport={{ once: true }}
                className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 px-8 py-16 text-center backdrop-blur-sm sm:px-12"
              >
                {/* Decorative gradient */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10" />

                <div className="relative z-10">
                  <h2 className="text-3xl font-bold text-white">
                    Ready to build better habits?
                  </h2>
                  <p className="mx-auto mt-4 max-w-xl text-gray-300">
                    Join thousands of people who use Perpetua to stay productive and
                    achieve their goals every day. Start for free — no credit card, no commitments.
                  </p>
                  <Link
                    href="/dashboard"
                    className="mt-8 inline-block rounded-lg bg-white px-6 py-3 text-base font-medium text-gray-900 transition-colors hover:bg-gray-100"
                  >
                    Get Started Free
                  </Link>
                  <p className="mt-4 text-sm text-gray-400">
                    ✨ Free tier includes 50 tasks, streaks, notes, and more
                  </p>
                </div>
              </motion.div>
            </div>
          </section>

          {/* Open Source Section */}
          <section className="relative border-t border-white/10 py-12">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
              <div className="flex flex-col items-center justify-center gap-4 text-center">
                <div className="flex items-center gap-2 text-gray-400">
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                  </svg>
                  <span className="text-lg font-medium">Proudly Open Source</span>
                </div>
                <p className="max-w-2xl text-sm text-gray-500">
                  Perpetua is open source and built in public to ensure complete transparency. Review the codebase to understand its architecture, decisions, and ongoing development.
                </p>
                <a
                  href="https://github.com/404mw/TODO-GIAIC/tree/002-perpetua-frontend"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-lg border border-white/20 bg-white/5 px-4 py-2 text-sm font-medium text-white backdrop-blur-sm transition-colors hover:bg-white/10"
                >
                  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                  </svg>
                  View on GitHub
                </a>
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <Footer />
    </div>
  )
}
