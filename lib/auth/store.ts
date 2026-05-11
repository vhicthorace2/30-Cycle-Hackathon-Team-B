import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { clearAuthCookies, setAuthCookies } from './cookies';

export type Role = 'admin' | 'user' | 'sme' | 'creator';

export interface User {
  id: string;
  name: string;
  email: string;
  role: Role;
  tenantId: string;
}

export interface Tenant {
  id: string;
  name: string;
}

type AuthUserInput = Omit<User, 'id' | 'tenantId'> & {
  id: string | number;
  tenantId: string | number;
};

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  currentTenant: Tenant | null;
  isAuthenticated: boolean;
  _hasHydrated: boolean;
  setHasHydrated: (val: boolean) => void;
  setAuth: (user: AuthUserInput, token: string, refreshToken: string) => void;
  updateToken: (token: string, refreshToken?: string) => void;
  switchTenant: (tenant: Tenant) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      currentTenant: null,
      isAuthenticated: false,
      _hasHydrated: false,
      setHasHydrated: (val) => set({ _hasHydrated: val }),
      setAuth: (user, token, refreshToken) => {
        const normalizedUser: User = {
          ...user,
          id: String(user.id),
          tenantId: String(user.tenantId),
        };

        if (token && refreshToken) {
          setAuthCookies(token, refreshToken);
        }
        set({
          user: normalizedUser,
          accessToken: token,
          refreshToken,
          isAuthenticated: true,
          currentTenant: { id: normalizedUser.tenantId, name: 'Personal' },
        });
      },
      updateToken: (token, refreshToken) => set((state) => ({ accessToken: token, refreshToken: refreshToken || state.refreshToken })),
      switchTenant: (tenant) => set({ currentTenant: tenant }),
      logout: () => {
        clearAuthCookies();
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false, currentTenant: null });
      },
    }),
    {
      name: 'auth-storage',
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
      },
    }
  )
);
