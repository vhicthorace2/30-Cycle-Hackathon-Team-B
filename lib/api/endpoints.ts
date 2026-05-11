export const API_ENDPOINTS = {
  auth: {
    signup: '/auth/signup',
    login: '/auth/login',
    adminLogin: '/auth/admin/login',
    refresh: '/auth/refresh',
    verify: '/auth/verify',
    logout: '/auth/logout',
    roles: '/auth/roles',
  },
  users: {
    me: '/users/me',
    onboard: '/users/me/onboard',
    adminAll: '/users/admin/all',
    platformStatus: (userId: string | number) => `/users/${userId}/platform-status`,
  },
  health: {
    api: '/health',
    db: '/health/db',
    cache: '/health/cache',
    ready: '/health/ready',
  },
  insights: {
    audience: '/creators/insights/audience',
    content: '/creators/insights/content',
    performance: '/creators/insights/performance',
  },
  social: {
    googleLoginPrepare: '/auth/socials/oauth2/google/login',
    googleLoginCallback: '/auth/socials/google/login/callback',
  },
  ingestion: {
    youtubeMetrics: '/ingestion/youtube/metrics',
    youtubeOauthPrepare: '/ingestion/youtube/oauth2',
    youtubeOauthCallback: '/ingestion/youtube/oauth2/callback',
  },
  discovery: {
    creators: '/sme/creators/discovery',
    compare: '/sme/creators/compare',
    profile: (userId: string) => `/sme/creators/${userId}/profile`,
  },
} as const;
