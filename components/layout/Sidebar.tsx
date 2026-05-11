'use client';
import { useSearchParams, useRouter } from 'next/navigation';
import { 
  Layout, ChartBar, Briefcase, User, Gear, SignOut, 
  SquaresFour, Users, IdentificationCard, ChatCircleText
} from '@phosphor-icons/react';
import { useAuthStore } from '@/lib/auth/store';
import { useMeProfile } from '@/lib/api/hooks';
import { useMemo } from 'react';
import api, { skipAuthRedirectConfig } from '@/lib/api/client';
import { API_ENDPOINTS } from '@/lib/api/endpoints';

const navItems = [
  { id: 'dashboard', label: 'Studio', icon: Layout, roles: ['creator', 'sme', 'agency', 'admin'] },
  { id: 'analytics', label: 'Metrics', icon: ChartBar, roles: ['creator', 'sme', 'agency', 'admin'] },
  { id: 'market', label: 'Find', icon: Briefcase, roles: ['sme', 'agency', 'admin'] },
  { id: 'profile', label: 'Profile', icon: User, roles: ['creator', 'sme', 'agency', 'admin'] },
  { id: 'settings', label: 'Settings', icon: Gear, roles: ['creator', 'sme', 'agency', 'admin'] },
  { id: 'chat', label: 'Chat', icon: ChatCircleText, roles: ['creator', 'sme', 'agency', 'admin'] },
];

export default function Sidebar() {
  const { logout, user } = useAuthStore();
  const { data } = useMeProfile();
  const searchParams = useSearchParams();
  const router = useRouter();
  const activeTab = searchParams.get('tab') || 'dashboard';

  const role = data?.profile?.role || user?.role || 'creator';
  const isAdmin = role === 'admin';

  const filteredNavItems = useMemo(() => {
    return navItems.map(item => {
      if (isAdmin) {
        if (item.id === 'dashboard') return { ...item, label: 'Manage', icon: Users };
        if (item.id === 'analytics') return { ...item, label: 'Audit', icon: IdentificationCard };
        if (item.id === 'market') return null; // Hide market for admins
      }
      return item;
    }).filter(Boolean);
  }, [isAdmin]);

  const setActiveTab = (tab: string) => {
    router.push(`/dashboard?tab=${tab}`, { scroll: false });
  };

  return (
    <aside className="w-20 hidden md:flex flex-col items-center py-10 border-r-2 border-black bg-white fixed h-full z-50">
      <div className="mb-14 cursor-pointer group" onClick={() => setActiveTab('dashboard')}>
         <SquaresFour size={32} weight="bold" className="text-black group-hover:rotate-90 transition-transform duration-500" />
      </div>
      
      <nav className="flex-1 flex flex-col items-center gap-6 overflow-y-auto w-full">
         {filteredNavItems.map(item => {
           if (!item) return null;
           const isAllowed = item.roles.includes(role);
           if (!isAllowed) return null;

           const Icon = item.icon;
           const isActive = activeTab === item.id;

           return (
             <button
               key={item.id}
               onClick={() => setActiveTab(item.id)}
               className={`p-3 transition-all relative group rounded-xl border-2 border-transparent ${isActive ? 'text-black' : 'text-zinc-300 hover:text-black hover:border-black/5'}`}
               title={item.label}
             >
               <Icon size={24} weight={isActive ? "fill" : "bold"} className="transition-transform group-hover:scale-110" />
             </button>
           );
         })}
      </nav>

      <button 
        onClick={async () => {
          try {
            await api.post(API_ENDPOINTS.auth.logout, undefined, skipAuthRedirectConfig);
          } catch {
            // continue local logout even if backend session is already invalid
          }
          logout();
          window.location.href = '/login';
        }} 
        className="mb-8 p-3 text-zinc-300 hover:text-red-500 transition-all active:scale-90 group relative"
        title="Logout"
      >
         <SignOut size={24} weight="bold" className="transition-transform group-hover:scale-110" />
      </button>
    </aside>
  );
}
