"use client"
import React, { useState, useEffect } from 'react';
import { 
  Brain, Target, Lightbulb, ChevronRight, Search, CheckCircle2, Loader2,
  Moon, Sun, TrendingUp, Users, DollarSign, BarChart3
} from 'lucide-react';

const analysisData = {
  scholarshipName: "The Horizon Innovation Merit Award",
  matchScore: 92,
  stats: { amount: "$10,000", acceptanceRate: "3.5%", deadline: "14 Days" },
  weights: [
    { label: "Community Impact", percent: 45, color: "text-indigo-600 dark:text-indigo-400", bg: "bg-indigo-600 dark:bg-indigo-500" },
    { label: "Resilience / Grit", percent: 30, color: "text-purple-600 dark:text-purple-400", bg: "bg-purple-600 dark:bg-purple-500" },
    { label: "Creativity", percent: 15, color: "text-sky-500 dark:text-sky-400", bg: "bg-sky-500 dark:bg-sky-400" },
    { label: "Academic GPA", percent: 10, color: "text-slate-400 dark:text-slate-500", bg: "bg-slate-400 dark:bg-slate-600" },
  ],
  hiddenPriorities: [
    { keyword: "Action over Theory", desc: "Values tangible results (numbers) over abstract goals." },
    { keyword: "Failure Analysis", desc: "Specifically looks for candidates who discuss a failure openly." },
    { keyword: "Local Focus", desc: "Prefers impact within your immediate city/town vs global." }
  ],
  toneAnalysis: { type: "Personal & Vulnerable", value: 75 },
  winnerInsight: "Analysis of previous 3 winners reveals a pattern: None had a 4.0 GPA, but all 3 founded a student organization."
};

const ScholarshipDecoder = () => {
  const [loading, setLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 1500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen transition-colors duration-500 font-sans bg-slate-100 dark:bg-slate-950 text-slate-900 dark:text-slate-100 selection:bg-indigo-500 selection:text-white">
        
        {loading ? (
          <div className="min-h-screen flex flex-col items-center justify-center space-y-6">
            <div className="relative">
              <div className="absolute inset-0 bg-indigo-500 blur-xl opacity-20 rounded-full animate-pulse"></div>
              <Loader2 className="w-16 h-16 animate-spin relative z-10 text-indigo-600 dark:text-indigo-400" />
            </div>
            <div className="text-center space-y-2">
              <h2 className="text-2xl font-bold animate-pulse text-slate-800 dark:text-white">
                Analyzing Scholarship Semantics...
              </h2>
              <p className="text-slate-500 dark:text-slate-400">
                Cross-referencing winner database...
              </p>
            </div>
          </div>
        ) : (
          <div className="pb-12">
            {/* Navbar */}
            <nav className="sticky top-0 z-50 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 px-6 py-4">
              <div className="max-w-7xl mx-auto flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <div className="bg-indigo-600 p-1.5 rounded-lg">
                    <Brain className="w-5 h-5 text-white" />
                  </div>
                  <span className="font-bold text-lg text-slate-800 dark:text-white tracking-tight">
                    Scholar<span className="text-indigo-600 dark:text-indigo-400">Match</span>.ai
                  </span>
                </div>
                <button 
                  onClick={() => setDarkMode(!darkMode)}
                  className="p-2 rounded-full bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 transition-all border border-slate-300 dark:border-slate-700"
                >
                  {darkMode ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5 text-slate-600" />}
                </button>
              </div>
            </nav>

            <main className="max-w-6xl mx-auto p-6 md:p-8">
              {/* Header Section */}
              <header className="mb-10 animate-fade-in-up">
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
                  <div>
                    <div className="flex items-center gap-2 mb-3">
                      <span className="px-3 py-1 rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-bold uppercase tracking-wider flex items-center gap-1 border border-green-200 dark:border-green-800">
                        <CheckCircle2 className="w-3 h-3" /> Analysis Complete
                      </span>
                      <span className="text-slate-400 dark:text-slate-500 text-sm">•</span>
                      <span className="text-slate-500 dark:text-slate-400 text-sm font-medium">ID: #882-XJ</span>
                    </div>
                    <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-3">
                      {analysisData.scholarshipName}
                    </h1>
                    
                    <div className="flex flex-wrap gap-4 md:gap-8 text-sm text-slate-600 dark:text-slate-400">
                      <div className="flex items-center gap-2">
                        <DollarSign className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                        <span>Award: <span className="font-semibold text-slate-900 dark:text-slate-200">{analysisData.stats.amount}</span></span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Users className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                        <span>Acceptance: <span className="font-semibold text-slate-900 dark:text-slate-200">{analysisData.stats.acceptanceRate}</span></span>
                      </div>
                      <div className="flex items-center gap-2">
                        <Target className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                        <span>Deadline: <span className="font-semibold text-slate-900 dark:text-slate-200">{analysisData.stats.deadline}</span></span>
                      </div>
                    </div>
                  </div>

                  {/* Match Score Badge */}
                  <div className="flex flex-col items-center justify-center bg-white dark:bg-slate-800 p-4 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 min-w-[120px]">
                    <div className="relative">
                       <svg className="w-16 h-16 transform -rotate-90">
                          <circle cx="32" cy="32" r="28" stroke="currentColor" strokeWidth="4" fill="transparent" className="text-slate-200 dark:text-slate-700" />
                          <circle cx="32" cy="32" r="28" stroke="currentColor" strokeWidth="4" fill="transparent" strokeDasharray="175.9" strokeDashoffset={175.9 - (175.9 * 92) / 100} className="text-indigo-600 dark:text-indigo-500" />
                       </svg>
                       <span className="absolute inset-0 flex items-center justify-center text-xl font-bold text-slate-900 dark:text-white">92</span>
                    </div>
                    <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-2 uppercase tracking-wide">Match Score</span>
                  </div>
                </div>
              </header>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                {/* LEFT COLUMN */}
                <div className="lg:col-span-5 space-y-6">
                  {/* Adaptive Weighting Card */}
                  <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-lg dark:shadow-2xl p-6 border border-slate-200 dark:border-slate-800 relative overflow-hidden group">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-sky-500"></div>
                    
                    <div className="flex justify-between items-center mb-8">
                      <h3 className="text-xl font-bold flex items-center gap-2 text-slate-900 dark:text-white">
                        <BarChart3 className="w-6 h-6 text-indigo-600 dark:text-indigo-500" /> 
                        Adaptive Weighting
                      </h3>
                    </div>

                    <div className="flex flex-col items-center justify-center mb-8 relative transition-transform duration-500 group-hover:scale-105">
                      <svg width="240" height="240" viewBox="0 0 100 100" className="-rotate-90 transform">
                        <circle cx="50" cy="50" r="40" fill="transparent" stroke="currentColor" strokeWidth="6" className="text-slate-200 dark:text-slate-800" />
                        <circle cx="50" cy="50" r="40" fill="transparent" stroke="#4f46e5" strokeWidth="8" 
                          strokeDasharray="251.2" strokeDashoffset="138" className="drop-shadow-lg filter" strokeLinecap="round"/> 
                        <circle cx="50" cy="50" r="40" fill="transparent" stroke="#9333ea" strokeWidth="8" 
                          strokeDasharray="251.2" strokeDashoffset="175" className="origin-center rotate-[162deg]" strokeLinecap="round"/> 
                        <circle cx="50" cy="50" r="40" fill="transparent" stroke="#0ea5e9" strokeWidth="8" 
                          strokeDasharray="251.2" strokeDashoffset="213" className="origin-center rotate-[270deg]" strokeLinecap="round"/> 
                      </svg>
                      
                      <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-5xl font-bold text-slate-900 dark:text-white tracking-tighter">100%</span>
                        <span className="text-xs text-slate-400 dark:text-slate-500 uppercase font-bold tracking-widest mt-1">Optimized</span>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {analysisData.weights.map((item, index) => (
                        <div key={index} className="group/item cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/50 p-2 rounded-lg transition-colors">
                          <div className="flex justify-between text-sm mb-2">
                            <span className="font-medium text-slate-700 dark:text-slate-300 flex items-center gap-2">
                              <span className={`w-2 h-2 rounded-full ${item.bg.split(' ')[0]}`}></span>
                              {item.label}
                            </span>
                            <span className={`font-bold ${item.color}`}>{item.percent}%</span>
                          </div>
                          <div className="w-full bg-slate-200 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
                            <div 
                              className={`h-2 rounded-full ${item.bg} transition-all duration-1000 ease-out`}
                              style={{ width: `${item.percent}%` }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                   {/* Tone Analysis */}
                   <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 border border-slate-200 dark:border-slate-800 shadow-lg">
                      <h4 className="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                        <TrendingUp className="w-4 h-4" /> Preferred Tone
                      </h4>
                      <div className="relative pt-6 pb-2">
                        <div className="h-2 bg-slate-200 dark:bg-slate-800 rounded-full w-full relative overflow-hidden">
                          <div className="absolute top-0 left-0 h-full w-full bg-gradient-to-r from-blue-300 via-purple-400 to-indigo-600 opacity-60 dark:opacity-30"></div>
                        </div>
                        
                        <div 
                          className="absolute top-2 w-1 h-10 bg-slate-800 dark:bg-white shadow-lg transform -translate-x-1/2 transition-all duration-1000"
                          style={{ left: `${analysisData.toneAnalysis.value}%` }}
                        >
                           <div className="absolute -top-7 left-1/2 transform -translate-x-1/2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 text-xs font-bold py-1 px-2 rounded whitespace-nowrap shadow-lg">
                              {analysisData.toneAnalysis.type}
                           </div>
                        </div>

                        <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400 mt-4 font-medium">
                          <span>Academic / Formal</span>
                          <span>Personal / Vulnerable</span>
                        </div>
                      </div>
                   </div>
                </div>

                {/* RIGHT COLUMN */}
                <div className="lg:col-span-7 space-y-6">
                  {/* Hidden Priorities */}
                  <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-lg p-8 border border-slate-200 dark:border-slate-800">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        <Search className="w-6 h-6 text-indigo-600 dark:text-indigo-500" /> 
                        Decoded Priorities
                      </h3>
                      <div className="text-xs font-medium px-2 py-1 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 border border-slate-200 dark:border-slate-700">
                        AI Confidence: High
                      </div>
                    </div>
                    
                    <div className="grid gap-4">
                      {analysisData.hiddenPriorities.map((priority, idx) => (
                        <div key={idx} className="flex items-start p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors border border-slate-200 dark:border-slate-700 group">
                          <div className="mt-1 text-indigo-600 dark:text-indigo-400 group-hover:text-indigo-700 dark:group-hover:text-indigo-300 transition-colors bg-white dark:bg-slate-800 p-1.5 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700">
                            <CheckCircle2 className="w-5 h-5" /> 
                          </div>
                          <div className="ml-4">
                            <h4 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wide mb-1">
                              {priority.keyword}
                            </h4>
                            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                              {priority.desc}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Winner Pattern Mining */}
                  <div className="relative rounded-3xl shadow-xl overflow-hidden group">
                    <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 to-violet-700 dark:from-indigo-900 dark:to-purple-900 transition-all duration-500"></div>
                    <div className="absolute top-0 right-0 -mt-8 -mr-8 w-40 h-40 bg-white opacity-10 rounded-full blur-3xl group-hover:opacity-20 transition-opacity duration-700"></div>
                    <div className="absolute bottom-0 left-0 -mb-8 -ml-8 w-32 h-32 bg-indigo-400 opacity-20 rounded-full blur-3xl"></div>

                    <div className="relative z-10 p-8 text-white">
                      <div className="flex items-start gap-5">
                        <div className="bg-white/20 backdrop-blur-md p-3.5 rounded-xl shadow-inner border border-white/10">
                          <Lightbulb className="w-7 h-7 text-yellow-300" />
                        </div>
                        <div>
                          <h3 className="text-xl font-bold mb-2 flex items-center gap-2 text-white">
                            Winner Pattern Insight
                            <span className="text-[10px] bg-indigo-500/50 px-2 py-0.5 rounded border border-indigo-400/30 uppercase tracking-wider text-white">RAG Analysis</span>
                          </h3>
                          <p className="text-indigo-100 text-base leading-relaxed font-medium">
                            {analysisData.winnerInsight}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Action Area */}
                  <div className="flex flex-col sm:flex-row gap-6 items-center justify-between bg-white dark:bg-slate-900 p-8 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
                    <div>
                      <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-1">Ready to draft?</h3>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        We've identified <span className="font-bold text-indigo-600 dark:text-indigo-400">3 stories</span> from your profile that match these criteria.
                      </p>
                    </div>
                    <button className="w-full sm:w-auto px-8 py-4 bg-slate-900 dark:bg-indigo-600 hover:bg-slate-700 dark:hover:bg-indigo-500 text-white font-bold rounded-2xl flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-indigo-500/25 active:scale-95">
                      Generate Strategy
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            </main>
          </div>
        )}

        <style>{`
          @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .animate-fade-in-up {
            animation: fadeInUp 0.8s ease-out forwards;
          }
        `}</style>
      </div>
    </div>
  );
};

export default ScholarshipDecoder;