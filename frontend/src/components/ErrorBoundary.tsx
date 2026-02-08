'use client'

import { Component } from 'react'
import type { ReactNode, ErrorInfo } from 'react'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode | ((error: Error, reset: () => void) => ReactNode)
}

interface ErrorBoundaryState {
  error: Error | null
}

/**
 * Error boundary for catching React rendering errors.
 *
 * Provides a fallback UI when a child component throws during rendering.
 * Supports both static fallback elements and render-prop functions with reset capability.
 *
 * @example
 * // Static fallback
 * <ErrorBoundary fallback={<p>Something went wrong</p>}>
 *   <MyComponent />
 * </ErrorBoundary>
 *
 * @example
 * // Render-prop with reset
 * <ErrorBoundary fallback={(error, reset) => (
 *   <div>
 *     <p>{error.message}</p>
 *     <button onClick={reset}>Try again</button>
 *   </div>
 * )}>
 *   <MyComponent />
 * </ErrorBoundary>
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('[ErrorBoundary] Caught error:', error, errorInfo)
  }

  private reset = () => {
    this.setState({ error: null })
  }

  render() {
    const { error } = this.state
    const { children, fallback } = this.props

    if (error) {
      if (typeof fallback === 'function') {
        return fallback(error, this.reset)
      }

      if (fallback) {
        return fallback
      }

      // Default fallback
      return (
        <div role="alert" style={{ padding: '1rem', textAlign: 'center' }}>
          <h2>Something went wrong</h2>
          <p style={{ color: '#666', marginTop: '0.5rem' }}>{error.message}</p>
          <button
            onClick={this.reset}
            style={{
              marginTop: '1rem',
              padding: '0.5rem 1rem',
              cursor: 'pointer',
            }}
          >
            Try again
          </button>
        </div>
      )
    }

    return children
  }
}
