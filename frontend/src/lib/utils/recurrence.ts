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

/**
 * Create an RRule string from recurrence parameters
 */
export function createRRuleString(params: {
  freq: 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'YEARLY';
  interval?: number;
  count?: number;
  until?: Date;
  byweekday?: number[];
  bymonthday?: number;
  dtstart?: Date;
}): string {
  try {
    const options: any = {
      freq: RRule[params.freq as keyof typeof RRule],
      interval: params.interval || 1,
    };

    if (params.count) {
      options.count = params.count;
    }

    if (params.until) {
      options.until = params.until;
    }

    if (params.byweekday) {
      options.byweekday = params.byweekday;
    }

    if (params.bymonthday) {
      options.bymonthday = params.bymonthday;
    }

    if (params.dtstart) {
      options.dtstart = params.dtstart;
    }

    const rule = new RRule(options);
    return rule.toString();
  } catch (error) {
    console.error('Failed to create RRule string:', error);
    return '';
  }
}

/**
 * Get human-readable description of recurrence pattern
 */
export function getRecurrenceDescription(rruleString: string): string {
  try {
    const rule = rrulestr(rruleString) as RRule;
    return rule.toText();
  } catch (error) {
    console.error('Failed to get recurrence message:', error);
    return 'Invalid recurrence pattern';
  }
}

/**
 * Get next N occurrences of a recurrence rule
 */
export function getNextOccurrences(
  rruleString: string,
  count: number = 5,
  after?: Date
): Date[] {
  try {
    const rule = rrulestr(rruleString) as RRule;
    const startDate = after || new Date();
    return rule.all((date, i) => i < count && date >= startDate);
  } catch (error) {
    console.error('Failed to get next occurrences:', error);
    return [];
  }
}
