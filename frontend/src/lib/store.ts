import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  display_name: string | null;
  avatar_url: string | null;
  role: string;
}

interface AppState {
  // Auth state
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isOnboardingComplete: boolean;
  
  // Actions
  setTokens: (access: string, refresh: string) => void;
  setUser: (user: User) => void;
  setOnboardingStatus: (status: boolean) => void;
  logout: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
      isOnboardingComplete: false,

      setTokens: (access, refresh) => set({ 
        accessToken: access, 
        refreshToken: refresh,
        isAuthenticated: true 
      }),
      
      setUser: (user) => set({ user }),
      
      setOnboardingStatus: (status) => set({ isOnboardingComplete: status }),

      logout: () => set({ 
        accessToken: null, 
        refreshToken: null, 
        user: null, 
        isAuthenticated: false,
        isOnboardingComplete: false
      }),
    }),
    {
      name: 'rewire-storage',
    }
  )
);
