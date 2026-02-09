import { create } from 'zustand';

interface PendingCompletionsState {
  pendingTaskIds: Set<string>;
  showWarning: boolean;
  addPending: (taskId: string) => void;
  removePending: (taskId: string) => void;
  togglePending: (taskId: string) => void;
  isPending: (taskId: string) => boolean;
  hasPending: (taskId: string) => boolean;
  getPendingCount: () => number;
  getPendingIds: () => string[];
  clear: () => void;
  clearPending: () => void;
  hasTasksWithIncompleteSubtasks: () => boolean;
  getTasksWithIncompleteSubtasks: () => Array<{ id: string; incompleteSubtasksCount: number }>;
  setShowWarning: (show: boolean) => void;
}

export const usePendingCompletionsStore = create<PendingCompletionsState>((set, get) => ({
  pendingTaskIds: new Set<string>(),
  showWarning: false,

  addPending: (taskId) => set((state) => ({
    pendingTaskIds: new Set([...state.pendingTaskIds, taskId]),
  })),

  removePending: (taskId) => set((state) => {
    const newSet = new Set(state.pendingTaskIds);
    newSet.delete(taskId);
    return { pendingTaskIds: newSet };
  }),

  togglePending: (taskId) => {
    const state = get();
    if (state.pendingTaskIds.has(taskId)) {
      state.removePending(taskId);
    } else {
      state.addPending(taskId);
    }
  },

  isPending: (taskId) => get().pendingTaskIds.has(taskId),

  hasPending: (taskId) => get().pendingTaskIds.has(taskId),

  getPendingCount: () => get().pendingTaskIds.size,

  getPendingIds: () => Array.from(get().pendingTaskIds),

  clear: () => set({ pendingTaskIds: new Set() }),

  clearPending: () => set({ pendingTaskIds: new Set() }),

  hasTasksWithIncompleteSubtasks: () => {
    // Placeholder: This would need access to tasks data to check subtasks
    // For now, return false
    return false;
  },

  getTasksWithIncompleteSubtasks: () => {
    // Placeholder: This would need access to tasks/subtasks data
    // For now, return empty array
    return [];
  },

  setShowWarning: (show) => set({ showWarning: show }),
}));
