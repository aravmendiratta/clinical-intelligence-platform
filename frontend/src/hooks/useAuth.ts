// frontend/src/hooks/useAuth.ts
import { createContext, useContext } from 'react';

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
}

const DEMO_USER: User = {
  id: 'demo-reviewer-id',
  email: 'demo@medintel.ai',
  full_name: 'Reviewer',
  role: 'admin',
  is_active: true,
  is_superuser: true,
};

export const AuthContext = createContext<AuthContextType>({
  user: DEMO_USER,
  token: 'demo-token',
  loading: false,
  isAuthenticated: true,
});

export function useAuthProvider(): AuthContextType {
  // Always return the demo admin user so recruiters/reviewers can evaluate the entire application without login blocks
  return {
    user: DEMO_USER,
    token: 'demo-token',
    loading: false,
    isAuthenticated: true,
  };
}

export function useAuth() {
  return useContext(AuthContext);
}
