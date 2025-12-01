"use client"
import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import {
  BookOpen, Star, Clock, CheckCircle2,
  FileText, ChevronRight, Zap, GraduationCap,
  Calendar, ArrowUpRight, Sparkles, Layout, CreditCard, Loader2, Settings
} from 'lucide-react';
import { getDashboardData, DashboardResponse, DashboardApplication, DashboardWorkflow } from '@/lib/api';
import { useAuthClient } from '@/hooks/useAuthClient';

// --- MOCK DATA (For User, Wallet, Subscription) ---
const mockUserData = {
  user: {
    id: "usr_99281",
    email: "alex@university.edu",
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
  // Dark mode optimized colors (translucent backgrounds + bright text)
  let color = "bg-slate-800 text-slate-400";
  let text = "Pending";
  let Icon = Clock;

  if (score !== null) {
    if (score >= 80) {
      color = "bg-green-500/10 text-green-400 border border-green-500/20";
      text = "Great Fit";
      Icon = Sparkles;
    } else if (score >= 60) {
      color = "bg-yellow-500/10 text-yellow-400 border border-yellow-500/20";
      text = "Good Fit";
      Icon = Star;
    } else {
      color = "bg-red-500/10 text-red-400 border border-red-500/20";
      text = "Low Match";
      Icon = Star;
    }
  }

  return (
    <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${color}`}>
      <Icon className="w-3.5 h-3.5" />
      <span>{text} {score !== null ? `(${Math.round(score)}%)` : ''}</span>
    </div>
  );
};

const Dashboard = () => {
  const searchParams = useSearchParams();
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null);
  const [userInfo, setUserInfo] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [checkoutStatus, setCheckoutStatus] = useState<'success' | 'canceled' | null>(null);

  useEffect(() => {
    const status = searchParams.get('checkout');
    if (status === 'success' || status === 'canceled') {
      setCheckoutStatus(status as 'success' | 'canceled');
      setTimeout(() => {
        window.history.replaceState({}, '', '/dashboard');
        setCheckoutStatus(null);
      }, 5000);
    }
  }, [searchParams]);

  const { user, isLoading: isAuthLoading } = useAuthClient();

  useEffect(() => {
    let isMounted = true;
    let pollInterval: NodeJS.Timeout;
    let pollCount = 0;
    const maxPolls = 5; // Poll for 10 seconds (5 * 2000ms)

    const fetchData = async (isPolling = false) => {
      if (!user) return;

      try {
        if (!isPolling) setLoading(true);

        setUserInfo({
          id: user.sub,
          email: user.email,
          name: user.name
        });

        const data = await getDashboardData(user.sub);

        if (isMounted) {
          console.log("Dashboard data:", data);
          setDashboardData(data);

          // If we're polling and found an active subscription, stop polling
          if (isPolling && data.subscription?.status === 'active') {
            console.log("Subscription activated, stopping poll");
            return true; // Stop polling
          }
        }
      } catch (err) {
        console.error("Dashboard fetch error:", err);
        if (isMounted && !isPolling) {
          setError(err instanceof Error ? err.message : 'Failed to load dashboard');
        }
      } finally {
        if (isMounted && !isPolling) {
          setLoading(false);
        }
      }
      return false; // Continue polling if needed
    };

    if (!isAuthLoading) {
      if (user) {
        // Initial fetch
        fetchData();

        // If coming from success checkout, start polling
        if (searchParams.get('checkout') === 'success') {
          console.log("Starting subscription poll...");
          pollInterval = setInterval(async () => {
            pollCount++;
            console.log(`Poll attempt ${pollCount}/${maxPolls}`);
            const shouldStop = await fetchData(true);

            if (shouldStop || pollCount >= maxPolls) {
              clearInterval(pollInterval);
            }
          }, 2000);
        }
      } else {
        setLoading(false);
      }
    }

    return () => {
      isMounted = false;
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [user, isAuthLoading, searchParams]);

  // Loading State - Dark Mode
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-purple-500" />
      </div>
    );
  }

  // Error State - Dark Mode
  if (error) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-bold text-white mb-2">Something went wrong</h2>
          <p className="text-slate-400">{error}</p>
          <button onClick={() => window.location.reload()} className="mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-bold transition-colors">Retry</button>
        </div>
      </div>
    );
  }

  // Extract data from new API structure
  const resumeSessions = dashboardData?.resume_sessions || [];
  const recentActivity = dashboardData?.recent_activity || [];

  // Flatten all applications
  const allApplications: DashboardApplication[] = [];
  let activeWorkflowsCount = 0;

  resumeSessions.forEach(resume => {
    resume.workflow_sessions.forEach(workflow => {
      if (workflow.status === 'processing' || workflow.status === 'waiting_for_input') {
        activeWorkflowsCount++;
      }
      workflow.applications.forEach(app => {
        allApplications.push(app);
      });
    });
  });

  const totalApplications = allApplications.length;

  return (
    <div className="min-h-screen bg-slate-950 font-sans text-slate-300 selection:bg-purple-500/30">

      {/* Top Navigation - Dark Mode */}
      <nav className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-30">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-purple-600 p-1.5 rounded-lg">
              <GraduationCap className="w-5 h-5 text-white" />
            </div>
            <a href="/" className="font-bold text-lg text-white hover:text-purple-400 transition-colors">ScholarFit</a>
          </div>

          <div className="flex items-center gap-6">
            <a href="/dashboard" className="font-medium text-white border-b-2 border-purple-500 h-16 flex items-center">Dashboard</a>
            {/* "My Documents" Removed */}
            <a href="/dashboard/profile" className="w-8 h-8 rounded-full bg-slate-800 text-purple-400 border border-slate-700 flex items-center justify-center font-bold text-sm hover:bg-slate-700 hover:text-purple-300 transition-colors">
              {userInfo?.name ? userInfo.name.charAt(0).toUpperCase() : 'U'}
            </a>
          </div>
        </div>
      </nav>

      {/* Checkout Status Notifications */}
      {checkoutStatus === 'success' && (
        <div className="bg-green-500/10 border-b border-green-500/20 px-6 py-4">
          <div className="max-w-6xl mx-auto flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-400" />
            <div>
              <p className="font-bold text-green-400">Subscription activated!</p>
              <p className="text-sm text-green-300/80">Your payment was successful. Welcome to ScholarFit Pro!</p>
            </div>
          </div>
        </div>
      )}
      {checkoutStatus === 'canceled' && (
        <div className="bg-yellow-500/10 border-b border-yellow-500/20 px-6 py-4">
          <div className="max-w-6xl mx-auto flex items-center gap-3">
            <Clock className="w-5 h-5 text-yellow-400" />
            <div>
              <p className="font-bold text-yellow-400">Checkout canceled</p>
              <p className="text-sm text-yellow-300/80">You can subscribe anytime from the pricing page.</p>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-6xl mx-auto px-6 py-8">

        {/* Welcome Section */}
        <header className="mb-10">
          <h1 className="text-3xl font-bold text-white mb-2">Welcome back! 👋</h1>
          <p className="text-lg text-slate-400">You're making great progress. You have <strong className="text-purple-400">{activeWorkflowsCount} active applications</strong> this week.</p>
        </header>

        {/* Key Stats Row */}
        <div className="grid md:grid-cols-3 gap-6 mb-10">

          {/* Card 1: Credits */}
          <div className="bg-slate-900 p-6 rounded-3xl shadow-lg border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition-all">
            <div className="flex items-start justify-between mb-4">
              {/* Changed from bg-blue-50 to translucent bg */}
              <div className="p-3 bg-blue-500/10 rounded-2xl border border-blue-500/20">
                <Zap className="w-6 h-6 text-blue-400" />
              </div>
              <span className="text-sm font-bold text-slate-500 uppercase">{dashboardData?.subscription?.plan.name} PLAN</span>
            </div>
            <div>
              <div className="text-3xl font-bold text-white mb-1">{dashboardData?.wallet?.balance_tokens || mockUserData.wallet.balance_tokens}</div>
              <p className="text-sm text-slate-400">AI Credits available</p>
            </div>
          </div>

          {/* Card 2: Applications */}
          <div className="bg-slate-900 p-6 rounded-3xl shadow-lg border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition-all">
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 bg-purple-500/10 rounded-2xl border border-purple-500/20">
                <BookOpen className="w-6 h-6 text-purple-400" />
              </div>
            </div>
            <div>
              <div className="text-3xl font-bold text-white mb-1">{totalApplications}</div>
              <p className="text-sm text-slate-400">Scholarships found</p>
            </div>
          </div>

          {/* Card 3: Action Item (Motivational) */}
          <div className="bg-gradient-to-br from-purple-700 to-indigo-800 p-6 rounded-3xl shadow-lg text-white flex flex-col justify-between relative overflow-hidden border border-purple-500/30">
            <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2" />

            <div className="relative z-10">
              <h3 className="font-bold text-lg mb-1">Find New Scholarships</h3>
              <p className="text-purple-100/80 text-sm mb-4">Upload a new resume version to find more matches.</p>
            </div>
            <button
              onClick={() => window.location.href = '/start'}
              className="relative z-10 bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 text-white font-bold py-2.5 px-4 rounded-xl text-sm w-fit transition-colors"
            >
              Analyze Resume +
            </button>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">

          {/* Left Column: Applications List */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xl font-bold text-white">My Applications</h2>
              <button className="text-sm font-bold text-purple-400 hover:text-purple-300">View All</button>
            </div>

            {allApplications.length === 0 ? (
              <div className="text-center py-10 bg-slate-900 rounded-3xl border border-slate-800">
                <p className="text-slate-500">No applications found yet.</p>
              </div>
            ) : (
              allApplications.map((app: DashboardApplication) => (
                <div key={app.id} className="bg-slate-900 rounded-3xl p-6 border border-slate-800 shadow-sm hover:border-slate-700 transition-all group">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-lg font-bold text-white group-hover:text-purple-400 transition-colors">
                        Scholarship Application
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-slate-500 mt-1">
                        <FileText className="w-4 h-4" />
                        <span>Application ID: {app.id.substring(0, 8)}</span>
                      </div>
                    </div>
                    <MatchBadge score={app.match_score} />
                  </div>

                  {/* Progress Bar Visual */}
                  <div className="mb-6">
                    <div className="flex justify-between text-xs font-bold text-slate-500 mb-2 uppercase tracking-wide">
                      <span>Progress</span>
                      <span>{app.status === 'complete' ? 'Ready to Apply' : 'Drafting'}</span>
                    </div>
                    {/* Darker track for progress bar */}
                    <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden">
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
                      <button
                        onClick={() => window.location.href = `/application?session=${app.session_id}`}
                        className="flex-1 bg-white text-slate-900 font-bold py-3 rounded-xl hover:bg-slate-200 transition-colors flex items-center justify-center gap-2"
                      >
                        <CheckCircle2 className="w-4 h-4" /> View Final Essay
                      </button>
                    ) : (
                      <button
                        onClick={() => window.location.href = `/matchmaker?session=${app.session_id}`}
                        className="flex-1 bg-blue-600 text-white font-bold py-3 rounded-xl hover:bg-blue-500 transition-colors flex items-center justify-center gap-2 shadow-lg shadow-blue-900/20"
                      >
                        Continue Application
                      </button>
                    )}

                    {/* Secondary Action - Darkened */}
                    <a href={app.scholarship_url} target="_blank" rel="noreferrer" className="px-4 py-3 bg-slate-800 text-slate-400 font-bold rounded-xl hover:bg-slate-700 hover:text-white transition-colors border border-slate-700">
                      <ArrowUpRight className="w-5 h-5" />
                    </a>
                  </div>
                </div>
              ))
            )}

            {/* Empty State / Add New */}
            <button
              onClick={() => window.location.href = '/start'}
              className="w-full py-6 rounded-3xl border-2 border-dashed border-slate-800 text-slate-500 font-bold hover:border-purple-500/50 hover:text-purple-400 hover:bg-slate-900/50 transition-all flex flex-col items-center gap-2"
            >
              <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-slate-400" />
              </div>
              Start a new application
            </button>
          </div>

          {/* Right Column: Recent Activity & Calendar */}
          <div className="space-y-8">

            {/* Recent Activity List */}
            <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-lg">
              <h3 className="font-bold text-white mb-6 flex items-center gap-2">
                <Clock className="w-5 h-5 text-slate-500" /> Recent Activity
              </h3>

              <div className="space-y-4">
                {recentActivity.length === 0 ? (
                  <p className="text-sm text-slate-500 italic">No recent activity</p>
                ) : (
                  recentActivity.slice(0, 5).map((activity, idx) => (
                    <div key={`${activity.ref_id}-${idx}`} className="flex items-start gap-3 pb-4 border-b border-slate-800 last:border-0">
                      <div className="w-8 h-8 bg-slate-800 rounded-full flex items-center justify-center flex-shrink-0 border border-slate-700">
                        {activity.type === 'transaction_deduction' && <Zap className="w-4 h-4 text-purple-400" />}
                        {activity.type === 'transaction_purchase' && <CreditCard className="w-4 h-4 text-green-400" />}
                        {activity.type === 'workflow_completed' && <CheckCircle2 className="w-4 h-4 text-blue-400" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-200 truncate">{activity.description}</p>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {new Date(activity.timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                      {activity.amount !== undefined && (
                        <span className={`text-sm font-bold ${activity.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                          {activity.amount > 0 ? '+' : ''}{activity.amount}
                        </span>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Account Mini-Summary */}
            <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-lg">
              <h3 className="font-bold text-white mb-4">My Account</h3>

              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-slate-800 border border-slate-700 rounded-full flex items-center justify-center text-xl">🎓</div>
                <div>
                  <div className="font-bold text-white">{userInfo?.name || 'User'}</div>
                  <div className="text-xs text-slate-500">{userInfo?.primaryEmail || userInfo?.email || 'No email'}</div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm p-3 bg-slate-800/50 rounded-xl border border-slate-800">
                  <span className="text-slate-400 flex items-center gap-2">
                    <Calendar className="w-4 h-4" /> Next Renewal
                  </span>
                  <span className="font-bold text-slate-200">
                    {dashboardData?.subscription?.current_period_end
                      ? new Date(dashboardData.subscription.current_period_end).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                      : 'Dec 1, 2025'}
                  </span>
                </div>
                <div className="flex justify-between items-center text-sm p-3 bg-slate-800/50 rounded-xl border border-slate-800">
                  <span className="text-slate-400 flex items-center gap-2">
                    <CreditCard className="w-4 h-4" /> Plan
                  </span>
                  <span className="font-bold text-purple-400">{dashboardData?.subscription?.plan?.name || 'Pro Student'}</span>
                </div>
              </div>

              <div className="flex gap-2 mt-4">
                <button
                  onClick={() => {
                    window.location.href = '/subscription';
                  }}
                  className="flex-1 py-2.5 text-sm font-bold text-white bg-purple-600 hover:bg-purple-500 rounded-lg transition-colors flex items-center justify-center gap-1 shadow-lg shadow-purple-900/20"
                >
                  <CreditCard className="w-4 h-4" />
                  View Billing
                </button>
                <button
                  onClick={async () => {
                    if (!userInfo?.id) return;
                    try {
                      const { createPortalSession } = await import('@/lib/api');
                      const { url } = await createPortalSession(userInfo.id, window.location.href);
                      window.location.href = url;
                    } catch (error) {
                      console.error('Failed to open portal:', error);
                      alert('Failed to open subscription management. Please try again.');
                    }
                  }}
                  className="flex-1 py-2.5 text-sm font-bold text-slate-300 hover:text-white border border-slate-700 hover:border-slate-600 hover:bg-slate-800 rounded-lg transition-colors flex items-center justify-center gap-1"
                >
                  <Settings className="w-4 h-4" />
                  Manage
                </button>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;