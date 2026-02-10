import { useNotificationStore } from '@/lib/stores/notification.store';

export function useToast() {
  const { addNotification } = useNotificationStore();

  return {
    toast: (options: {
      title: string;
      message: string;
      type?: 'success' | 'error' | 'warning' | 'info';
      duration?: number;
    }) => {
      addNotification({
        type: options.type || 'info',
        title: options.title,
        message: options.message,
      });
    },
    success: (title: string, message: string) => {
      addNotification({ type: 'success', title, message });
    },
    error: (title: string, message: string) => {
      addNotification({ type: 'error', title, message });
    },
    warning: (title: string, message: string) => {
      addNotification({ type: 'warning', title, message });
    },
    info: (title: string, message: string) => {
      addNotification({ type: 'info', title, message });
    },
  };
}
