import { create } from 'zustand';
import type { Task } from '@/lib/schemas/task.schema';

interface NewTaskModalState {
  isOpen: boolean;
  mode: 'create' | 'edit';
  editTask?: Task;
  open: () => void;
  openEdit: (task: Task) => void;
  close: () => void;
}

export const useNewTaskModalStore = create<NewTaskModalState>((set) => ({
  isOpen: false,
  mode: 'create',
  editTask: undefined,
  open: () => set({ isOpen: true, mode: 'create', editTask: undefined }),
  openEdit: (task) => set({ isOpen: true, mode: 'edit', editTask: task }),
  close: () => set({ isOpen: false, editTask: undefined }),
}));
