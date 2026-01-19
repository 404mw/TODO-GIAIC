import { setupServer } from 'msw/node'
import { handlers } from './handlers'

/**
 * MSW server for API mocking in Node.js environment (Jest tests)
 *
 * This configures MSW to intercept API requests in Node.js and return mock responses
 * based on the handlers defined in ./handlers
 *
 * Usage:
 * - Import in Jest setup file (tests/setup/jest.setup.ts)
 * - Call server.listen() before all tests
 * - Call server.resetHandlers() after each test
 * - Call server.close() after all tests
 */
export const server = setupServer(...handlers)
