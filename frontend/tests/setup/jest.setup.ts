import '@testing-library/jest-dom'
// import { server } from '@/mocks/server'

// Establish API mocking before all tests
// FIXME: MSW has ES module issues in Jest on Windows
// beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))

// Reset any request handlers that we may add during the tests,
// so they don't affect other tests
// afterEach(() => server.resetHandlers())

// Clean up after the tests are finished
// afterAll(() => server.close())

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return []
  }
  unobserve() {}
} as any

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
} as any
