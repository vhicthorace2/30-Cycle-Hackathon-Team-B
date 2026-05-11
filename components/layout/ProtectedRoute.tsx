'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth/store';
import api, { skipAuthRedirectConfig } from '@/lib/api/client';
import { API_ENDPOINTS } from '@/lib/api/endpoints';

type VerifyResponse = {
  valid: boolean;
  userId: string | number;
  email: string;
  tenantId?: string | number;
  role?: 'admin' | 'user' | 'sme' | 'creator';
};

type MeProfileResponse = {
  profile: {
    id: string | number;
    name: string;
    email: string;
    tenantId: string | number;
    role: 'admin' | 'user' | 'sme' | 'creator';
  };
};

export default function ProtectedRoute({ children }: { 
  children: React.ReactNode; 
}) {
  const { isAuthenticated, _hasHydrated } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!_hasHydrated) return;
    if (isAuthenticated) return;
    const checkSession = async () => {
      try {
        const verify = await api.get<VerifyResponse>(API_ENDPOINTS.auth.verify, skipAuthRedirectConfig);
        if (!verify.data.valid) {
          router.replace('/login');
          return;
        }

        const profile = await api.get<MeProfileResponse>(API_ENDPOINTS.users.me, skipAuthRedirectConfig);
        const user = profile.data.profile;
        useAuthStore.getState().setAuth(
          {
            id: user.id,
            name: user.name,
            email: user.email,
            role: user.role,
            tenantId: user.tenantId,
          },
          useAuthStore.getState().accessToken || '',
          useAuthStore.getState().refreshToken || ''
        );
      } catch {
        router.replace('/login');
      }
    };

    checkSession();
  }, [_hasHydrated, isAuthenticated, router]);

  // Show loading while Zustand rehydrates from localStorage
  if (!_hasHydrated) return (
    <div className="min-h-screen bg-[#F8FAFC] flex">
      {/* Skeleton Sidebar */}
      <div className="w-20 hidden md:flex flex-col items-center py-10 border-r border-zinc-100 bg-white h-full fixed">
         <div className="w-10 h-10 bg-zinc-100 rounded-xl mb-12 animate-pulse" />
         <div className="space-y-6 flex-1">
            {[1,2,3,4].map(i => <div key={i} className="w-10 h-10 bg-zinc-50 rounded-xl animate-pulse" />)}
         </div>
      </div>
      {/* Main Content Skeleton */}
      <div className="flex-1 md:ml-20 flex flex-col">
         <div className="h-20 bg-white border-b border-zinc-100 px-10 flex items-center justify-between animate-pulse">
            <div className="w-64 h-10 bg-zinc-50 rounded-2xl" />
            <div className="w-32 h-10 bg-zinc-50 rounded-full" />
         </div>
         <div className="p-10 space-y-10">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
               {[1,2,3,4].map(i => <div key={i} className="h-44 bg-zinc-100 rounded-[2rem] animate-pulse" />)}
            </div>
            <div className="h-[400px] bg-zinc-100 rounded-[2.5rem] animate-pulse" />
         </div>
      </div>
    </div>
  );

  if (!isAuthenticated) return null;

  return <>{children}</>;
}
