"use client"
import React, { useState, useEffect } from 'react';
import {
  BookOpen, Star, Clock, CheckCircle2,
  FileText, ChevronRight, Zap, GraduationCap,
  Calendar, ArrowUpRight, Sparkles, Layout, CreditCard, Loader2
} from 'lucide-react';
import { getDashboardData, DashboardResponse, Application } from '@/lib/api';

// --- MOCK DATA (For User, Wallet, Subscription) ---
const mockUserData = {
  user: {
    id: "usr_99281",
    email: "alex@university.edu", // Student email
    created_at: "2025-04-01T10:00:00Z"
  },
  wallet: {
    balance_tokens: 1200,
    currency: "TOK",
    last_updated: "2025-11-23T11:20:00Z"
  },
  subscription: {
    status: "active",
    plan: {
      name: "Pro",
      interval: "monthly",
      price_cents: 999,
      tokens_per_period: 2000,
      features: {}
    },
    current_period_start: "2025-11-01T00:00:00Z",
    current_period_end: "2025-12-01T00:00:00Z"
  }
};

// --- HELPER COMPONENTS ---

const MatchBadge = ({ score }: { score: number | null }) => {
  let color = "bg-slate-100 text-slate-500";
  let text = "Pending";
  let Icon = Clock;

  if (score !== null) {
    if (score >= 80) {
      color = "bg-green-100 text-green-700";
      text = "Great Fit";
      Icon = Sparkles;
    } else if (score >= 60) {
      color = "bg-yellow-100 text-yellow-800";
      text = "Good Fit";
      Icon = Star;
    } else {
      color = "bg-red-100 text-red-700";
      text = "Low Match";
      Icon = Star;
    }
  }

  return (
    <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-bold ${color}`}>
      <Icon className="w-3.5 h-3.5" />
      <span>{text} {score !== null ? `(${Math.round(score)}%)` : ''}</span>
    </div>
  );
};

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null);
  const [userInfo, setUserInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch user ID first (similar to profile page)
        const userRes = await fetch('/api/logto/user');
        if (!userRes.ok) throw new Error('Failed to fetch user session');
        const userData = await userRes.json();
        setUserInfo(userData);

        if (userData.id) {
          const data = await getDashboardData(userData.id);
          setDashboardData(data);
        } else {
          throw new Error('User ID not found');
        }
      } catch (err) {
        console.error("Dashboard fetch error:", err);
        setError(err instanceof Error ? err.message : 'Failed to load dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-purple-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-bold text-slate-800 mb-2">Something went wrong</h2>
          <p className="text-slate-500">{error}</p>
          <button onClick={() => window.location.reload()} className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-lg font-bold">Retry</button>
        </div>
      </div>
    );
  }

  // Use API data or fallback to empty arrays
  const applications = dashboardData?.applications || [];
  const stats = dashboardData?.stats || {
    total_applications: 0,
    total_interviews: 0,
    average_match_score: 0,
    active_workflows_count: 0
  };

  // Combine applications and active workflows for recent activity if needed, 
  // or just use applications for now as the main list.
  // The API returns 'applications' separately.

  return (
    <div className="min-h-screen bg-[#F8FAFC] font-sans text-slate-600">

      {/* Top Navigation */}
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-purple-600 p-1.5 rounded-lg">
              <GraduationCap className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg text-slate-800">ScholarFit</span>
          </div>

          <div className="flex items-center gap-6">
            <a href="#" className="font-medium text-slate-900 border-b-2 border-purple-600 h-16 flex items-center">Dashboard</a>
            <a href="#" className="font-medium hover:text-purple-600 transition-colors">My Documents</a>
            <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold text-sm">
              AD
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-8">

        {/* Welcome Section */}
        <header className="mb-10">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Welcome back! 👋</h1>
          <p className="text-lg text-slate-500">You're making great progress. You have <strong className="text-purple-600">{stats.active_workflows_count} active applications</strong> this week.</p>
        </header>

        {/* Key Stats Row */}
        <div className="grid md:grid-cols-3 gap-6 mb-10">

          {/* Card 1: Credits */}
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-blue-50 rounded-2xl">
                <Zap className="w-6 h-6 text-blue-500" />
              </div>
              <span className="text-sm font-bold text-slate-400 uppercase">Pro Plan</span>
            </div>
            <div>
              <div className="text-3xl font-bold text-slate-900 mb-1">{mockUserData.wallet.balance_tokens}</div>
              <p className="text-sm text-slate-500">AI Credits available</p>
            </div>
          </div>

          {/* Card 2: Applications */}
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 flex flex-col justify-between hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-purple-50 rounded-2xl">
                <BookOpen className="w-6 h-6 text-purple-500" />
              </div>
            </div>
            <div>
              <div className="text-3xl font-bold text-slate-900 mb-1">{stats.total_applications}</div>
              <p className="text-sm text-slate-500">Scholarships found</p>
            </div>
          </div>

          {/* Card 3: Action Item (Motivational) */}
          <div className="bg-gradient-to-br from-purple-600 to-indigo-600 p-6 rounded-3xl shadow-lg text-white flex flex-col justify-between relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2" />

            <div className="relative z-10">
              <h3 className="font-bold text-lg mb-1">Find New Scholarships</h3>
              <p className="text-purple-100 text-sm mb-4">Upload a new resume version to find more matches.</p>
            </div>
            <button className="relative z-10 bg-white text-purple-700 font-bold py-2.5 px-4 rounded-xl text-sm w-fit hover:bg-purple-50 transition-colors">
              Analyze Resume +
            </button>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">

          {/* Left Column: Applications List (The main thing students care about) */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xl font-bold text-slate-900">My Applications</h2>
              <button className="text-sm font-bold text-purple-600 hover:text-purple-700">View All</button>
            </div>

            {applications.length === 0 ? (
              <div className="text-center py-10 bg-white rounded-3xl border border-slate-100">
                <p className="text-slate-400">No applications found yet.</p>
              </div>
            ) : (
              applications.map((app) => (
                <div key={app.id} className="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm hover:shadow-md transition-all group">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-bold text-slate-900 group-hover:text-purple-600 transition-colors">
                        Scholarship Application
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-slate-500 mt-1">
                        <FileText className="w-4 h-4" />
                        {/* Resume filename is not directly in Application object, would need to join with resumes list if needed */}
                        <span>Application ID: {app.id.substring(0, 8)}</span>
                      </div>
                    </div>
                    <MatchBadge score={app.match_score} />
                  </div>

                  {/* Progress Bar Visual */}
                  <div className="mb-6">
                    <div className="flex justify-between text-xs font-bold text-slate-400 mb-2 uppercase tracking-wide">
                      <span>Progress</span>
                      <span>{app.status === 'complete' ? 'Ready to Apply' : 'Drafting'}</span>
                    </div>
                    <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${app.status === 'complete' ? 'bg-green-500' :
                          app.status === 'error' ? 'bg-red-500' : 'bg-blue-500'
                          }`}
                        style={{ width: app.status === 'complete' ? '100%' : '50%' }}
                      ></div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {/* Primary Action Button */}
                    {app.status === 'complete' ? (
                      <button className="flex-1 bg-slate-900 text-white font-bold py-3 rounded-xl hover:bg-slate-800 transition-colors flex items-center justify-center gap-2">
                        <CheckCircle2 className="w-4 h-4" /> View Final Essay
                      </button>
                    ) : (
                      <button className="flex-1 bg-blue-600 text-white font-bold py-3 rounded-xl hover:bg-blue-700 transition-colors flex items-center justify-center gap-2">
                        Continue Application
                      </button>
                    )}

                    {/* Secondary Action */}
                    <a href={app.scholarship_url} target="_blank" rel="noreferrer" className="px-4 py-3 bg-slate-100 text-slate-600 font-bold rounded-xl hover:bg-slate-200 transition-colors">
                      <ArrowUpRight className="w-5 h-5" />
                    </a>
                  </div>
                </div>
              ))
            )}

            {/* Empty State / Add New */}
            <button className="w-full py-6 rounded-3xl border-2 border-dashed border-slate-200 text-slate-400 font-bold hover:border-purple-400 hover:text-purple-600 hover:bg-purple-50 transition-all flex flex-col items-center gap-2">
              <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center">
                <Sparkles className="w-5 h-5" />
              </div>
              Start a new application
            </button>
          </div>

          {/* Right Column: Recent Activity & Calendar */}
          <div className="space-y-8">

            {/* Recent Activity List - Using Mock Data for now as API doesn't return activity feed directly */}
            <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
              <h3 className="font-bold text-slate-900 mb-6 flex items-center gap-2">
                <Clock className="w-5 h-5 text-slate-400" /> Recent Activity
              </h3>

              <div className="space-y-6">
                {/* Placeholder for activity feed */}
                <p className="text-sm text-slate-400 italic">Activity feed coming soon...</p>
              </div>
            </div>

            {/* Account Mini-Summary */}
            <div className="bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
              <h3 className="font-bold text-slate-900 mb-4">My Account</h3>

              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center text-xl">🎓</div>
                <div>
                  <div className="font-bold text-slate-900">{userInfo?.name || 'User'}</div>
                  <div className="text-xs text-slate-500">{userInfo?.primaryEmail || userInfo?.email || 'No email'}</div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm p-3 bg-slate-50 rounded-xl">
                  <span className="text-slate-500 flex items-center gap-2">
                    <Calendar className="w-4 h-4" /> Next Renewal
                  </span>
                  <span className="font-bold text-slate-700">Dec 1, 2025</span>
                </div>
                <div className="flex justify-between items-center text-sm p-3 bg-slate-50 rounded-xl">
                  <span className="text-slate-500 flex items-center gap-2">
                    <CreditCard className="w-4 h-4" /> Plan
                  </span>
                  <span className="font-bold text-purple-600">Pro Student</span>
                </div>
              </div>

              <button className="w-full mt-4 py-2 text-sm font-bold text-slate-400 hover:text-slate-600 transition-colors">
                Manage Subscription
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;