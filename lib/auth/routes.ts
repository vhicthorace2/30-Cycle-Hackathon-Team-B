export type AuthRole = 'admin' | 'user' | 'sme' | 'creator';

export function getPostLoginRoute(role?: AuthRole | null) {
  return '/dashboard';
}
