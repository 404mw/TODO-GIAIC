'use client';

import { useEffect } from 'react';
import { useReportWebVitals } from 'next/web-vitals';

/**
 * Web Vitals metrics interface
 * Follows Core Web Vitals standards from Google
 */
interface WebVitalMetric {
  id: string;
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  navigationType: string;
}

/**
 * Thresholds for Core Web Vitals ratings
 * Based on https://web.dev/vitals/
 */
const THRESHOLDS = {
  LCP: { good: 2500, poor: 4000 }, // Largest Contentful Paint
  FID: { good: 100, poor: 300 },   // First Input Delay
  CLS: { good: 0.1, poor: 0.25 },  // Cumulative Layout Shift
  FCP: { good: 1800, poor: 3000 }, // First Contentful Paint
  TTFB: { good: 800, poor: 1800 }, // Time to First Byte
  INP: { good: 200, poor: 500 },   // Interaction to Next Paint
};

/**
 * Get rating based on metric value and thresholds
 */
function getRating(name: string, value: number): 'good' | 'needs-improvement' | 'poor' {
  const threshold = THRESHOLDS[name as keyof typeof THRESHOLDS];
  if (!threshold) return 'good';

  if (value <= threshold.good) return 'good';
  if (value <= threshold.poor) return 'needs-improvement';
  return 'poor';
}

/**
 * WebVitalsReporter Component
 *
 * Tracks and reports Core Web Vitals metrics for performance monitoring.
 * Metrics are logged in development and can be sent to analytics in production.
 *
 * Metrics tracked:
 * - LCP (Largest Contentful Paint): Loading performance
 * - FID (First Input Delay): Interactivity
 * - CLS (Cumulative Layout Shift): Visual stability
 * - FCP (First Contentful Paint): Initial render speed
 * - TTFB (Time to First Byte): Server response time
 * - INP (Interaction to Next Paint): Overall responsiveness
 */
export function WebVitalsReporter() {
  useReportWebVitals((metric) => {
    const { id, name, value, delta, navigationType } = metric;

    const rating = getRating(name, value);

    const formattedMetric: WebVitalMetric = {
      id,
      name,
      value: Math.round(name === 'CLS' ? value * 1000 : value), // CLS is unitless, others in ms
      rating,
      delta: Math.round(delta),
      navigationType: navigationType || 'unknown',
    };

    // Log in development
    if (process.env.NODE_ENV === 'development') {
      const color = rating === 'good' ? '\x1b[32m' : rating === 'needs-improvement' ? '\x1b[33m' : '\x1b[31m';
      console.log(
        `%c[Web Vitals] ${name}: ${formattedMetric.value}${name === 'CLS' ? '' : 'ms'} (${rating})`,
        `color: ${rating === 'good' ? 'green' : rating === 'needs-improvement' ? 'orange' : 'red'}`
      );
    }

    // TODO: Send to analytics provider in production
    // Example: analytics.track('web_vital', formattedMetric);
  });

  return null;
}

/**
 * Hook to measure custom performance metrics
 *
 * @example
 * const measure = usePerformanceMeasure('task-creation');
 * // Start measurement
 * measure.start();
 * // ... perform operation
 * // End measurement and get duration
 * const duration = measure.end();
 */
export function usePerformanceMeasure(name: string) {
  useEffect(() => {
    // Cleanup marks on unmount
    return () => {
      try {
        performance.clearMarks(`${name}-start`);
        performance.clearMarks(`${name}-end`);
        performance.clearMeasures(name);
      } catch {
        // Ignore errors if marks don't exist
      }
    };
  }, [name]);

  return {
    start: () => {
      performance.mark(`${name}-start`);
    },
    end: (): number => {
      performance.mark(`${name}-end`);
      try {
        const measure = performance.measure(name, `${name}-start`, `${name}-end`);
        return measure.duration;
      } catch {
        return 0;
      }
    },
  };
}

/**
 * Performance observer for long tasks
 * Helps identify JavaScript that blocks the main thread
 */
export function useLongTaskObserver(callback?: (duration: number) => void) {
  useEffect(() => {
    if (typeof window === 'undefined' || !('PerformanceObserver' in window)) {
      return;
    }

    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          const duration = entry.duration;

          if (process.env.NODE_ENV === 'development') {
            console.warn(
              `%c[Performance] Long task detected: ${Math.round(duration)}ms`,
              'color: orange'
            );
          }

          callback?.(duration);
        }
      });

      observer.observe({ type: 'longtask', buffered: true });

      return () => observer.disconnect();
    } catch {
      // PerformanceObserver not supported for longtask
      return undefined;
    }
  }, [callback]);
}
