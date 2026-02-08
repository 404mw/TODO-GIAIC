/**
 * @jest-environment jsdom
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ReminderForm } from '@/components/reminders/ReminderForm';
import type { Task } from '@/lib/schemas/task.schema';

// Mock DOM methods for Radix UI compatibility with JSDOM
beforeAll(() => {
  HTMLElement.prototype.hasPointerCapture = jest.fn();
  HTMLElement.prototype.setPointerCapture = jest.fn();
  HTMLElement.prototype.releasePointerCapture = jest.fn();

  // Mock scrollIntoView
  Element.prototype.scrollIntoView = jest.fn();

  // Mock getComputedStyle
  window.getComputedStyle = jest.fn().mockImplementation(() => ({
    getPropertyValue: jest.fn(),
  }));
});

describe('ReminderForm', () => {
  const mockTaskWithDueDate: Task = {
    id: 'task-1',
    title: 'Test Task',
    description: '',
    priority: 'medium',
    estimatedDuration: null,
    focusTimeSeconds: 0,
    completed: false,
    completedAt: null,
    completedBy: null,
    hidden: false,
    archived: false,
    templateId: null,
    subtaskCount: 0,
    subtaskCompletedCount: 0,
    version: 1,
    dueDate: '2026-01-15T10:00:00Z',
    createdAt: '2026-01-10T10:00:00Z',
    updatedAt: '2026-01-10T10:00:00Z',
  };

  const mockTaskWithoutDueDate: Task = {
    ...mockTaskWithDueDate,
    dueDate: null,
  };

  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  // T083: Test ReminderForm validates task has due date required
  describe('due date validation', () => {
    it('should render form when task has due date', () => {
      render(<ReminderForm task={mockTaskWithDueDate} onSubmit={mockOnSubmit} />);

      expect(screen.getByLabelText(/reminder time/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /add reminder/i })).toBeInTheDocument();
    });

    it('should show error message when task has no due date', () => {
      render(<ReminderForm task={mockTaskWithoutDueDate} onSubmit={mockOnSubmit} />);

      expect(screen.getByText(/task must have a due date/i)).toBeInTheDocument();
      expect(screen.queryByLabelText(/reminder time/i)).not.toBeInTheDocument();
    });

    it('should disable form submission when task has no due date', () => {
      render(<ReminderForm task={mockTaskWithoutDueDate} onSubmit={mockOnSubmit} />);

      const submitButton = screen.queryByRole('button', { name: /add reminder/i });
      expect(submitButton).not.toBeInTheDocument();
    });
  });

  describe('offset minute selector', () => {
    it('should render preset timing options', async () => {
      const user = userEvent.setup();
      render(<ReminderForm task={mockTaskWithDueDate} onSubmit={mockOnSubmit} />);

      // Open the Radix Select dropdown
      const trigger = screen.getByRole('combobox', { name: /reminder time/i });
      await user.click(trigger);

      // Wait for options to appear and verify they exist
      await waitFor(() => {
        expect(screen.getByRole('option', { name: /15 minutes before/i })).toBeInTheDocument();
        expect(screen.getByRole('option', { name: /30 minutes before/i })).toBeInTheDocument();
        expect(screen.getByRole('option', { name: /1 hour before/i })).toBeInTheDocument();
        expect(screen.getByRole('option', { name: /1 day before/i })).toBeInTheDocument();
      });
    });

    it('should submit reminder with correct offset', async () => {
      const user = userEvent.setup();
      render(<ReminderForm task={mockTaskWithDueDate} onSubmit={mockOnSubmit} />);

      // Open the Radix Select dropdown
      const trigger = screen.getByRole('combobox', { name: /reminder time/i });
      await user.click(trigger);

      // Select "30 minutes before" option
      await waitFor(() => {
        expect(screen.getByRole('option', { name: /30 minutes before/i })).toBeInTheDocument();
      });
      const option = screen.getByRole('option', { name: /30 minutes before/i });
      await user.click(option);

      const submitButton = screen.getByRole('button', { name: /add reminder/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            taskId: 'task-1',
            title: 'Reminder for: Test Task',
            timing: expect.objectContaining({
              type: 'relative_to_due_date',
              offsetMinutes: 30,
            }),
            deliveryMethod: 'both',
            enabled: true,
          })
        );
      });
    });
  });

  describe('form validation', () => {
    it('should submit with default offset when no selection made', async () => {
      const user = userEvent.setup();
      render(<ReminderForm task={mockTaskWithDueDate} onSubmit={mockOnSubmit} />);

      // Submit without changing the default selection (15 minutes)
      const submitButton = screen.getByRole('button', { name: /add reminder/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            taskId: 'task-1',
            title: 'Reminder for: Test Task',
            timing: expect.objectContaining({
              type: 'relative_to_due_date',
              offsetMinutes: 15,
            }),
            deliveryMethod: 'both',
            enabled: true,
          })
        );
      });
    });
  });
});
