/**
 * About Page (T156)
 * Phase 13 - Public Pages
 *
 * About page with:
 * - Project description
 * - Team/mission info
 * - Values section
 * - Dark aesthetic matching other public pages
 *
 * FR-066: About page with project description
 */

'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { useReducedMotion } from '@/lib/hooks/useReducedMotion'

const VALUES = [
  {
    title: 'Simplicity First',
    message:
      'We believe productivity tools should reduce complexity, not add to it. Every feature is designed to be intuitive and accessible.',
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
          d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"
        />
      </svg>
    ),
  },
  {
    title: 'Habit Science',
    message:
      'Perpetua is built on proven habit-forming principles. Streaks, achievements, and visual feedback help you build lasting productivity habits.',
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
          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
        />
      </svg>
    ),
  },
  {
    title: 'Privacy Focused',
    message:
      'Your data belongs to you. We use local storage where possible and never sell your information. Your productivity is your business.',
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
          d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
        />
      </svg>
    ),
  },
  {
    title: 'Accessibility',
    message:
      'Productivity tools should work for everyone. We prioritize WCAG compliance, keyboard navigation, and reduced-motion support.',
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
          d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
        />
      </svg>
    ),
  },
]

const STATS = [
  { label: 'Active Users', value: '10K+' },
  { label: 'Tasks Completed', value: '1M+' },
  { label: 'Streaks Active', value: '5K+' },
  { label: 'Uptime', value: '99.9%' },
]

export default function AboutPage() {
  const shouldReduceMotion = useReducedMotion()

  const fadeIn = shouldReduceMotion
    ? {}
    : {
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.4 },
      }

  const staggerChildren = shouldReduceMotion
    ? {}
    : {
        initial: { opacity: 0 },
        animate: { opacity: 1 },
        transition: { staggerChildren: 0.1 },
      }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden px-4 py-24">
        {/* Background gradient */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute -left-1/4 top-0 h-[500px] w-[500px] rounded-full bg-blue-500/10 blur-3xl" />
          <div className="absolute -right-1/4 top-1/4 h-[500px] w-[500px] rounded-full bg-purple-500/10 blur-3xl" />
        </div>

        <motion.div {...fadeIn} className="relative mx-auto max-w-4xl text-center">
          <h1 className="text-4xl font-bold text-white sm:text-5xl">
            Building the future of
            <span className="block bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              personal productivity
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-400">
            Perpetua was born from a simple idea: productivity should be
            rewarding, not punishing. We're building tools that help you build
            lasting habits while celebrating every small win along the way.
          </p>
        </motion.div>
      </section>

      {/* Stats Section */}
      <section className="border-y border-white/10 bg-white/5 px-4 py-12">
        <div className="mx-auto max-w-6xl">
          <motion.div
            {...staggerChildren}
            className="grid grid-cols-2 gap-8 lg:grid-cols-4"
          >
            {STATS.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-3xl font-bold text-white">{stat.value}</div>
                <div className="mt-1 text-sm text-gray-400">{stat.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="px-4 py-24">
        <div className="mx-auto max-w-4xl">
          <motion.div
            {...fadeIn}
            transition={{ ...fadeIn.transition, delay: 0.1 }}
            className="text-center"
          >
            <h2 className="text-3xl font-bold text-white">Our Mission</h2>
            <div className="mx-auto mt-8 max-w-3xl space-y-6 text-gray-400">
              <p>
                We believe that productivity isn't about doing more—it's about
                doing what matters, consistently. Traditional task managers
                focus on cramming more into your day. Perpetua focuses on
                helping you build sustainable habits that compound over time.
              </p>
              <p>
                Our approach is grounded in behavioral science. Features like
                consistency streaks with grace days, focus mode timers, and
                achievement celebrations aren't gimmicks—they're carefully
                designed to leverage the same psychological principles that make
                habits stick.
              </p>
              <p>
                Whether you're managing personal projects, professional tasks,
                or daily routines, Perpetua adapts to your workflow. We strip
                away the complexity that plagues most productivity tools and
                leave you with what actually matters: getting things done.
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Values Section */}
      <section className="bg-white/5 px-4 py-24">
        <div className="mx-auto max-w-6xl">
          <motion.div {...fadeIn} className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-white">Our Values</h2>
            <p className="mx-auto mt-4 max-w-2xl text-gray-400">
              These principles guide every decision we make, from feature design
              to customer support.
            </p>
          </motion.div>

          <div className="grid gap-6 md:grid-cols-2">
            {VALUES.map((value, index) => (
              <motion.div
                key={value.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                className="rounded-xl border border-white/10 bg-gray-950 p-6"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-white/5">
                  {value.icon}
                </div>
                <h3 className="text-lg font-semibold text-white">
                  {value.title}
                </h3>
                <p className="mt-2 text-gray-400">{value.message}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section className="px-4 py-24">
        <div className="mx-auto max-w-4xl">
          <motion.div {...fadeIn} className="text-center">
            <h2 className="text-3xl font-bold text-white">Built with Modern Tech</h2>
            <p className="mx-auto mt-4 max-w-2xl text-gray-400">
              Perpetua is built with Next.js, React, and TypeScript for a fast,
              reliable, and type-safe experience. We use TailwindCSS for styling
              and Framer Motion for smooth animations.
            </p>
            <div className="mt-12 flex flex-wrap justify-center gap-4">
              {['Next.js', 'React', 'TypeScript', 'TailwindCSS', 'Framer Motion', 'Zod'].map(
                (tech) => (
                  <span
                    key={tech}
                    className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-gray-300"
                  >
                    {tech}
                  </span>
                )
              )}
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-4 py-24">
        <motion.div
          {...fadeIn}
          className="mx-auto max-w-4xl rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 p-12 text-center backdrop-blur-sm"
        >
          <h2 className="text-3xl font-bold text-white">
            Ready to build better habits?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-gray-300">
            Join thousands of users who use Perpetua to stay productive and
            achieve their goals every day.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <Link
              href="/dashboard/tasks"
              className="rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-3 font-medium text-white transition-all hover:from-blue-600 hover:to-purple-700"
            >
              Get Started Free
            </Link>
            <Link
              href="/contact"
              className="rounded-lg border border-white/20 bg-white/5 px-6 py-3 font-medium text-white transition-colors hover:bg-white/10"
            >
              Contact Us
            </Link>
          </div>
        </motion.div>
      </section>
    </div>
  )
}
