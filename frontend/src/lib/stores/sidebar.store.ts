import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SidebarState {
  isCollapsed: boolean;
  isMobile: boolean;
  isOpen: boolean;
  toggle: () => void;
  setCollapsed: (collapsed: boolean) => void;
  setMobile: (mobile: boolean) => void;
  close: () => void;
}

// Check if we're on mobile (< 1024px) on initial load
const isMobile = typeof window !== 'undefined' && window.innerWidth < 1024;

export const useSidebarStore = create<SidebarState>()(
  persist(
    (set) => ({
      // Start collapsed on mobile, use persisted state on desktop
      isCollapsed: isMobile,
      isMobile: isMobile,
      isOpen: !isMobile, // Computed from isCollapsed
      toggle: () => set((state) => ({
        isCollapsed: !state.isCollapsed,
        isOpen: !state.isOpen,
      })),
      setCollapsed: (collapsed) => set({
        isCollapsed: collapsed,
        isOpen: !collapsed,
      }),
      setMobile: (mobile) => {
        // When switching to mobile, auto-close sidebar
        if (mobile) {
          set({ isMobile: mobile, isCollapsed: true, isOpen: false });
        } else {
          set((state) => ({ isMobile: mobile, isOpen: !state.isCollapsed }));
        }
      },
      close: () => set({ isCollapsed: true, isOpen: false }),
    }),
    {
      name: 'sidebar-storage',
      // Only persist isCollapsed, always recompute isMobile and isOpen on load
      partialize: (state) => ({ isCollapsed: state.isCollapsed }),
    }
  )
);
