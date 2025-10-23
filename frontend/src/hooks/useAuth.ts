// frontend/src/hooks/useAuth.ts
'use client';

import { useContext } from 'react';
import { AuthContext } from '@/components/Auth/AuthProvider';

export function useAuth() {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}