/**
 * Animation utilities for Framer Motion
 */

/**
 * Stagger container variant for animating children with a delay
 */
export const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.05,
    },
  },
};

/**
 * Default gradient blob configuration for animated backgrounds
 */
export const DEFAULT_GRADIENT_BLOBS = [
  {
    id: 'blob-1',
    color: 'from-blue-400/30 to-purple-400/30',
    size: 400,
    position: 'top-0 left-0',
    blur: 'blur-3xl',
    initialX: -100,
    initialY: -100,
    animateX: 100,
    animateY: 100,
    duration: 25,
  },
  {
    id: 'blob-2',
    color: 'from-pink-400/30 to-orange-400/30',
    size: 400,
    position: 'bottom-0 right-0',
    blur: 'blur-3xl',
    initialX: 100,
    initialY: 100,
    animateX: -100,
    animateY: -100,
    duration: 20,
  },
  {
    id: 'blob-3',
    color: 'from-green-400/20 to-teal-400/20',
    size: 350,
    position: 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2',
    blur: 'blur-3xl',
    initialX: 0,
    initialY: -50,
    animateX: 0,
    animateY: 50,
    duration: 30,
  },
];

/**
 * Create a blob transition animation configuration
 */
export function createBlobTransition(duration: number = 20) {
  return {
    duration,
    repeat: Infinity,
    repeatType: 'reverse' as const,
    ease: 'easeInOut' as const,
  };
}

/**
 * Fade in animation variant
 */
export const fadeIn = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  },
};

/**
 * Slide up animation variant
 */
export const slideUp = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  },
};

/**
 * Scale animation variant
 */
export const scale = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
};
