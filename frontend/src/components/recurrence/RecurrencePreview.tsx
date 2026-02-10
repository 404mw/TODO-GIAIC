/**
 * RecurrencePreview Component (FR-069)
 * Task: T105, T109
 * Phase: 6 - US1 Extended - Recurrence
 *
 * Displays next N occurrences with date-fns formatting
 * Shows preview of upcoming recurring task instances
 */

'use client';

import { useMemo } from 'react';
import { format } from 'date-fns';
import { getNextOccurrences } from '@/lib/utils/recurrence';

export interface RecurrencePreviewProps {
  rrule: string;
  count?: number;
}

export function RecurrencePreview({ rrule, count = 5 }: RecurrencePreviewProps) {
  // Get next N occurrences
  const occurrences = useMemo(() => {
    return getNextOccurrences(rrule, count);
  }, [rrule, count]);

  // Handle invalid rule
  if (occurrences.length === 0) {
    return (
      <div className="rounded-md border border-red-200 bg-red-50 p-3 dark:border-red-800 dark:bg-red-950">
        <p className="text-sm text-red-700 dark:text-red-300">Invalid recurrence pattern or no future occurrences</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Next {count} occurrences:</h4>
      <ul className="space-y-1">
        {occurrences.map((date, index) => (
          <li
            key={index}
            className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400"
          >
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-blue-100 text-xs font-medium text-blue-700 dark:bg-blue-900 dark:text-blue-300">
              {index + 1}
            </span>
            <span>{format(date, 'PPP')}</span>
            {/* PPP = Jan 10, 2026 */}
          </li>
        ))}
      </ul>
    </div>
  );
}
