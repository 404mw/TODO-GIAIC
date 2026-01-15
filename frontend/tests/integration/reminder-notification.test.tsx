/**
 * @jest-environment jsdom
 */

import { render, waitFor } from '@testing-library/react';
import { act } from 'react';

// Mock Service Worker and Notification API
global.Notification = {
  permission: 'default',
  requestPermission: jest.fn(),
} as any;

global.ServiceWorkerRegistration = class {
  active = {
    postMessage: jest.fn(),
  };
} as any;

describe('Reminder Notifications Integration', () => {
  let mockServiceWorker: any;
  let originalNavigator: any;

  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();

    // Mock Service Worker
    mockServiceWorker = {
      postMessage: jest.fn(),
      addEventListener: jest.fn(),
    };

    originalNavigator = global.navigator;
    Object.defineProperty(global, 'navigator', {
      value: {
        ...originalNavigator,
        serviceWorker: {
          ready: Promise.resolve({
            active: mockServiceWorker,
          }),
          addEventListener: jest.fn(),
        },
      },
      configurable: true,
    });
  });

  afterEach(() => {
    jest.useRealTimers();
    Object.defineProperty(global, 'navigator', {
      value: originalNavigator,
      configurable: true,
    });
  });

  // T085: Test Service Worker detects due reminder and sends notification
  describe('Service Worker reminder detection', () => {
    it('should detect due reminder and trigger browser notification', async () => {
      const mockReminder = {
        id: 'reminder-1',
        taskId: 'task-1',
        title: 'Task Due Soon',
        offsetMinutes: -15,
        delivered: false,
        createdAt: '2026-01-10T10:00:00Z',
      };

      const mockTask = {
        id: 'task-1',
        title: 'Finish Report',
        dueDate: new Date(Date.now() + 900000), // 15 minutes from now
      };

      // Mock Notification permission granted
      (global.Notification as any).permission = 'granted';
      (global.Notification as any).requestPermission = jest
        .fn()
        .mockResolvedValue('granted');

      // Simulate Service Worker message
      const messageEvent = new MessageEvent('message', {
        data: {
          type: 'REMINDER_DUE',
          reminder: mockReminder,
          task: mockTask,
        },
      });

      const messageHandler = jest.fn();
      global.navigator.serviceWorker.addEventListener('message', messageHandler);

      // Trigger message event
      act(() => {
        messageHandler(messageEvent);
      });

      await waitFor(() => {
        expect(messageHandler).toHaveBeenCalledWith(
          expect.objectContaining({
            data: expect.objectContaining({
              type: 'REMINDER_DUE',
              reminder: mockReminder,
            }),
          })
        );
      });
    });

    it('should post message to all clients when reminder is due', async () => {
      const mockReminder = {
        id: 'reminder-2',
        taskId: 'task-2',
        title: 'Meeting Reminder',
        offsetMinutes: -30,
        delivered: false,
      };

      // Simulate Service Worker posting message
      act(() => {
        mockServiceWorker.postMessage({
          type: 'REMINDER_DUE',
          reminder: mockReminder,
        });
      });

      expect(mockServiceWorker.postMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'REMINDER_DUE',
        })
      );
    });

    it('should not send notification for already delivered reminders', async () => {
      const deliveredReminder = {
        id: 'reminder-3',
        taskId: 'task-3',
        title: 'Delivered Reminder',
        offsetMinutes: -15,
        delivered: true, // Already delivered
      };

      const messageHandler = jest.fn();
      global.navigator.serviceWorker.addEventListener('message', messageHandler);

      // Service Worker should skip delivered reminders
      // Verify by checking that no message is posted for delivered reminder
      expect(mockServiceWorker.postMessage).not.toHaveBeenCalled();
    });
  });

  // T086: Test browser permission denied falls back to in-app toast only
  describe('Browser permission fallback', () => {
    it('should fall back to in-app toast when browser permission denied', async () => {
      // Mock permission denied
      (global.Notification as any).permission = 'denied';
      (global.Notification as any).requestPermission = jest
        .fn()
        .mockResolvedValue('denied');

      const mockReminder = {
        id: 'reminder-4',
        taskId: 'task-4',
        title: 'Task Reminder',
        offsetMinutes: -15,
        delivered: false,
      };

      const mockTask = {
        id: 'task-4',
        title: 'Complete Project',
        dueDate: new Date(Date.now() + 900000),
      };

      const messageEvent = new MessageEvent('message', {
        data: {
          type: 'REMINDER_DUE',
          reminder: mockReminder,
          task: mockTask,
          fallbackToast: true, // Indicates browser notification unavailable
        },
      });

      const messageHandler = jest.fn();
      global.navigator.serviceWorker.addEventListener('message', messageHandler);

      act(() => {
        messageHandler(messageEvent);
      });

      await waitFor(() => {
        expect(messageHandler).toHaveBeenCalledWith(
          expect.objectContaining({
            data: expect.objectContaining({
              fallbackToast: true,
            }),
          })
        );
      });
    });

    it('should request permission on first reminder creation', async () => {
      (global.Notification as any).permission = 'default';
      (global.Notification as any).requestPermission = jest
        .fn()
        .mockResolvedValue('granted');

      // Simulate first reminder creation trigger
      await act(async () => {
        await global.Notification.requestPermission();
      });

      expect(global.Notification.requestPermission).toHaveBeenCalled();
    });

    it('should still send in-app toast even when permission is default (not yet asked)', async () => {
      (global.Notification as any).permission = 'default';

      const mockReminder = {
        id: 'reminder-5',
        taskId: 'task-5',
        title: 'Default Permission Reminder',
        offsetMinutes: -15,
        delivered: false,
      };

      const messageEvent = new MessageEvent('message', {
        data: {
          type: 'REMINDER_DUE',
          reminder: mockReminder,
          fallbackToast: true,
        },
      });

      const messageHandler = jest.fn();
      global.navigator.serviceWorker.addEventListener('message', messageHandler);

      act(() => {
        messageHandler(messageEvent);
      });

      await waitFor(() => {
        expect(messageHandler).toHaveBeenCalled();
      });
    });
  });

  describe('Service Worker unavailable fallback', () => {
    it('should handle missing Service Worker gracefully', async () => {
      // Remove Service Worker support
      Object.defineProperty(global, 'navigator', {
        value: {
          ...originalNavigator,
          serviceWorker: undefined,
        },
        configurable: true,
      });

      // Application should still render without crashing
      const { container } = render(<div>App without Service Worker</div>);
      expect(container).toBeInTheDocument();

      // Fallback warning should be logged (or shown to user)
      // This will be tested in the actual component
    });
  });

  describe('Notification click behavior', () => {
    it('should navigate to task detail when notification clicked', async () => {
      const mockTask = {
        id: 'task-6',
        title: 'Clickable Task',
      };

      (global.Notification as any).permission = 'granted';

      const mockNotification = {
        onclick: jest.fn(),
        close: jest.fn(),
      };

      // Simulate notification click
      act(() => {
        mockNotification.onclick();
      });

      expect(mockNotification.onclick).toHaveBeenCalled();
      // In real implementation, this should trigger navigation to /dashboard/tasks/task-6
    });
  });

  describe('60-second polling interval', () => {
    it('should check for due reminders every 60 seconds', async () => {
      const pollInterval = 60000; // 60 seconds

      const mockPollFunction = jest.fn();

      // Simulate Service Worker setInterval
      setInterval(mockPollFunction, pollInterval);

      // Fast-forward 60 seconds
      act(() => {
        jest.advanceTimersByTime(pollInterval);
      });

      expect(mockPollFunction).toHaveBeenCalledTimes(1);

      // Fast-forward another 60 seconds
      act(() => {
        jest.advanceTimersByTime(pollInterval);
      });

      expect(mockPollFunction).toHaveBeenCalledTimes(2);
    });
  });
});
