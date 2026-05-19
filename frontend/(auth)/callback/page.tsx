'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth/store';
import api from '@/lib/api/client';
import { getPostLoginRoute } from '@/lib/auth/routes';
import { toast } from 'sonner';
import { useQueryClient } from '@tanstack/react-query';

export default function Callback() {
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);
  const queryClient = useQueryClient();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Backend handles Google's redirect and sets httpOnly cookies, then redirects here.
        // First try to verify session; if verify succeeds but doesn't return full user, fetch /users/me.
        const verifyResp = await api.get('/auth/verify', { withCredentials: true }).catch(() => null);

        let user = null;

        if (verifyResp?.data) {
          if (verifyResp.data.user) {
            user = verifyResp.data.user;
          } else if (verifyResp.data.valid) {
            const meResp = await api.get('/users/me', { withCredentials: true });
            const d = meResp.data;
            user = {
              id: d.profile?.id,
              name: d.profile?.name,
              email: d.profile?.email,
              role: d.role,
              tenantId: d.profile?.tenantId,
            };
          }
        } else {
          const meResp = await api.get('/users/me', { withCredentials: true });
          const d = meResp.data;
          user = {
            id: d.profile?.id,
            name: d.profile?.name,
            email: d.profile?.email,
            role: d.role,
            tenantId: d.profile?.tenantId,
          };
        }

        if (user) {
          setAuth(user);
          router.replace(getPostLoginRoute(user.role));
          return;
        }

        await queryClient.invalidateQueries({ queryKey: ['users', 'me'] });
        toast.success('You are connected.');
        router.replace('/dashboard');
      } catch (err) {
        console.error('OAuth Callback Error:', err);
        await queryClient.invalidateQueries({ queryKey: ['users', 'me'] });
        toast.error('Failed to complete the connection.');
        router.push('/dashboard');
      }
    };
    handleCallback();
  }, [router, setAuth, queryClient]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="text-6xl mb-6 animal-float">🐨</div>
        <div className="text-3xl">Connecting your joy...</div>
      </div>
    </div>
  );
}
