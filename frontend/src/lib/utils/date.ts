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
