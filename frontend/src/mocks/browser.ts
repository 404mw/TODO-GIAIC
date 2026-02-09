import { setupWorker } from 'msw/browser'
import { handlers } from './handlers'

/**
 * MSW browser worker for API mocking in development
 *
 * This configures MSW to intercept API requests and return mock responses
 * based on the handlers defined in ./handlers
 *
 * Usage:
 * - Import and start in app initialization (see app/providers.tsx)
 * - Service worker is registered at /mockServiceWorker.js
 * - Only runs in development mode (NODE_ENV !== 'production')
 */
export const worker = setupWorker(...handlers)

/**
 * Start MSW worker with custom configuration
 *
 * @param options - MSW worker start options
 * @returns Promise that resolves when worker is ready
 */
export const startMSW = async (options?: Parameters<typeof worker.start>[0]) => {
  if (typeof window === 'undefined') {
    // Server-side: MSW not needed
    return
  }

  if (process.env.NODE_ENV === 'production') {
    // Don't run MSW in production
    return
  }

  try {
    await worker.start({
      onUnhandledRequest: 'warn', // Warn for unhandled requests
      ...options,
    })
    console.log('[MSW] Mock Service Worker started successfully')
  } catch (error) {
    console.error('[MSW] Failed to start Mock Service Worker:', error)
  }
}
