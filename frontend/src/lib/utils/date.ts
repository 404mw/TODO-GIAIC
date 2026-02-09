import { format, formatDistanceToNow, isPast } from 'date-fns';

export function formatDate(date: string | Date): string {
  return format(new Date(date), 'MMM d, yyyy');
}

export function formatDateTime(date: string | Date): string {
  return format(new Date(date), 'MMM d, yyyy h:mm a');
}

export function formatRelativeTime(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
}

export function formatTime(date: string | Date): string {
  return format(new Date(date), 'h:mm a');
}

export function isOverdue(date: string | Date): boolean {
  return isPast(new Date(date));
}

export function isSameDay(date1: string | Date, date2: string | Date): boolean {
  const d1 = new Date(date1);
  const d2 = new Date(date2);
  return d1.toDateString() === d2.toDateString();
}

/**
 * Format reminder offset in minutes to human-readable string
 * Negative values = before, positive = after, 0 = at time
 */
export function formatReminderOffset(offsetMinutes: number): string {
  if (offsetMinutes === 0) {
    return 'At due time';
  }

  const absMinutes = Math.abs(offsetMinutes);
  const isBefore = offsetMinutes < 0;
  const prefix = isBefore ? 'before' : 'after';

  if (absMinutes < 60) {
    return `${absMinutes} min ${prefix}`;
  }

  const hours = Math.floor(absMinutes / 60);
  const minutes = absMinutes % 60;

  if (hours < 24) {
    if (minutes === 0) {
      return `${hours} hour${hours > 1 ? 's' : ''} ${prefix}`;
    }
    return `${hours}h ${minutes}m ${prefix}`;
  }

  const days = Math.floor(hours / 24);
  const remainingHours = hours % 24;

  if (remainingHours === 0) {
    return `${days} day${days > 1 ? 's' : ''} ${prefix}`;
  }

  return `${days}d ${remainingHours}h ${prefix}`;
}

/**
 * Calculate the actual trigger time for a reminder based on task due date and offset
 */
export function calculateReminderTriggerTime(
  taskDueDate: string | Date,
  offsetMinutes: number
): Date {
  const dueDate = new Date(taskDueDate);
  const triggerTime = new Date(dueDate.getTime() + offsetMinutes * 60 * 1000);
  return triggerTime;
}
