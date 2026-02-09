import { create } from 'zustand';

interface PendingCompletionsState {
  pendingTaskIds: Set<string>;
  addPending: (taskId: string) => void;
  removePending: (taskId: string) => void;
  isPending: (taskId: string) => boolean;
  clear: () => void;
}

export const usePendingCompletionsStore = create<PendingCompletionsState>((set, get) => ({
  pendingTaskIds: new Set<string>(),

  addPending: (taskId) => set((state) => ({
    pendingTaskIds: new Set([...state.pendingTaskIds, taskId]),
  })),

  removePending: (taskId) => set((state) => {
    const newSet = new Set(state.pendingTaskIds);
    newSet.delete(taskId);
    return { pendingTaskIds: newSet };
  }),

  isPending: (taskId) => get().pendingTaskIds.has(taskId),

  clear: () => set({ pendingTaskIds: new Set() }),
}));
