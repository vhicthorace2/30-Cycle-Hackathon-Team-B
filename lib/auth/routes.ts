export type AuthRole = 'admin' | 'user' | 'sme' | 'creator';

export function getPostLoginRoute() {
  return '/dashboard';
}
