"use client";

import { useState } from 'react';
import { supabase } from '@/lib/supabase';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const router = useRouter();

  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isSignUp) {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
        alert('Check your email for the confirmation link!');
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        router.push('/test'); // Redirect to test page on success
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo/Brand */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent mb-2">
            JEE Diagnostic
          </h1>
          <p className="text-slate-400">AI-Powered Preparation Platform</p>
        </div>

        {/* Card */}
        <div className="bg-slate-800 p-8 rounded-2xl border border-slate-700 shadow-xl backdrop-blur-md bg-opacity-70">
          <h2 className="text-2xl font-bold mb-6 text-center">
            {isSignUp ? 'Create an Account' : 'Welcome Back'}
          </h2>

          <form onSubmit={handleAuth} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full p-3 rounded-lg bg-slate-900 border border-slate-700 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-3 rounded-lg bg-slate-900 border border-slate-700 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
                placeholder="••••••••"
                required
              />
            </div>

            {error && (
              <div className="text-red-400 text-sm bg-red-900 bg-opacity-20 p-3 rounded-lg border border-red-800">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white p-3 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {loading ? 'Processing...' : isSignUp ? 'Sign Up' : 'Log In'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-slate-400">
            {isSignUp ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              onClick={() => setIsSignUp(!isSignUp)}
              className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
            >
              {isSignUp ? 'Log In' : 'Sign Up'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
