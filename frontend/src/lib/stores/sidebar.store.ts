import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SidebarState {
  isCollapsed: boolean;
  isOpen: boolean;
  toggle: () => void;
  setCollapsed: (collapsed: boolean) => void;
}

// Check if we're on mobile (< 1024px) on initial load
const isMobile = typeof window !== 'undefined' && window.innerWidth < 1024;

export const useSidebarStore = create<SidebarState>()(
  persist(
    (set, get) => ({
      // Start collapsed on mobile, expanded on desktop (unless user has a saved preference)
      isCollapsed: isMobile,
      get isOpen() {
        return !get().isCollapsed;
      },
      toggle: () => set((state) => ({ isCollapsed: !state.isCollapsed })),
      setCollapsed: (collapsed) => set({ isCollapsed: collapsed }),
    }),
    { name: 'sidebar-storage' }
  )
);
