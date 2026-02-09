import { RRule, RRuleSet, rrulestr } from 'rrule';

export function parseRecurrence(rruleString: string): RRule | null {
  try {
    return rrulestr(rruleString) as RRule;
  } catch (error) {
    console.error('Failed to parse recurrence rule:', error);
    return null;
  }
}

export function getNextOccurrence(rruleString: string, after?: Date): Date | null {
  try {
    const rule = rrulestr(rruleString) as RRule;
    return rule.after(after || new Date(), true);
  } catch (error) {
    console.error('Failed to get next occurrence:', error);
    return null;
  }
}

export function formatRecurrence(rruleString: string): string {
  try {
    const rule = rrulestr(rruleString) as RRule;
    return rule.toText();
  } catch (error) {
    console.error('Failed to format recurrence:', error);
    return 'Invalid recurrence rule';
  }
}

export function getAllOccurrences(
  rruleString: string,
  start: Date,
  end: Date
): Date[] {
  try {
    const rule = rrulestr(rruleString) as RRule;
    return rule.between(start, end, true);
  } catch (error) {
    console.error('Failed to get occurrences:', error);
    return [];
  }
}
