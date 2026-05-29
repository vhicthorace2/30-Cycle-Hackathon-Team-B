'use client';

import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { ArrowRight, CheckCircle, YoutubeLogo } from '@phosphor-icons/react';
import { toast } from 'sonner';
import { useMeProfile, usePrepareYoutubeOauth, useUpdateCreatorProfile } from '@/lib/api/hooks';
import { useAuthStore } from '@/lib/auth/store';

const creatorTypeOptions = ['gaming', 'lifestyle', 'education', 'tech', 'beauty', 'fitness'];

export default function OnboardingPage() {
  const router = useRouter();
  const { user, setAuth } = useAuthStore();
  const { data: profile, isLoading, isError } = useMeProfile();
  const onboardMutation = useUpdateCreatorProfile();
  const [displayName, setDisplayName] = useState('');
  const [bio, setBio] = useState('');
  const [industry, setIndustry] = useState('');
  const [creatorTypes, setCreatorTypes] = useState<string[]>(['lifestyle']);
  const [connectYoutube, setConnectYoutube] = useState(false);
  const { data: youtubeOauth, isFetching: loadingYoutubeOauth } = usePrepareYoutubeOauth(connectYoutube);

  const role = profile?.role || user?.role || 'creator';
  const isCreator = role === 'creator';
  const firstName = (profile?.profile?.name || user?.name || 'there').split(' ')[0];

  useEffect(() => {
    if (profile?.profile && !user) {
      setAuth({
        id: profile.profile.id,
        name: profile.profile.name,
        email: profile.profile.email,
        role: profile.role as any,
        tenantId: profile.profile.tenantId,
      });
    }
  }, [profile, setAuth, user]);

  useEffect(() => {
    if (isError && !user) {
      router.replace('/signup');
    }
  }, [isError, router, user]);

  useEffect(() => {
    if (profile?.profile) {
      setDisplayName(profile.profile.displayName || profile.profile.name || '');
      setBio(profile.profile.bio || '');
      setIndustry(profile.profile.creatorTypes?.[0] || '');
      if (profile.profile.creatorTypes?.length) setCreatorTypes(profile.profile.creatorTypes);
    }
  }, [profile]);

  useEffect(() => {
    if (youtubeOauth?.authorizationUrl && connectYoutube) {
      window.location.href = youtubeOauth.authorizationUrl;
    }
  }, [youtubeOauth, connectYoutube]);

  const selectedTypes = useMemo(
    () => (isCreator ? creatorTypes : [industry.trim().toLowerCase() || 'business']),
    [creatorTypes, industry, isCreator],
  );

  const toggleCreatorType = (type: string) => {
    setCreatorTypes((current) =>
      current.includes(type)
        ? current.filter((item) => item !== type)
        : [...current, type],
    );
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!displayName.trim()) {
      toast.error('Display name is required.');
      return;
    }

    if (isCreator && selectedTypes.length === 0) {
      toast.error('Choose at least one creator type.');
      return;
    }

    try {
      await onboardMutation.mutateAsync({
        displayName: displayName.trim(),
        bio: bio.trim() || undefined,
        industry: industry.trim() || undefined,
        creatorTypes: selectedTypes,
      });
      toast.success('Onboarding complete.');
      router.replace('/dashboard');
    } catch (error: any) {
      const message = error?.response?.data?.message || 'Unable to complete onboarding.';
      toast.error(Array.isArray(message) ? message.join(', ') : message);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F8F9FF] flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-[#006D32]/20 border-t-[#006D32] rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8F9FF] flex flex-col">
      <header className="fixed top-0 left-0 right-0 z-50 h-20 backdrop-blur-md bg-[#F8F9FF]/80 border-b border-[#0B1C30]/10">
        <div className="max-w-[1280px] mx-auto px-6 lg:px-[116px] h-full flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div className="w-9 h-9 rounded-full bg-[#6B61F0] text-white flex items-center justify-center font-black">O</div>
            <span className="text-xl font-black text-[#0B1C30]" style={{ fontFamily: "'Space Grotesk'" }}>Omniview</span>
          </Link>
          <div className="hidden sm:flex items-center gap-2 text-sm font-bold text-[#006D32]">
            <CheckCircle size={18} weight="fill" />
            Account created
          </div>
        </div>
      </header>

      <main className="flex-1 pt-28 pb-12 px-4 sm:px-8">
        <div className="max-w-6xl mx-auto grid lg:grid-cols-[1.05fr_0.95fr] gap-10 items-center">
          <motion.section
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45 }}
            className="space-y-8"
          >
            <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-[#64FF92] rounded-full text-sm font-bold tracking-widest text-[#00210B]">
              ONBOARDING
            </div>
            <div>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-[1.08] text-[#0B1C30]" style={{ fontFamily: "'Space Grotesk'" }}>
                Set up your workspace, {firstName}.
              </h1>
              <p className="text-lg text-[#374151] max-w-xl leading-relaxed mt-5">
                Add the profile details used by the dashboard, discovery, and creator scoring endpoints.
              </p>
            </div>
            <div className="relative w-full max-w-[480px] aspect-[4/3] hidden lg:block">
              <Image
                src="/undraw_online-community_3o0l.svg"
                alt="Onboarding illustration"
                fill
                className="object-contain drop-shadow-2xl"
                priority
              />
            </div>
          </motion.section>

          <motion.form
            onSubmit={handleSubmit}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.08 }}
            className="bg-white rounded-3xl border border-[#E5E7EB] shadow-sm p-5 sm:p-8 space-y-6"
          >
            <div>
              <h2 className="text-2xl font-black text-[#0B1C30]" style={{ fontFamily: "'Space Grotesk'" }}>
                Profile basics
              </h2>
              
            </div>

            <div className="space-y-4">
              <label className="block">
                <span className="block text-sm font-bold text-[#0B1C30] mb-2">Display name</span>
                <input
                  value={displayName}
                  onChange={(event) => setDisplayName(event.target.value)}
                  placeholder={isCreator ? 'Creator Studio' : 'Acme Foods'}
                  className="w-full px-4 py-3 rounded-xl border border-[#E5E7EB] bg-[#F8F9FF] text-sm font-medium focus:outline-none focus:border-[#006D32] focus:ring-2 focus:ring-[#006D32]/20"
                />
              </label>

              <label className="block">
                <span className="block text-sm font-bold text-[#0B1C30] mb-2">{isCreator ? 'Creator niche' : 'Business industry'}</span>
                <input
                  value={industry}
                  onChange={(event) => setIndustry(event.target.value)}
                  placeholder={isCreator ? 'Education, gaming, tech...' : 'Retail, food, fintech...'}
                  className="w-full px-4 py-3 rounded-xl border border-[#E5E7EB] bg-[#F8F9FF] text-sm font-medium focus:outline-none focus:border-[#006D32] focus:ring-2 focus:ring-[#006D32]/20"
                />
              </label>

              <label className="block">
                <span className="block text-sm font-bold text-[#0B1C30] mb-2">Short bio</span>
                <textarea
                  value={bio}
                  onChange={(event) => setBio(event.target.value)}
                  rows={4}
                  placeholder={isCreator ? 'Tell brands what you create.' : 'Tell creators what your business is building.'}
                  className="w-full px-4 py-3 rounded-xl border border-[#E5E7EB] bg-[#F8F9FF] text-sm font-medium focus:outline-none focus:border-[#006D32] focus:ring-2 focus:ring-[#006D32]/20 resize-none"
                />
              </label>
            </div>

            {isCreator && (
              <div>
                <p className="text-sm font-bold text-[#0B1C30] mb-3">Creator types</p>
                <div className="flex flex-wrap gap-2">
                  {creatorTypeOptions.map((type) => {
                    const selected = creatorTypes.includes(type);
                    return (
                      <button
                        key={type}
                        type="button"
                        onClick={() => toggleCreatorType(type)}
                        className={`px-3 py-2 rounded-full text-xs font-bold capitalize transition ${
                          selected
                            ? 'bg-[#006D32] text-white'
                            : 'bg-[#EFF4FF] text-[#0B1C30] hover:bg-[#D3E4FE]'
                        }`}
                      >
                        {type}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {isCreator && !profile?.platformStatus?.youtube?.connected && (
              <button
                type="button"
                onClick={() => setConnectYoutube(true)}
                disabled={loadingYoutubeOauth}
                className="w-full flex items-center justify-center gap-2 rounded-xl border border-[#E5E7EB] bg-[#FFF7F7] px-4 py-3 text-sm font-bold text-[#0B1C30] transition hover:border-red-200 disabled:opacity-60"
              >
                <YoutubeLogo size={20} weight="fill" className="text-red-600" />
                {loadingYoutubeOauth ? 'Preparing YouTube...' : 'Connect YouTube now'}
              </button>
            )}

            <button
              type="submit"
              disabled={onboardMutation.isPending}
              className="w-full flex items-center justify-center gap-3 px-5 py-4 rounded-2xl bg-[#006D32] hover:bg-[#005227] text-white font-bold shadow-lg shadow-[#006D32]/20 transition disabled:opacity-60"
            >
              {onboardMutation.isPending ? 'Saving profile...' : 'Finish setup'}
              <ArrowRight size={20} weight="bold" />
            </button>
          </motion.form>
        </div>
      </main>
    </div>
  );
}
