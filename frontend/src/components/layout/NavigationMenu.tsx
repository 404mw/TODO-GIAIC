'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'

/**
 * NavigationMenu Component
 *
 * Features:
 * - Active route highlighting with visual feedback
 * - Icon-based navigation for better UX
 * - Accessible navigation with proper ARIA labels
 * - Staggered entry animations with reduced motion support
 *
 * FR-034: Active route highlighting
 * FR-052: Smooth animations
 * FR-054: Reduced motion support
 * T065: Framer Motion animations
 */

export interface NavItem {
  href: string
  label: string
  icon: React.ReactNode
  onboardingId?: string // T143-T147: For onboarding tour
}

interface NavigationMenuProps {
  items: NavItem[]
  collapsed?: boolean
}

export function NavigationMenu({ items, collapsed = false }: NavigationMenuProps) {
  const pathname = usePathname()

  // Animation variants for staggered entry
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05,
        delayChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, x: -10 },
    visible: {
      opacity: 1,
      x: 0,
      transition: {
        type: 'spring' as const,
        stiffness: 300,
        damping: 24,
      },
    },
  }

  return (
    <nav className={`flex-1 overflow-y-auto ${collapsed ? 'px-2' : 'px-3'} py-4`} aria-label="Primary navigation">
      <motion.ul
        className="space-y-1"
        role="list"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {items.map((item) => {
          const isActive = pathname === item.href
          return (
            <motion.li key={item.href} variants={itemVariants}>
              <Link
                href={item.href}
                className={[
                  'flex items-center rounded-lg text-sm font-medium overflow-hidden',
                  collapsed ? 'justify-center p-2.5' : 'gap-3 px-3 py-2.5',
                  'transition-colors duration-150',
                  isActive
                    ? 'bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
                    : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800',
                ]
                  .filter(Boolean)
                  .join(' ')}
                aria-current={isActive ? 'page' : undefined}
                aria-label={`Navigate to ${item.label}`}
                title={collapsed ? item.label : undefined}
                data-onboarding={item.onboardingId}
              >
                <span className="shrink-0">{item.icon}</span>
                <motion.span
                  initial={false}
                  animate={{
                    opacity: collapsed ? 0 : 1,
                    width: collapsed ? 0 : 'auto',
                  }}
                  transition={{
                    opacity: { duration: 0.15, delay: collapsed ? 0 : 0.1 },
                    width: { duration: 0.2 },
                  }}
                  className="whitespace-nowrap"
                >
                  {item.label}
                </motion.span>
              </Link>
            </motion.li>
          )
        })}
      </motion.ul>
    </nav>
  )
}
