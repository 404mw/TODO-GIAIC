/**
 * FeatureCard Component (T153)
 * Phase 13 - Public Pages
 *
 * Glassmorphic feature card with backdrop blur for landing page.
 * Used to display product features with icons and descriptions.
 *
 * FR-065: Glassmorphism and backdrop blur effects
 */

'use client'

import { motion } from 'framer-motion'
import { useReducedMotion } from '@/lib/hooks/useReducedMotion'

interface FeatureCardProps {
  icon: React.ReactNode
  title: string
  message: string
  iconBgColor?: string
  index?: number
}

export function FeatureCard({
  icon,
  title,
  message,
  iconBgColor = 'from-blue-500/20 to-purple-500/20',
  index = 0,
}: FeatureCardProps) {
  const shouldReduceMotion = useReducedMotion()

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.4,
        delay: index * 0.1,
        ease: 'easeOut' as const,
      },
    },
  }

  return (
    <motion.div
      variants={shouldReduceMotion ? {} : cardVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-50px' }}
      className="group relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-md transition-all duration-300 hover:border-white/20 hover:bg-white/10"
    >
      {/* Gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 opacity-0 transition-opacity duration-300 group-hover:opacity-100" />

      {/* Content */}
      <div className="relative z-10">
        {/* Icon container */}
        <div
          className={`mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${iconBgColor}`}
        >
          {icon}
        </div>

        {/* Title */}
        <h3 className="mb-2 text-lg font-semibold text-white">
          {title}
        </h3>

        {/* Description */}
        <p className="text-sm leading-relaxed text-gray-400">
          {message}
        </p>
      </div>

      {/* Decorative corner accent */}
      <div className="absolute -right-8 -top-8 h-24 w-24 rounded-full bg-gradient-to-br from-blue-500/10 to-purple-500/10 blur-2xl transition-all duration-300 group-hover:scale-150" />
    </motion.div>
  )
}
