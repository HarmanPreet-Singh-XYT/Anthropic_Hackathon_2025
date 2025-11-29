"use client"
import React, { useState } from 'react';
import { 
  CreditCard, CheckCircle2, Zap, Calendar, 
  Download, ArrowUpRight, GraduationCap, 
  TrendingUp, Activity, ShieldCheck
} from 'lucide-react';

const SubscriptionPage = () => {
  const [isDark, setIsDark] = useState(true);

  // Mock Data
  const plan = {
    name: "PRO SCHOLAR",
    status: "active",
    cost: "$9.99",
    cycle: "monthly",
    renewal: "2025-12-01",
    usage: 1240,
    limit: 2000
  };

  const usagePercent = (plan.usage / plan.limit) * 100;

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDark ? 'dark bg-slate-950' : 'bg-slate-50'}`}>
      <div className="font-sans selection:bg-purple-500/30 selection:text-purple-600 dark:selection:text-purple-300 dark:text-slate-100">
        
        {/* Same Navbar Wrapper as Profile (Simplified for brevity) */}
        <nav className="sticky top-0 z-50 w-full backdrop-blur-xl bg-white/70 dark:bg-slate-950/70 border-b border-slate-200/50 dark:border-slate-800">
           <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2 font-black text-xl tracking-tighter text-slate-900 dark:text-white">
              <div className="w-8 h-8 bg-gradient-to-tr from-blue-600 to-purple-600 rounded-lg flex items-center justify-center text-white shadow-lg shadow-blue-500/30">
                <GraduationCap className="w-5 h-5" />
              </div>
              ScholarFit<span className="text-purple-600">.ai</span>
            </div>
            <button onClick={() => setIsDark(!isDark)} className="text-xs font-mono font-bold uppercase text-slate-500 hover:text-purple-500 transition-colors">
              {isDark ? "Light Mode" : "Dark Mode"}
            </button>
          </div>
        </nav>

        <main className="relative max-w-7xl mx-auto px-6 py-12">
          
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700/50 text-green-700 dark:text-green-300 text-xs font-bold font-mono tracking-wider mb-4 animate-fade-in-up">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                SUBSCRIPTION ACTIVE
              </div>
              <h1 className="text-4xl md:text-5xl font-black text-slate-900 dark:text-white tracking-tighter">
                Resource Allocation
              </h1>
            </div>
            
            {/* Action Buttons */}
            <div className="flex gap-4">
              <button className="px-6 py-3 rounded-xl border border-slate-200 dark:border-slate-700 font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-900 transition-colors">
                Billing History
              </button>
              <button className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold shadow-lg shadow-purple-500/25 hover:scale-105 transition-all">
                Manage Plan
              </button>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            
            {/* Left Col: Plan & Usage */}
            <div className="md:col-span-2 space-y-8">
              
              {/* Plan Card - Tech Style */}
              <div className="relative overflow-hidden bg-slate-900 text-white rounded-3xl p-8 border border-slate-800 shadow-2xl">
                <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/20 rounded-full blur-[100px] pointer-events-none -translate-y-1/2 translate-x-1/2"></div>
                
                <div className="relative z-10 flex justify-between items-start">
                  <div>
                    <h3 className="font-mono text-slate-400 text-xs uppercase tracking-widest mb-2">Current Tier</h3>
                    <div className="text-4xl font-black tracking-tight mb-2 bg-clip-text text-transparent bg-gradient-to-r from-white via-blue-100 to-purple-200">
                      {plan.name}
                    </div>
                    <div className="flex items-center gap-2 text-slate-300 font-mono text-sm">
                      <span className="text-white font-bold">{plan.cost}</span> / {plan.cycle}
                      <span className="w-1 h-1 rounded-full bg-slate-500"></span>
                      Renews {plan.renewal}
                    </div>
                  </div>
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-white/10 flex items-center justify-center backdrop-blur-md">
                    <ShieldCheck className="w-7 h-7 text-white" />
                  </div>
                </div>

                {/* Features List Mini */}
                <div className="mt-8 flex gap-6 text-sm font-medium text-slate-300">
                  <span className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-400" /> All Agents Unlocked</span>
                  <span className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-green-400" /> Priority Support</span>
                </div>
              </div>

              {/* Usage Reactor */}
              <div className="bg-white dark:bg-slate-900/50 backdrop-blur-md rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl p-8">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="flex items-center gap-2 font-bold text-slate-900 dark:text-white">
                    <Activity className="w-5 h-5 text-purple-500" />
                    Compute Usage
                  </h3>
                  <span className="text-xs font-mono font-bold text-slate-500 dark:text-slate-400">
                    {plan.usage} / {plan.limit} TOKENS
                  </span>
                </div>

                <div className="relative h-6 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden shadow-inner">
                  <div 
                    className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 transition-all duration-1000 ease-out"
                    style={{ width: `${usagePercent}%` }}
                  >
                    {/* Animated shine effect */}
                    <div className="absolute top-0 right-0 bottom-0 w-full bg-gradient-to-r from-transparent via-white/20 to-transparent -skew-x-12 translate-x-[-100%] animate-[shimmer_2s_infinite]"></div>
                  </div>
                </div>
                
                <p className="mt-4 text-xs text-slate-500 dark:text-slate-400 font-mono">
                  Cycle resets in <span className="text-slate-900 dark:text-white font-bold">12 days</span>.
                </p>
              </div>

              {/* Invoice Table - Terminal Style */}
              <div className="bg-white dark:bg-slate-900/50 backdrop-blur-md rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl overflow-hidden">
                <div className="px-8 py-6 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center">
                  <h3 className="font-bold text-slate-900 dark:text-white">Transaction Log</h3>
                  <Download className="w-4 h-4 text-slate-400" />
                </div>
                <table className="w-full text-sm text-left">
                  <thead className="bg-slate-50 dark:bg-slate-950/50 text-xs font-mono text-slate-500 uppercase tracking-wider">
                    <tr>
                      <th className="px-8 py-4">Invoice ID</th>
                      <th className="px-8 py-4">Date</th>
                      <th className="px-8 py-4">Amount</th>
                      <th className="px-8 py-4 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {[1, 2, 3].map((i) => (
                      <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors group cursor-pointer">
                        <td className="px-8 py-4 font-mono text-slate-500 dark:text-slate-400 group-hover:text-purple-600 transition-colors">
                          INV-2025-00{i}
                        </td>
                        <td className="px-8 py-4 font-bold text-slate-900 dark:text-white">Nov 0{i}, 2025</td>
                        <td className="px-8 py-4 font-mono text-slate-600 dark:text-slate-300">$9.99</td>
                        <td className="px-8 py-4 text-right">
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-800 uppercase tracking-wide">
                            Paid
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

            </div>

            {/* Right Col: Payment Method */}
            <div className="space-y-6">
              
              {/* Glass Credit Card */}
              <div className="relative h-56 rounded-3xl p-8 text-white shadow-2xl overflow-hidden group">
                {/* Background Gradient */}
                <div className="absolute inset-0 bg-gradient-to-br from-slate-800 to-black z-0"></div>
                <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/20 rounded-full blur-3xl z-0 -translate-y-1/2 translate-x-1/2 group-hover:bg-purple-500/30 transition-colors"></div>
                
                {/* Card Content */}
                                <div className="relative z-10 flex flex-col justify-between h-full">
                  <div className="flex justify-between items-start">
                    <CreditCard className="w-8 h-8 text-slate-400" />
                    <span className="font-mono text-xs bg-white/10 px-2 py-1 rounded backdrop-blur-md">
                      PRIMARY
                    </span>
                  </div>
                  
                  <div className="space-y-1">
                    <div className="font-mono text-xl tracking-widest text-slate-300">
                      •••• •••• •••• 4242
                    </div>
                  </div>

                  <div className="flex justify-between items-end">
                    <div>
                      <div className="text-[10px] text-slate-400 uppercase tracking-widest mb-1">Card Holder</div>
                      <div className="font-bold text-sm tracking-wide">ALEX DEVELOPER</div>
                    </div>
                    <div className="text-right">
                       <div className="text-[10px] text-slate-400 uppercase tracking-widest mb-1">Expires</div>
                       <div className="font-mono text-sm font-bold">12/28</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Payment Actions */}
              <div className="bg-white dark:bg-slate-900/50 backdrop-blur-md rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl p-6">
                <h3 className="font-bold text-slate-900 dark:text-white mb-4">Payment Configuration</h3>
                <div className="flex items-center gap-4 mb-6 p-3 bg-slate-50 dark:bg-slate-950 rounded-xl border border-slate-100 dark:border-slate-800">
                   <div className="w-12 h-8 bg-white dark:bg-slate-800 rounded border border-slate-200 dark:border-slate-700 flex items-center justify-center font-bold text-xs italic text-slate-800 dark:text-slate-200">
                     VISA
                   </div>
                   <div>
                     <div className="text-sm font-bold text-slate-900 dark:text-white">Visa ending in 4242</div>
                     <div className="text-xs text-slate-500 font-mono">Added Nov 2024</div>
                   </div>
                </div>
                <button className="w-full py-3 rounded-xl border border-slate-200 dark:border-slate-700 font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors text-sm">
                  Update Payment Method
                </button>
              </div>

              {/* Enterprise Upsell */}
              <div className="bg-gradient-to-br from-blue-900 to-slate-900 rounded-3xl p-6 border border-blue-800/50 relative overflow-hidden">
                <div className="flex gap-4 relative z-10">
                  <div className="p-3 bg-blue-500/20 rounded-xl h-fit">
                    <TrendingUp className="w-6 h-6 text-blue-400" />
                  </div>
                  <div>
                    <h4 className="font-bold text-white mb-2">Enterprise Access</h4>
                    <p className="text-sm text-blue-200 leading-relaxed mb-4">
                      Need higher API limits or SSO for your research lab?
                    </p>
                    <a href="#" className="inline-flex items-center gap-2 text-sm font-bold text-white hover:text-blue-200 transition-colors">
                      Contact Sales <ArrowUpRight className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default SubscriptionPage;