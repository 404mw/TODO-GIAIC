import { calculateReminderTriggerTime } from '@/lib/utils/date';
import type { Reminder } from '@/lib/schemas/reminder.schema';
import type { Task } from '@/lib/schemas/task.schema';

describe('calculateReminderTriggerTime', () => {
  const baseTask: Task = {
    id: 'task-1',
    title: 'Test Task',
    description: '',
    tags: [],
    priority: 'medium',
    estimatedDuration: null,
    reminders: [],
    hidden: false,
    completed: false,
    completedAt: null,
    dueDate: '2026-01-15T14:00:00.000Z', // 2pm UTC - ISO string format
    createdAt: '2026-01-10T10:00:00Z',
    updatedAt: '2026-01-10T10:00:00Z',
    parentTaskId: null,
    isRecurringInstance: false,
  };

  // Helper function to create a reminder with the correct timing structure
  const createReminder = (id: string, offsetMinutes: number): Reminder => ({
    id,
    taskId: 'task-1',
    title: 'Task reminder',
    timing: {
      type: 'relative_to_due_date',
      offsetMinutes,
    },
    deliveryMethod: 'both',
    enabled: true,
    delivered: false,
    createdAt: '2026-01-10T10:00:00Z',
  });

  // T084: Test calculateReminderTriggerTime with various offsets
  describe('offset calculations', () => {
    it('should calculate trigger time 15 minutes before due date', () => {
      const reminder = createReminder('reminder-1', -15);

      const triggerTime = calculateReminderTriggerTime(reminder, baseTask);

      expect(triggerTime).not.toBeNull();
      expect(triggerTime?.toISOString()).toBe('2026-01-15T13:45:00.000Z'); // 1:45pm UTC
    });

    it('should calculate trigger time 30 minutes before due date', () => {
      const reminder = createReminder('reminder-2', -30);

      const triggerTime = calculateReminderTriggerTime(reminder, baseTask);

      expect(triggerTime).not.toBeNull();
      expect(triggerTime?.toISOString()).toBe('2026-01-15T13:30:00.000Z'); // 1:30pm UTC
    });

    it('should calculate trigger time 1 hour before due date', () => {
      const reminder = createReminder('reminder-3', -60);

      const triggerTime = calculateReminderTriggerTime(reminder, baseTask);

      expect(triggerTime).not.toBeNull();
      expect(triggerTime?.toISOString()).toBe('2026-01-15T13:00:00.000Z'); // 1pm UTC
    });

    it('should calculate trigger time 1 day before due date', () => {
      const reminder = createReminder('reminder-4', -1440); // 24 hours = 1440 minutes

      const triggerTime = calculateReminderTriggerTime(reminder, baseTask);

      expect(triggerTime).not.toBeNull();
      expect(triggerTime?.toISOString()).toBe('2026-01-14T14:00:00.000Z'); // Previous day, 2pm UTC
    });

    it('should handle positive offsets (after due date)', () => {
      const reminder = createReminder('reminder-5', 30); // 30 minutes AFTER due date

      const triggerTime = calculateReminderTriggerTime(reminder, baseTask);

      expect(triggerTime).not.toBeNull();
      expect(triggerTime?.toISOString()).toBe('2026-01-15T14:30:00.000Z'); // 2:30pm UTC
    });
  });

  describe('edge cases', () => {
    it('should return null when task has no due date', () => {
      const taskWithoutDueDate: Task = {
        ...baseTask,
        dueDate: null,
      };

      const reminder = createReminder('reminder-6', -15);

      const triggerTime = calculateReminderTriggerTime(reminder, taskWithoutDueDate);

      expect(triggerTime).toBeNull();
    });

    it('should handle zero offset (exactly at due time)', () => {
      const reminder = createReminder('reminder-7', 0);

      const triggerTime = calculateReminderTriggerTime(reminder, baseTask);

      expect(triggerTime).not.toBeNull();
      expect(triggerTime?.toISOString()).toBe('2026-01-15T14:00:00.000Z'); // Exactly at due date
    });

    it('should handle large negative offsets (weeks before)', () => {
      const reminder = createReminder('reminder-8', -10080); // 1 week = 7 days = 10080 minutes

      const triggerTime = calculateReminderTriggerTime(reminder, baseTask);

      expect(triggerTime).not.toBeNull();
      expect(triggerTime?.toISOString()).toBe('2026-01-08T14:00:00.000Z'); // 7 days before
    });

    it('should handle invalid due date', () => {
      const taskWithInvalidDate: Task = {
        ...baseTask,
        dueDate: 'invalid-date',
      };

      const reminder = createReminder('reminder-9', -15);

      const triggerTime = calculateReminderTriggerTime(reminder, taskWithInvalidDate);

      expect(triggerTime).toBeNull();
    });
  });

  describe('timezone handling', () => {
    it('should work consistently across timezones', () => {
      // Due date specified in different timezone format - 9am EST = 2pm UTC
      const taskWithTimezone: Task = {
        ...baseTask,
        dueDate: '2026-01-15T14:00:00.000Z', // Already in UTC
      };

      const reminder = createReminder('reminder-10', -60);

      const triggerTime = calculateReminderTriggerTime(reminder, taskWithTimezone);

      expect(triggerTime).not.toBeNull();
      // Should still calculate 1 hour before in UTC
      expect(triggerTime?.toISOString()).toBe('2026-01-15T13:00:00.000Z');
    });
  });
});
