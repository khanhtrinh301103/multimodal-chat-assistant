// frontend/src/components/Auth/AuthProvider.tsx
'use client';

import React, { createContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation'; // ✅ Add this import
import { supabase } from '@/lib/supabase';
import { User as SupabaseUser } from '@supabase/supabase-js';
import { User } from '@/types/user';

interface AuthContextType {
  user: User | null;
  supabaseUser: SupabaseUser | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<{ error: string | null }>;
  signUp: (email: string, password: string, fullName: string) => Promise<{ error: string | null }>;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [supabaseUser, setSupabaseUser] = useState<SupabaseUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter(); // ✅ Add this

  // Fetch user profile from public.users table
  const fetchUserProfile = async (userId: string): Promise<User | null> => {
    try {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('id', userId)
        .single();

      if (error) {
        console.error('Error fetching user profile:', error);
        return null;
      }

      return data as User;
    } catch (err) {
      console.error('Error fetching user profile:', err);
      return null;
    }
  };

  // Load user session on mount
  useEffect(() => {
    const loadSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        
        if (session?.user) {
          setSupabaseUser(session.user);
          const profile = await fetchUserProfile(session.user.id);
          setUser(profile);
        }
      } catch (error) {
        console.error('Error loading session:', error);
      } finally {
        setLoading(false);
      }
    };

    loadSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth event:', event);
        
        if (session?.user) {
          setSupabaseUser(session.user);
          const profile = await fetchUserProfile(session.user.id);
          setUser(profile);
        } else {
          setSupabaseUser(null);
          setUser(null);
        }
        
        setLoading(false);
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // Sign in
  const signIn = async (email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        return { error: error.message };
      }

      if (data.user) {
        const profile = await fetchUserProfile(data.user.id);
        setUser(profile);
        setSupabaseUser(data.user);
      }

      return { error: null };
    } catch (err: any) {
      return { error: err.message || 'An error occurred during sign in' };
    }
  };

  // Sign up
  const signUp = async (email: string, password: string, fullName: string) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
          },
        },
      });

      if (error) {
        return { error: error.message };
      }

      // Profile will be auto-created by database trigger
      // Wait a moment then fetch it
      if (data.user) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        const profile = await fetchUserProfile(data.user.id);
        setUser(profile);
        setSupabaseUser(data.user);
      }

      return { error: null };
    } catch (err: any) {
      return { error: err.message || 'An error occurred during sign up' };
    }
  };

  // Sign out - ✅ UPDATED WITH REDIRECT
  const signOut = async () => {
    try {
      console.log('Signing out...');
      
      // Sign out from Supabase
      await supabase.auth.signOut();
      
      // Clear state
      setUser(null);
      setSupabaseUser(null);
      
      // Clear storage
      localStorage.clear();
      sessionStorage.clear();
      
      console.log('Sign out successful, redirecting to /auth');
      
      // Redirect to auth page
      router.push('/auth');
    } catch (error) {
      console.error('Error signing out:', error);
      alert('Failed to sign out. Please try again.');
    }
  };

  // Refresh user profile
  const refreshUser = async () => {
    if (supabaseUser) {
      const profile = await fetchUserProfile(supabaseUser.id);
      setUser(profile);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        supabaseUser,
        loading,
        signIn,
        signUp,
        signOut,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
