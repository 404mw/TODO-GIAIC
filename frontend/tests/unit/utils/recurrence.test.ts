/**
 * Unit tests for recurrence utilities (FR-069, FR-070, FR-073)
 * Task: T102, T103, T104
 * Phase: 6 - US1 Extended - Recurrence
 */

import { RRule } from 'rrule';
import { onTaskComplete, parseRecurrenceRule, isRecurrenceEnded } from '@/lib/utils/recurrence';
import type { Task } from '@/lib/schemas/task.schema';

describe('Recurrence Utils - onTaskComplete', () => {
  beforeEach(() => {
    // Set fixed date for consistent testing
    jest.useFakeTimers();
    jest.setSystemTime(new Date('2026-01-10T12:00:00Z'));
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('T102: generates next instance with correct due date for daily recurrence', () => {
    // GIVEN: A task with daily recurrence
    const task: Task = {
      id: 'task-1',
      title: 'Daily review',
      description: '',
      tags: [],
      priority: 'medium',
      estimatedDuration: null,
      reminders: [],
      recurrence: {
        enabled: true,
        rule: 'FREQ=DAILY;INTERVAL=1',
        timezone: 'UTC',
        instanceGenerationMode: 'on_completion',
        humanReadable: 'Every day',
      },
      hidden: false,
      completed: false,
      completedAt: null,
      createdAt: '2026-01-09T12:00:00Z',
      updatedAt: '2026-01-09T12:00:00Z',
      parentTaskId: null,
      isRecurringInstance: false,
    };

    // WHEN: Task is completed
    const nextInstance = onTaskComplete(task);

    // THEN: Next instance is generated with tomorrow's due date
    expect(nextInstance).not.toBeNull();
    expect(nextInstance!.id).not.toBe(task.id); // New UUID
    expect(nextInstance!.completed).toBe(false);
    expect(nextInstance!.completedAt).toBeNull();
    expect(nextInstance!.isRecurringInstance).toBe(true);
    expect(nextInstance!.parentRecurringTaskId).toBe(task.id);
    expect(nextInstance!.dueDate).toBe('2026-01-11T12:00:00.000Z'); // Tomorrow
  });

  test('T102: generates next instance for weekly recurrence', () => {
    // GIVEN: A task with weekly recurrence (every Monday)
    const task: Task = {
      id: 'task-2',
      title: 'Weekly review',
      description: '',
      tags: [],
      priority: 'high',
      estimatedDuration: null,
      reminders: [],
      recurrence: {
        enabled: true,
        rule: 'FREQ=WEEKLY;INTERVAL=1;BYDAY=MO',
        timezone: 'UTC',
        instanceGenerationMode: 'on_completion',
        humanReadable: 'Every week on Monday',
      },
      hidden: false,
      completed: false,
      completedAt: null,
      createdAt: '2026-01-05T12:00:00Z', // Previous Monday
      updatedAt: '2026-01-05T12:00:00Z',
      parentTaskId: null,
      isRecurringInstance: false,
    };

    // WHEN: Task is completed on Friday (2026-01-10 is Friday)
    const nextInstance = onTaskComplete(task);

    // THEN: Next instance is generated for next Monday (2026-01-12)
    expect(nextInstance).not.toBeNull();
    expect(nextInstance!.dueDate).toBe('2026-01-12T12:00:00.000Z'); // Next Monday
  });

  test('T102: generates next instance for custom interval (every 2 weeks)', () => {
    // GIVEN: A task with bi-weekly recurrence
    const task: Task = {
      id: 'task-3',
      title: 'Bi-weekly review',
      description: '',
      tags: [],
      priority: 'medium',
      estimatedDuration: null,
      reminders: [],
      recurrence: {
        enabled: true,
        rule: 'FREQ=WEEKLY;INTERVAL=2;BYDAY=TU',
        timezone: 'UTC',
        instanceGenerationMode: 'on_completion',
        humanReadable: 'Every 2 weeks on Tuesday',
      },
      hidden: false,
      completed: false,
      completedAt: null,
      createdAt: '2025-12-31T12:00:00Z', // 2 weeks ago
      updatedAt: '2025-12-31T12:00:00Z',
      parentTaskId: null,
      isRecurringInstance: false,
    };

    // WHEN: Task is completed on Friday Jan 10, 2026
    // Note: "Every 2 weeks on Tuesday" from Dec 31
    // First Tuesday after Dec 31 = Jan 6
    // Next Tuesday (2 weeks later) = Jan 20
    const nextInstance = onTaskComplete(task);

    // THEN: Next instance is generated for 2 weeks later (Jan 20)
    expect(nextInstance).not.toBeNull();
    expect(nextInstance!.dueDate).toBe('2026-01-20T12:00:00.000Z'); // Next bi-weekly Tuesday
  });

  test('T102: returns null when recurrence is disabled', () => {
    // GIVEN: A task with disabled recurrence
    const task: Task = {
      id: 'task-4',
      title: 'One-time task',
      description: '',
      tags: [],
      priority: 'low',
      estimatedDuration: null,
      reminders: [],
      recurrence: {
        enabled: false,
        rule: 'FREQ=DAILY;INTERVAL=1',
        timezone: 'UTC',
        instanceGenerationMode: 'on_completion',
        humanReadable: 'Every day',
      },
      hidden: false,
      completed: false,
      completedAt: null,
      createdAt: '2026-01-10T12:00:00Z',
      updatedAt: '2026-01-10T12:00:00Z',
      parentTaskId: null,
      isRecurringInstance: false,
    };

    // WHEN: Task is completed
    const nextInstance = onTaskComplete(task);

    // THEN: No next instance is generated
    expect(nextInstance).toBeNull();
  });

  test('T102: returns null when task has no recurrence', () => {
    // GIVEN: A task without recurrence
    const task: Task = {
      id: 'task-5',
      title: 'No recurrence',
      description: '',
      tags: [],
      priority: 'medium',
      estimatedDuration: null,
      reminders: [],
      recurrence: undefined,
      hidden: false,
      completed: false,
      completedAt: null,
      createdAt: '2026-01-10T12:00:00Z',
      updatedAt: '2026-01-10T12:00:00Z',
      parentTaskId: null,
      isRecurringInstance: false,
    };

    // WHEN: Task is completed
    const nextInstance = onTaskComplete(task);

    // THEN: No next instance is generated
    expect(nextInstance).toBeNull();
  });
});

describe('Recurrence Utils - parseRecurrenceRule', () => {
  test('T103: parses and validates daily recurrence pattern', () => {
    // GIVEN: A daily RRule string
    const ruleString = 'FREQ=DAILY;INTERVAL=1';

    // WHEN: Rule is parsed
    const result = parseRecurrenceRule(ruleString);

    // THEN: Rule is valid and parsed correctly
    expect(result.isValid).toBe(true);
    expect(result.error).toBeUndefined();
    expect(result.rrule).toBeDefined();
    expect(result.rrule!.options.freq).toBe(RRule.DAILY);
    expect(result.rrule!.options.interval).toBe(1);
  });

  test('T103: parses and validates weekly recurrence with specific days', () => {
    // GIVEN: A weekly RRule string with BYDAY
    const ruleString = 'FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,WE,FR';

    // WHEN: Rule is parsed
    const result = parseRecurrenceRule(ruleString);

    // THEN: Rule is valid and includes weekdays
    expect(result.isValid).toBe(true);
    expect(result.rrule).toBeDefined();
    expect(result.rrule!.options.freq).toBe(RRule.WEEKLY);
    expect(result.rrule!.options.byweekday).toBeDefined();
    expect(result.rrule!.options.byweekday).toHaveLength(3);
  });

  test('T103: parses and validates monthly recurrence', () => {
    // GIVEN: A monthly RRule string
    const ruleString = 'FREQ=MONTHLY;INTERVAL=1';

    // WHEN: Rule is parsed
    const result = parseRecurrenceRule(ruleString);

    // THEN: Rule is valid
    expect(result.isValid).toBe(true);
    expect(result.rrule!.options.freq).toBe(RRule.MONTHLY);
  });

  test('T103: rejects invalid RRule pattern', () => {
    // GIVEN: An invalid RRule string
    const ruleString = 'INVALID_PATTERN';

    // WHEN: Rule is parsed
    const result = parseRecurrenceRule(ruleString);

    // THEN: Rule is invalid with error message
    expect(result.isValid).toBe(false);
    expect(result.error).toBeDefined();
    expect(result.rrule).toBeUndefined();
  });
});

describe('Recurrence Utils - isRecurrenceEnded', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    jest.setSystemTime(new Date('2026-01-10T12:00:00Z'));
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('T104: detects recurrence ended after COUNT limit reached', () => {
    // GIVEN: A recurrence with COUNT=5 and 5 instances already generated
    const ruleString = 'FREQ=DAILY;INTERVAL=1;COUNT=5';
    const instancesGenerated = 5;

    // WHEN: Checking if recurrence has ended
    const hasEnded = isRecurrenceEnded(ruleString, instancesGenerated);

    // THEN: Recurrence has ended
    expect(hasEnded).toBe(true);
  });

  test('T104: detects recurrence not ended before COUNT limit', () => {
    // GIVEN: A recurrence with COUNT=10 and only 5 instances generated
    const ruleString = 'FREQ=DAILY;INTERVAL=1;COUNT=10';
    const instancesGenerated = 5;

    // WHEN: Checking if recurrence has ended
    const hasEnded = isRecurrenceEnded(ruleString, instancesGenerated);

    // THEN: Recurrence has not ended
    expect(hasEnded).toBe(false);
  });

  test('T104: detects recurrence ended after UNTIL date passed', () => {
    // GIVEN: A recurrence with UNTIL date in the past
    const ruleString = 'FREQ=DAILY;INTERVAL=1;UNTIL=20260105T120000Z'; // 5 days ago
    const instancesGenerated = 5;

    // WHEN: Checking if recurrence has ended
    const hasEnded = isRecurrenceEnded(ruleString, instancesGenerated);

    // THEN: Recurrence has ended
    expect(hasEnded).toBe(true);
  });

  test('T104: detects recurrence not ended before UNTIL date', () => {
    // GIVEN: A recurrence with UNTIL date in the future
    const ruleString = 'FREQ=DAILY;INTERVAL=1;UNTIL=20260120T120000Z'; // 10 days from now
    const instancesGenerated = 5;

    // WHEN: Checking if recurrence has ended
    const hasEnded = isRecurrenceEnded(ruleString, instancesGenerated);

    // THEN: Recurrence has not ended
    expect(hasEnded).toBe(false);
  });

  test('T104: detects infinite recurrence (no COUNT or UNTIL)', () => {
    // GIVEN: A recurrence with no COUNT or UNTIL
    const ruleString = 'FREQ=DAILY;INTERVAL=1';
    const instancesGenerated = 100;

    // WHEN: Checking if recurrence has ended
    const hasEnded = isRecurrenceEnded(ruleString, instancesGenerated);

    // THEN: Recurrence has not ended (infinite)
    expect(hasEnded).toBe(false);
  });
});
