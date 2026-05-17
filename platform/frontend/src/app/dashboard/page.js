"use client";

import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function DashboardPage() {
  const [user, setUser] = useState(null);
  const [attempts, setAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    async function checkSession() {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        router.push('/login');
      } else {
        setUser(user);
        fetchAttempts(user.id);
      }
    }
    checkSession();
  }, [router]);
  const fetchAttempts = async (userId) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/test-attempts/${userId}`);
      const data = await response.json();
      setAttempts(data);
    } catch (error) {
      console.error("Error fetching attempts:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-slate-100 flex items-center justify-center">
        <div className="text-xl font-bold">Loading dashboard...</div>
      </div>
    );
  }

  // Prepare Chart Data
  const chartData = attempts
    .filter(a => a.score !== null)
    .sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
    .map((attempt, index) => ({
      name: `Attempt ${index + 1}`,
      score: attempt.score,
      date: new Date(attempt.start_time).toLocaleDateString()
    }));

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col p-8">
      {/* Header */}
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">Student Dashboard</h1>
          <p className="text-slate-400">Welcome back, {user?.email}</p>
        </div>
        <div className="flex gap-4">
          <Link href="/test">
            <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2.5 rounded-lg font-medium transition-colors">
              Start New Test
            </button>
          </Link>
          <button 
            onClick={handleLogout}
            className="bg-slate-700 hover:bg-slate-600 text-white px-5 py-2.5 rounded-lg font-medium transition-colors"
          >
            Log Out
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Profile Summary */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700">
          <h2 className="text-lg font-bold text-indigo-400 mb-4">Profile Summary</h2>
          <div className="space-y-2 text-sm">
            <p><span className="text-slate-400">Email:</span> {user?.email}</p>
            <p><span className="text-slate-400">Tests Attempted:</span> {attempts.length}</p>
          </div>
        </div>

        {/* Recent Attempts */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 md:col-span-2">
          <h2 className="text-lg font-bold text-indigo-400 mb-4">Recent Test Attempts</h2>
          
          {attempts.length === 0 ? (
            <div className="text-slate-500 text-center py-8">
              No tests attempted yet. Click "Start New Test" to begin!
            </div>
          ) : (
            <div className="space-y-4">
              {attempts.map((attempt) => (
                <div key={attempt.id} className="flex justify-between items-center bg-slate-750 p-4 rounded-lg hover:bg-slate-700 transition-colors">
                  <div>
                    <p className="font-medium">Attempt #{attempt.id}</p>
                    <p className="text-xs text-slate-500">{new Date(attempt.start_time).toLocaleString()}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={`text-sm font-bold ${attempt.status === 'Completed' ? 'text-emerald-400' : 'text-yellow-400'}`}>
                      {attempt.status}
                    </span>
                    <span className="text-lg font-bold text-indigo-400">
                      {attempt.score !== null ? `${attempt.score} pts` : '--'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Chart Card */}
        {chartData.length > 0 && (
          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 md:col-span-3">
            <h2 className="text-lg font-bold text-indigo-400 mb-4">Performance Trend</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '0.5rem' }}
                    labelStyle={{ color: '#f8fafc' }}
                    itemStyle={{ color: '#6366f1' }}
                  />
                  <Line type="monotone" dataKey="score" stroke="#6366f1" strokeWidth={3} dot={{ fill: '#6366f1' }} activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
