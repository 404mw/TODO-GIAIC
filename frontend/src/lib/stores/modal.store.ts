import { create } from 'zustand';

type ModalName = 'createTask' | 'editTask' | 'deleteTask' | 'settings' | 'upgrade' | null;

interface ModalState {
  activeModal: ModalName;
  modalData: unknown;
  openModal: (name: ModalName, data?: unknown) => void;
  closeModal: () => void;
}

export const useModalStore = create<ModalState>((set) => ({
  activeModal: null,
  modalData: null,
  openModal: (name, data) => set({ activeModal: name, modalData: data }),
  closeModal: () => set({ activeModal: null, modalData: null }),
}));
