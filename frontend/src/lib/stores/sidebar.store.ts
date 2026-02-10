import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SidebarState {
  isCollapsed: boolean;
  isOpen: boolean;
  isMobile: boolean;
  toggle: () => void;
  setCollapsed: (collapsed: boolean) => void;
  setMobile: (mobile: boolean) => void;
  close: () => void;
}

// Check if we're on mobile (< 1024px) on initial load
const isMobile = typeof window !== 'undefined' && window.innerWidth < 1024;

export const useSidebarStore = create<SidebarState>()(
  persist(
    (set, get) => ({
      // Start collapsed on mobile, use persisted state on desktop
      isCollapsed: isMobile,
      isMobile: isMobile,
      get isOpen() {
        // On mobile, always start closed unless explicitly toggled
        const state = get();
        return !state.isCollapsed;
      },
      toggle: () => set((state) => ({ isCollapsed: !state.isCollapsed })),
      setCollapsed: (collapsed) => set({ isCollapsed: collapsed }),
      setMobile: (mobile) => {
        // When switching to mobile, auto-close sidebar
        if (mobile) {
          set({ isMobile: mobile, isCollapsed: true });
        } else {
          set({ isMobile: mobile });
        }
      },
      close: () => set({ isCollapsed: true }),
    }),
    {
      name: 'sidebar-storage',
      // Only persist desktop preference, not mobile state
      partialize: (state) => ({ isCollapsed: state.isMobile ? true : state.isCollapsed }),
    }
  )
);
