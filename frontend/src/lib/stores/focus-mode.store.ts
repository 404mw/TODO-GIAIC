import { create } from 'zustand';

interface FocusModeState {
  isActive: boolean;
  currentTaskId: string | null;
  startTime: Date | null;
  activate: (taskId: string) => void;
  deactivate: () => void;
}

export const useFocusModeStore = create<FocusModeState>((set) => ({
  isActive: false,
  currentTaskId: null,
  startTime: null,
  activate: (taskId) => set({
    isActive: true,
    currentTaskId: taskId,
    startTime: new Date(),
  }),
  deactivate: () => set({
    isActive: false,
    currentTaskId: null,
    startTime: null,
  }),
}));
