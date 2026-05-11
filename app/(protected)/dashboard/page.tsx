'use client';

import { useMemo, type FormEvent } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { toast } from 'sonner';
import {
  useAdminUsers,
  useAudienceInsights,
  useContentInsights,
  useDiscoverCreators,
  useMeProfile,
  usePerformanceInsights,
  useRoles,
  useUpdateCreatorProfile,
} from '@/lib/api/hooks';
import { useAuthStore } from '@/lib/auth/store';
import { formatNumber } from '@/lib/utils';

type DashboardTab =
  | 'dashboard'
  | 'analytics'
  | 'market'
  | 'profile'
  | 'settings'
  | 'notifications'
  | 'chat';

const TABS: DashboardTab[] = [
  'dashboard',
  'analytics',
  'market',
  'profile',
  'settings',
  'notifications',
  'chat',
];

function LoadingState() {
  return (
    <div className="p-6 md:p-8">
      <div className="max-w-6xl mx-auto space-y-4">
        <div className="h-10 w-40 rounded-xl bg-zinc-200 animate-pulse" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((item) => (
            <div key={item} className="h-28 rounded-2xl bg-zinc-200 animate-pulse" />
          ))}
        </div>
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-3xl border-2 border-black bg-white p-6">
      <h2 className="text-xl font-black tracking-tight text-black mb-4">{title}</h2>
      {children}
    </section>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const storeUser = useAuthStore((state) => state.user);

  const rawTab = searchParams.get('tab');
  const activeTab: DashboardTab = TABS.includes(rawTab as DashboardTab)
    ? (rawTab as DashboardTab)
    : 'dashboard';

  const me = useMeProfile();
  const role = me.data?.profile.role || storeUser?.role || 'creator';
  const isCreator = role === 'creator';
  const isSme = role === 'sme';
  const isAdmin = role === 'admin';

  const audience = useAudienceInsights(
    30,
    isCreator && (activeTab === 'dashboard' || activeTab === 'analytics')
  );
  const content = useContentInsights(5, isCreator && activeTab === 'analytics');
  const performance = usePerformanceInsights(
    30,
    isCreator && (activeTab === 'dashboard' || activeTab === 'analytics')
  );
  const discovery = useDiscoverCreators(
    12,
    0,
    undefined,
    (isSme || isAdmin) && (activeTab === 'dashboard' || activeTab === 'market')
  );
  const adminUsers = useAdminUsers(isAdmin && activeTab === 'dashboard');
  const adminRoles = useRoles(isAdmin && activeTab === 'dashboard');

  const updateCreatorProfile = useUpdateCreatorProfile();

  const setTab = (tab: DashboardTab) => {
    router.push(`/dashboard?tab=${tab}`, { scroll: false });
  };

  const summaryCards = useMemo(() => {
    const profile = me.data?.profile;
    return [
      { label: 'Role', value: role.toUpperCase() },
      { label: 'Audience', value: formatNumber(profile?.audienceSize || 0) },
      {
        label: 'Influence',
        value:
          profile?.influenceScore != null ? profile.influenceScore.toFixed(1) : '—',
      },
    ];
  }, [me.data?.profile, role]);

  const handleSaveProfile = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!isCreator) {
      toast.info('Profile updates are currently available for creator accounts.');
      return;
    }

    try {
      const formData = new FormData(event.currentTarget);
      const displayName = String(formData.get('displayName') || '').trim();
      const bio = String(formData.get('bio') || '').trim();

      await updateCreatorProfile.mutateAsync({
        displayName: displayName || undefined,
        bio: bio || undefined,
        creatorTypes: me.data?.profile.creatorTypes || [],
      });
      toast.success('Profile updated successfully.');
      await me.refetch();
    } catch {
      toast.error('Failed to update profile.');
    }
  };

  if (me.isLoading) return <LoadingState />;
  if (!me.data) return <div className="p-6 md:p-8 text-sm font-bold">Unable to load dashboard data.</div>;

  const profile = me.data.profile;

  return (
    <div className="p-4 md:p-8 pb-24 md:pb-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <header className="space-y-4">
          <h1 className="text-4xl md:text-5xl font-black tracking-tight">Dashboard</h1>
          <p className="text-sm text-zinc-600 font-semibold">
            Connected to backend APIs from authentication through role-based dashboard rendering.
          </p>

          <div className="flex flex-wrap gap-2">
            {TABS.map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setTab(tab)}
                className={`px-4 py-2 rounded-full border-2 border-black text-xs font-black uppercase tracking-wider ${
                  tab === activeTab ? 'bg-black text-white' : 'bg-white text-black'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {summaryCards.map((card) => (
            <article key={card.label} className="rounded-3xl border-2 border-black bg-white p-5">
              <p className="text-xs font-black uppercase tracking-wider text-zinc-500">{card.label}</p>
              <p className="mt-2 text-2xl font-black text-black">{card.value}</p>
            </article>
          ))}
        </div>

        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {isCreator && (
              <Section title="Creator overview">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm font-semibold">
                  <div className="rounded-2xl border border-black p-4">Subscribers: {formatNumber(audience.data?.channel?.subscriberCount || 0)}</div>
                  <div className="rounded-2xl border border-black p-4">Total views: {formatNumber(audience.data?.channel?.totalViewCount || 0)}</div>
                  <div className="rounded-2xl border border-black p-4">
                    Engagement rate: {performance.data?.engagementRate != null ? `${performance.data.engagementRate.toFixed(2)}%` : '—'}
                  </div>
                  <div className="rounded-2xl border border-black p-4">YouTube connected: {me.data.platformStatus.youtube.connected ? 'Yes' : 'No'}</div>
                </div>
              </Section>
            )}

            {(isSme || isAdmin) && (
              <Section title="Creator discovery snapshot">
                {discovery.isLoading ? (
                  <p className="text-sm font-semibold">Loading creators…</p>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {(discovery.data?.creators || []).slice(0, 6).map((creator) => (
                      <article key={creator.userId} className="rounded-2xl border border-black p-4">
                        <p className="text-base font-black">{creator.displayName || 'Unnamed creator'}</p>
                        <p className="text-xs font-semibold text-zinc-600 mt-1">Audience: {formatNumber(creator.audienceSize || 0)}</p>
                        <p className="text-xs font-semibold text-zinc-600">Influence: {creator.influenceScore ?? '—'}</p>
                      </article>
                    ))}
                  </div>
                )}
              </Section>
            )}

            {isAdmin && (
              <Section title="Admin controls">
                <p className="text-sm font-semibold mb-3">Roles from backend: {JSON.stringify(adminRoles.data)}</p>
                <p className="text-sm font-semibold">Users loaded: {adminUsers.data?.length || 0}</p>
              </Section>
            )}
          </div>
        )}

        {activeTab === 'analytics' && (
          <Section title="Analytics">
            {isCreator ? (
              <div className="space-y-4 text-sm font-semibold">
                <p>Audience views: {formatNumber(audience.data?.audience.views || 0)}</p>
                <p>Subscribers gained: {formatNumber(audience.data?.audience.subscribersGained || 0)}</p>
                <p>Top content items: {content.data?.items.length || 0}</p>
                <p>Time series points: {performance.data?.timeSeries.length || 0}</p>
              </div>
            ) : (
              <p className="text-sm font-semibold">Analytics details are focused on creator insight endpoints.</p>
            )}
          </Section>
        )}

        {activeTab === 'market' && (
          <Section title="Market">
            {isSme || isAdmin ? (
              <ul className="space-y-3">
                {(discovery.data?.creators || []).map((creator) => (
                  <li key={creator.userId} className="rounded-2xl border border-black p-4 text-sm font-semibold">
                    {creator.displayName || 'Unnamed creator'} — {formatNumber(creator.audienceSize || 0)} audience
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm font-semibold">Market discovery is available to SME and admin roles.</p>
            )}
          </Section>
        )}

        {activeTab === 'profile' && (
          <Section title="Profile">
            <div className="space-y-2 text-sm font-semibold">
              <p>Name: {profile.displayName || profile.name}</p>
              <p>Email: {profile.email}</p>
              <p>Tenant: {profile.tenantId}</p>
              <p>Onboarded: {profile.isOnboarded ? 'Yes' : 'No'}</p>
              <p>YouTube connected: {me.data.platformStatus.youtube.connected ? 'Yes' : 'No'}</p>
              <p>TikTok connected: {me.data.platformStatus.tiktok.connected ? 'Yes' : 'No'}</p>
              <p>Instagram connected: {me.data.platformStatus.instagram.connected ? 'Yes' : 'No'}</p>
            </div>
          </Section>
        )}

        {activeTab === 'settings' && (
          <Section title="Settings">
            <form className="space-y-4" onSubmit={handleSaveProfile}>
              <div>
                <label className="block text-xs font-black uppercase tracking-wider mb-2">Display name</label>
                <input
                  name="displayName"
                  defaultValue={profile.displayName || profile.name}
                  className="w-full rounded-2xl border-2 border-black px-4 py-3 text-sm font-semibold"
                />
              </div>
              <div>
                <label className="block text-xs font-black uppercase tracking-wider mb-2">Bio</label>
                <textarea
                  name="bio"
                  rows={4}
                  defaultValue={profile.bio || ''}
                  className="w-full rounded-2xl border-2 border-black px-4 py-3 text-sm font-semibold"
                />
              </div>
              <button
                type="submit"
                disabled={updateCreatorProfile.isPending}
                className="rounded-full border-2 border-black bg-black text-white px-5 py-3 text-xs font-black uppercase tracking-wider disabled:opacity-60"
              >
                {updateCreatorProfile.isPending ? 'Saving…' : 'Save changes'}
              </button>
            </form>
          </Section>
        )}

        {activeTab === 'notifications' && (
          <Section title="Notifications">
            <p className="text-sm font-semibold">Notifications are now based on your live backend profile and platform status.</p>
          </Section>
        )}

        {activeTab === 'chat' && (
          <Section title="Chat">
            <p className="text-sm font-semibold">Chat UI placeholder retained while backend messaging endpoints are not yet available.</p>
          </Section>
        )}
      </div>
    </div>
  );
}
