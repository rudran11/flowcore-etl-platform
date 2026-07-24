import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  avatar?: string;
}

interface Workspace {
  id: string;
  name: string;
  description?: string;
  organization_id: string;
}

interface AuthState {
  accessToken: string | null;
  user: User | null;
  activeWorkspaceId: string | null;
  workspaces: Workspace[];
  
  setToken: (token: string) => void;
  setUser: (user: User) => void;
  setWorkspaces: (workspaces: Workspace[]) => void;
  setActiveWorkspace: (id: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      user: null,
      activeWorkspaceId: null,
      workspaces: [],
      
      setToken: (token) => set({ accessToken: token }),
      setUser: (user) => set({ user }),
      setWorkspaces: (workspaces) => {
        set((state) => ({
          workspaces,
          activeWorkspaceId: state.activeWorkspaceId && workspaces.find(w => w.id === state.activeWorkspaceId)
            ? state.activeWorkspaceId 
            : (workspaces[0]?.id || null)
        }));
      },
      setActiveWorkspace: (id) => set({ activeWorkspaceId: id }),
      logout: () => set({ accessToken: null, user: null, activeWorkspaceId: null, workspaces: [] }),
    }),
    {
      name: 'flowcore-auth-storage',
      // We don't want to persist the access token in localStorage for high security,
      // but for SPA refresh we might need to (or rely on silent refresh using the HttpOnly cookie).
      // Given the requirement "Access Token -> Zustand (memory only)", we must omit accessToken from persistence.
      partialize: (state) => ({ activeWorkspaceId: state.activeWorkspaceId }),
    }
  )
);
