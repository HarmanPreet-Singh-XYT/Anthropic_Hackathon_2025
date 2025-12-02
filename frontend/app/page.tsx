"use client"
import React, { useState, useEffect } from 'react';
import {
  Moon, Sun, Brain, PenTool, Target, Zap,
  CheckCircle, ArrowRight, Github, Play,
  UploadCloud, FileText, Sparkles, User,
  BarChart3, RefreshCw, GraduationCap,
  ShieldCheck,
  Check
} from 'lucide-react';
import { useTheme } from '@/context/ThemeContext';
import { useAuthClient } from '@/hooks/useAuthClient';
import { triggerSignIn } from '@/app/auth-actions';
import { Navigation } from '@/components/Navigation';

const App = () => {
  const [activeTab, setActiveTab] = useState('input'); // For the Interactive Demo
  const { darkMode, toggleDarkMode } = useTheme();
  const { user, isLoading } = useAuthClient();

  const handleTryItOut = (e: React.MouseEvent) => {
    e.preventDefault();
    if (user) {
      window.location.href = '/dashboard';
    } else {
      // Require sign-in before accessing /start
      triggerSignIn();
    }
  };

  const handleSignIn = () => {
    triggerSignIn();
  };
  // Handle Dark Mode
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const toggleTheme = () => toggleDarkMode();

  return (
    <div className="min-h-screen bg-black text-white font-sans selection:bg-blue-500 selection:text-white overflow-x-hidden">

      {/* STAR PARTICLES BACKGROUND */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        {/* Star particles */}
        {[...Array(50)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-white rounded-full animate-pulse"
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              opacity: Math.random() * 0.5 + 0.1,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${Math.random() * 3 + 2}s`
            }}
          />
        ))}
        {/* Subtle glow effects */}
        <div className="absolute left-1/4 top-0 -z-10 h-[400px] w-[400px] rounded-full bg-white/5 blur-[120px]"></div>
        <div className="absolute right-1/4 bottom-0 -z-10 h-[400px] w-[400px] rounded-full bg-white/5 blur-[120px]"></div>
      </div>

      {/* Navigation */}
      <Navigation variant="landing" />

      {/* HERO SECTION */}
      <section className="relative pt-32 pb-24 lg:pt-48 lg:pb-32 min-h-screen flex items-center">
        <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col items-center text-center">

          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 backdrop-blur-md border border-white/10 text-sm font-medium mb-12 hover:bg-white/10 transition-all">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white/50 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-white/70"></span>
            </span>
            <span className="text-white/90 font-semibold">Agentiiv Hackathon 2025</span>
            <span className="text-white/30">|</span>
            <span className="text-white/60">Team</span>
          </div>

          {/* Headline */}
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-black tracking-tight mb-8 leading-[1.05]">
            Don't just apply.<br />
            <span className="text-white italic">
              Command the Room.
            </span>
          </h1>

          <p className="mt-6 max-w-2xl mx-auto text-lg md:text-xl text-white/70 leading-relaxed">
            The first AI that decodes scholarship "personalities." We adapt your story to match the hidden values of any committee, instantly.
          </p>

          {/* CTA Buttons */}
          <div className="mt-12 flex flex-col sm:flex-row gap-4 w-full justify-center">
            <button
              onClick={handleTryItOut}
              className="group relative flex items-center justify-center gap-3 bg-white hover:bg-white/90 text-black px-8 py-4 rounded-full font-semibold text-base shadow-lg shadow-white/10 transition-all hover:shadow-white/20 hover:shadow-xl"
            >
              <Play className="w-5 h-5 fill-current" /> {user ? 'Launch Dashboard' : 'Launch Live Demo'}
            </button>
            <a href='https://github.com/HarmanPreet-Singh-XYT/Anthropic_Hackathon_2025' className="flex items-center justify-center gap-2 bg-white/5 backdrop-blur-sm border border-white/20 hover:bg-white/10 hover:border-white/30 text-white px-8 py-4 rounded-full font-semibold text-base transition-all">
              <Github className="w-5 h-5" /> View Repo
            </a>
          </div>

          {/* INTERACTIVE MOCKUP COMPONENT */}
          <div className="mt-24 w-full max-w-5xl mx-auto">
            <div className="relative rounded-3xl border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl shadow-black/50 overflow-hidden">
              {/* Fake Browser Header */}
              <div className="h-12 border-b border-white/5 bg-black/60 flex items-center px-6 gap-3">
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
                </div>
                <div className="ml-4 px-4 py-1.5 bg-white/5 rounded-lg text-xs text-white/50 flex items-center gap-2 flex-1 max-w-sm">
                  <Target className="w-3 h-3" /> scholarmatch.ai/engine/active
                </div>
              </div>

              {/* Interactive Area */}
              <div className="grid md:grid-cols-12 min-h-[500px]">

                {/* Sidebar Navigation */}
                <div className="md:col-span-3 border-r border-white/5 p-6 bg-black/20">
                  <div className="space-y-2">
                    <button
                      onClick={() => setActiveTab('input')}
                      className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3 transition-all ${activeTab === 'input' ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-lg shadow-blue-500/20' : 'hover:bg-white/5 text-white/50 hover:text-white/80'}`}
                    >
                      <User className="w-4 h-4" /> Profile & Link
                    </button>
                    <button
                      onClick={() => setActiveTab('analysis')}
                      className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3 transition-all ${activeTab === 'analysis' ? 'bg-purple-600/20 text-purple-400 border border-purple-500/30 shadow-lg shadow-purple-500/20' : 'hover:bg-white/5 text-white/50 hover:text-white/80'}`}
                    >
                      <Brain className="w-4 h-4" /> AI Analysis
                    </button>
                    <button
                      onClick={() => setActiveTab('draft')}
                      className={`w-full text-left px-4 py-3 rounded-xl flex items-center gap-3 transition-all ${activeTab === 'draft' ? 'bg-green-600/20 text-green-400 border border-green-500/30 shadow-lg shadow-green-500/20' : 'hover:bg-white/5 text-white/50 hover:text-white/80'}`}
                    >
                      <FileText className="w-4 h-4" /> Final Draft
                    </button>
                  </div>

                  <div className="mt-8 p-4 bg-white/5 rounded-xl border border-white/10">
                    <p className="text-xs text-blue-400 font-semibold mb-2">LIVE STATUS</p>
                    <div className="flex items-center gap-2 text-xs text-white/70">
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-green-400"></span>
                      </span>
                      System Ready
                    </div>
                  </div>
                </div>

                {/* Main Content Area - Dynamic based on Tab */}
                <div className="md:col-span-9 p-8 bg-black/30 relative">

                  {activeTab === 'input' && (
                    <div className="space-y-6">
                      <div className="flex items-center justify-between">
                        <h3 className="text-xl font-bold text-white">Scholarship Target</h3>
                        <span className="text-xs bg-white/5 px-3 py-1 rounded-full text-white/50 border border-white/10">Step 1 of 3</span>
                      </div>

                      <div className="space-y-4">
                        <div className="border border-dashed border-white/20 rounded-xl p-8 flex flex-col items-center justify-center text-center hover:bg-white/5 hover:border-white/30 transition-all cursor-pointer group">
                          <div className="w-12 h-12 bg-blue-600/20 rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform border border-blue-500/30">
                            <UploadCloud className="w-6 h-6 text-blue-400" />
                          </div>
                          <p className="font-medium text-white">Upload Student Profile (PDF/DOCX)</p>
                          <p className="text-sm text-white/50">Drag and drop or click to browse</p>
                        </div>

                        <div>
                          <label className="block text-sm font-medium mb-2 text-white/70">Scholarship URL</label>
                          <div className="flex gap-2">
                            <input type="text" value="https://foundation.org/grants/innovation-2025" readOnly className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white/50 text-sm" />
                            <button onClick={() => setActiveTab('analysis')} className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-all">Scan</button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {activeTab === 'analysis' && (
                    <div className="space-y-6">
                      <div className="flex items-center justify-between">
                        <h3 className="text-xl font-bold text-white">Decoding Priorities</h3>
                        <RefreshCw className="w-4 h-4 animate-spin text-purple-400" />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="col-span-2 p-4 bg-white/5 rounded-xl border border-white/10">
                          <div className="flex justify-between text-sm mb-2">
                            <span className="font-semibold text-white">Detected Theme: Innovation & Risk</span>
                            <span className="text-green-400 font-mono font-semibold">98% Match</span>
                          </div>
                          <div className="w-full bg-white/10 rounded-full h-2">
                            <div className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full w-[98%] shadow-lg shadow-blue-500/30"></div>
                          </div>
                        </div>

                        <div className="p-4 rounded-xl border border-red-500/30 bg-red-600/10">
                          <p className="text-xs text-red-400 font-semibold uppercase mb-1">De-Emphasize</p>
                          <p className="text-sm font-medium text-white/90">Standard GPA & Class Attendance</p>
                        </div>
                        <div className="p-4 rounded-xl border border-green-500/30 bg-green-600/10">
                          <p className="text-xs text-green-400 font-semibold uppercase mb-1">Hyper-Focus</p>
                          <p className="text-sm font-medium text-white/90">"Robotics Club Failure & Pivot"</p>
                        </div>
                      </div>

                      <div className="flex justify-end mt-4">
                        <button onClick={() => setActiveTab('draft')} className="bg-purple-600 hover:bg-purple-500 text-white px-6 py-2 rounded-lg text-sm font-semibold shadow-lg shadow-purple-500/30 transition-all">Generate Draft &rarr;</button>
                      </div>
                    </div>
                  )}

                  {activeTab === 'draft' && (
                    <div className="h-full flex flex-col">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl font-bold flex items-center gap-2 text-white">
                          <Sparkles className="w-5 h-5 text-yellow-400" /> Tailored Essay
                        </h3>
                        <div className="flex gap-2">
                          <span className="px-3 py-1 bg-green-600/20 border border-green-500/30 text-green-400 text-xs font-semibold rounded-full">Optimized</span>
                        </div>
                      </div>

                      <div className="flex-1 bg-white/5 border border-white/10 rounded-xl p-6 font-serif leading-relaxed text-white/90 text-sm overflow-y-auto max-h-[300px]">
                        <p className="mb-4">
                          <span className="bg-yellow-500/20 border-b-2 border-yellow-500/50 text-white px-1">Innovation isn't about the awards on a shelf; it's about the prototypes in the trash bin.</span> That is a lesson I learned not in the classroom, but at 2 AM in the robotics lab...
                        </p>
                        <p>
                          While my transcript shows a 3.8 GPA, it doesn't capture the three months I spent debugging a LIDAR sensor for our community drone project. This aligns with the <span className="font-bold text-blue-400">Future Innovators Foundation's</span> mission to support persistence over perfection...
                        </p>
                        <div className="h-4 w-3/4 bg-white/10 rounded animate-pulse mt-4"></div>
                        <div className="h-4 w-1/2 bg-white/10 rounded animate-pulse mt-2"></div>
                      </div>
                    </div>
                  )}

                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SOCIAL PROOF MARQUEE */}
      <section className="py-16 border-y border-white/5 bg-black overflow-hidden">
        <p className="text-center text-xs font-semibold uppercase tracking-widest text-white/40 mb-8">Trusted by students at</p>
        <div className="flex gap-16 whitespace-nowrap opacity-50 hover:opacity-70 transition-opacity duration-500 justify-center">
          {['Stanford University', 'MIT Media Lab', 'Rhodes Trust', 'Gates Foundation', 'National Science Foundation', 'Fulbright Program'].map((org, i) => (
            <div key={i} className="flex items-center gap-2 text-lg font-semibold text-white/60">
              <GraduationCap className="w-5 h-5" /> {org}
            </div>
          ))}
        </div>
      </section>

      {/* REFINED: HOW IT WORKS (The Processing Pipeline) */}
      <section id="how-it-works" className="py-32 bg-black relative overflow-hidden">

        {/* Background Elements */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-px h-full bg-gradient-to-b from-transparent via-blue-500/20 to-transparent hidden md:block"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-24">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">From Resume to <span className="text-blue-400">Winner</span></h2>
            <p className="text-white/60 text-lg max-w-2xl mx-auto">
              A 3-stage RAG pipeline that transforms raw data into a hyper-targeted narrative.
            </p>
          </div>

          <div className="space-y-12 relative">

            {/* STAGE 1: INGESTION */}
            <div className="flex flex-col md:flex-row items-center gap-8 relative">
              {/* Number/Icon Node */}
              <div className="md:w-1/2 flex justify-end md:pr-12 order-2 md:order-1">
                <div className="bg-white/5 backdrop-blur-sm p-6 rounded-2xl border border-white/10 w-full max-w-md relative group hover:bg-white/10 hover:border-white/20 transition-all duration-300">
                  <div className="absolute top-0 right-0 bg-blue-600/20 text-blue-400 text-xs font-semibold px-3 py-1 rounded-bl-lg rounded-tr-xl border-l border-b border-blue-500/30">STEP 01</div>
                  <div className="flex items-center gap-4 mb-4">
                    <div className="p-3 bg-blue-600/20 rounded-lg border border-blue-500/30">
                      <UploadCloud className="w-6 h-6 text-blue-400" />
                    </div>
                    <h3 className="text-xl font-bold text-white">Dual-Source Ingestion</h3>
                  </div>
                  <p className="text-white/70 text-sm mb-4 leading-relaxed">
                    We ingest your static Student Profile (PDF/CV) and simultaneously scrape the live Scholarship URL.
                  </p>
                  {/* Micro-tasks */}
                  <div className="bg-black/40 rounded-lg p-3 space-y-2 border border-white/5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-white/60 flex items-center gap-2"><CheckCircle className="w-3 h-3 text-green-400" /> PDF Parsing</span>
                      <span className="text-white/40 font-mono">DONE</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-white/60 flex items-center gap-2"><CheckCircle className="w-3 h-3 text-green-400" /> URL Scraping</span>
                      <span className="text-white/40 font-mono">DONE</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Center Dot */}
              <div className="absolute left-1/2 -translate-x-1/2 w-4 h-4 bg-blue-500 rounded-full border-4 border-black z-20 hidden md:block shadow-[0_0_20px_rgba(59,130,246,0.6)]"></div>

              <div className="md:w-1/2 order-1 md:order-2 md:pl-12 hidden md:block">
                <span className="text-6xl font-black text-white/5 select-none">01</span>
              </div>
            </div>

            {/* STAGE 2: PROCESSING */}
            <div className="flex flex-col md:flex-row items-center gap-8 relative">
              <div className="md:w-1/2 flex justify-end md:pr-12 hidden md:block">
                <span className="text-6xl font-black text-white/5 select-none">02</span>
              </div>

              {/* Center Dot */}
              <div className="absolute left-1/2 -translate-x-1/2 w-4 h-4 bg-purple-500 rounded-full border-4 border-black z-20 hidden md:block shadow-[0_0_20px_rgba(168,85,247,0.6)]"></div>

              {/* Card */}
              <div className="md:w-1/2 md:pl-12">
                <div className="bg-white/5 backdrop-blur-sm p-6 rounded-2xl border border-purple-500/30 w-full max-w-md relative group hover:bg-white/10 hover:border-purple-500/50 transition-all duration-300">
                  <div className="absolute top-0 right-0 bg-purple-600/20 text-purple-400 text-xs font-semibold px-3 py-1 rounded-bl-lg rounded-tr-xl border-l border-b border-purple-500/30">STEP 02</div>
                  <div className="flex items-center gap-4 mb-4">
                    <div className="p-3 bg-purple-600/20 rounded-lg border border-purple-500/30">
                      <Brain className="w-6 h-6 text-purple-400" />
                    </div>
                    <h3 className="text-xl font-bold text-white">Semantic Mapping</h3>
                  </div>
                  <p className="text-white/70 text-sm mb-4 leading-relaxed">
                    Our "Adaptive Weighting" engine compares your history against the scholarship's hidden values using vector embeddings.
                  </p>

                  {/* Visualization of processing */}
                  <div className="flex gap-1 h-1.5 w-full mb-2">
                    <div className="h-full w-1/3 bg-purple-500 rounded-full animate-pulse shadow-lg shadow-purple-500/30"></div>
                    <div className="h-full w-1/3 bg-purple-400 rounded-full animate-pulse delay-75"></div>
                    <div className="h-full w-1/3 bg-purple-300 rounded-full animate-pulse delay-150"></div>
                  </div>
                  <p className="text-xs text-purple-400 font-mono text-center">Identifying "Win Themes"...</p>
                </div>
              </div>
            </div>

            {/* STAGE 3: GENERATION */}
            <div className="flex flex-col md:flex-row items-center gap-8 relative">
              <div className="md:w-1/2 flex justify-end md:pr-12 order-2 md:order-1">
                <div className="bg-white/5 backdrop-blur-sm p-6 rounded-2xl border border-white/10 w-full max-w-md relative group hover:bg-white/10 hover:border-white/20 transition-all duration-300">
                  <div className="absolute top-0 right-0 bg-green-600/20 text-green-400 text-xs font-semibold px-3 py-1 rounded-bl-lg rounded-tr-xl border-l border-b border-green-500/30">STEP 03</div>
                  <div className="flex items-center gap-4 mb-4">
                    <div className="p-3 bg-green-600/20 rounded-lg border border-green-500/30">
                      <PenTool className="w-6 h-6 text-green-400" />
                    </div>
                    <h3 className="text-xl font-bold text-white">Strategic Drafting</h3>
                  </div>
                  <p className="text-white/70 text-sm mb-4 leading-relaxed">
                    The LLM generates a unique essay that emphasizes the traits this specific committee cares about most.
                  </p>

                  {/* Mock File Output */}
                  <div className="flex items-center gap-3 bg-black/40 p-3 rounded-lg border border-white/5">
                    <FileText className="w-8 h-8 text-white/40" />
                    <div>
                      <p className="text-sm font-semibold text-white">Final_Draft_v1.docx</p>
                      <div className="flex items-center gap-2">
                        <span className="text-[10px] text-white/50">Match Score: 98%</span>
                        <span className="h-1.5 w-1.5 rounded-full bg-green-400 shadow-lg shadow-green-400/50"></span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Center Dot */}
              <div className="absolute left-1/2 -translate-x-1/2 w-4 h-4 bg-green-500 rounded-full border-4 border-black z-20 hidden md:block shadow-[0_0_20px_rgba(34,197,94,0.6)]"></div>

              <div className="md:w-1/2 order-1 md:order-2 md:pl-12 hidden md:block">
                <span className="text-6xl font-black text-white/5 select-none">03</span>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* FEATURES SECTION */}
      <section id="features" className="py-32 bg-black border-t border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white">Everything You Need to Win</h2>
            <p className="text-white/60 text-lg max-w-2xl mx-auto">
              Advanced RAG technology combined with behavioral psychology to build the ultimate scholarship copilot.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

            {/* Feature 1: Adaptive Scoring */}
            <div className="md:col-span-2 bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                <Target className="w-48 h-48 text-blue-400" />
              </div>
              <div className="relative z-10">
                <div className="w-12 h-12 bg-blue-600/20 rounded-xl flex items-center justify-center mb-4 border border-blue-500/30">
                  <Target className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-2xl font-bold mb-3 text-white">Adaptive Scoring Engine</h3>
                <p className="text-white/70 max-w-md leading-relaxed">
                  System dynamically re-weights your profile based on scholarship type. Merit scholarships prioritize grades, service scholarships prioritize volunteering.
                </p>
              </div>
            </div>

            {/* Feature 2: Tone Matcher */}
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-purple-500/30 hover:bg-white/10 hover:border-purple-500/50 transition-all">
              <div className="w-10 h-10 bg-purple-600/20 rounded-lg flex items-center justify-center mb-4 border border-purple-500/30">
                <Sparkles className="w-5 h-5 text-purple-400" />
              </div>
              <h3 className="text-lg font-bold mb-2 text-white">Tone Matcher</h3>
              <p className="text-white/70 text-sm">
                Analyzes donor language to replicate their specific vocabulary and emotional resonance.
              </p>
            </div>

            {/* Feature 3: Winner Mining */}
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all">
              <div className="w-10 h-10 bg-green-600/20 rounded-lg flex items-center justify-center mb-4 border border-green-500/30">
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>
              <h3 className="text-lg font-bold mb-2 text-white">Winner Mining</h3>
              <p className="text-white/70 text-sm">
                Analyzed 10,000+ past winner bios to find commonalities in successful applicants.
              </p>
            </div>

            {/* Feature 4: Privacy */}
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all">
              <div className="w-10 h-10 bg-orange-600/20 rounded-lg flex items-center justify-center mb-4 border border-orange-500/30">
                <ShieldCheck className="w-5 h-5 text-orange-400" />
              </div>
              <h3 className="text-lg font-bold mb-2 text-white">Private by Design</h3>
              <p className="text-white/70 text-sm">
                Stories processed ephemerally. We never train models on your private data.
              </p>
            </div>

            {/* Feature 5: One-Click Tailoring */}
            <div className="md:col-span-2 bg-gradient-to-r from-blue-600/20 to-indigo-600/20 backdrop-blur-sm rounded-2xl p-8 border border-blue-500/30 hover:border-blue-500/50 transition-all relative overflow-hidden">
              <div className="absolute right-0 bottom-0 opacity-10">
                <PenTool className="w-48 h-48 text-blue-400" />
              </div>
              <div className="relative z-10 max-w-lg">
                <h3 className="text-2xl font-bold mb-3 text-white">One-Click Tailoring</h3>
                <p className="text-white/70 mb-6">
                  Upload a base essay once. We rewrite it instantly for 50 different scholarships, changing the angle every time.
                </p>
              </div>
            </div>

            {/* Feature 6: Explainable AI */}
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 hover:bg-white/10 hover:border-white/20 transition-all relative">
              <div className="w-10 h-10 bg-yellow-600/20 rounded-lg flex items-center justify-center mb-4 border border-yellow-500/30">
                <Zap className="w-5 h-5 text-yellow-400" />
              </div>
              <h3 className="text-lg font-bold mb-2 text-white">Explainable AI</h3>
              <p className="text-white/70 text-sm">
                Understand why each word was chosen. See the strategy behind every edit.
              </p>
            </div>

          </div>
        </div>
      </section>

      {/* NEW: REAL WORLD EXAMPLES SECTION */}
      <section className="py-24 bg-white dark:bg-slate-900 border-y border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <span className="text-blue-600 dark:text-blue-400 font-bold tracking-wider uppercase text-sm">The Chameleon Effect</span>
            <h2 className="text-3xl md:text-5xl font-bold mt-2">One Story. Two Winning Angles.</h2>
            <p className="text-slate-600 dark:text-slate-400 mt-4 max-w-2xl mx-auto">
              See how our AI takes the same student experience (e.g., "Running a D&D Club") and radically reframes it based on who is reading.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">

            {/* Case A: Leadership Focus */}
            <div className="group bg-slate-50 dark:bg-slate-950 rounded-2xl p-8 border border-slate-200 dark:border-slate-800 hover:border-blue-500 dark:hover:border-blue-500 transition-colors relative overflow-hidden">
              <div className="absolute top-0 right-0 bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-bl-lg">Target: Community Leadership</div>

              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <h4 className="font-bold text-lg">The "Leader" Angle</h4>
                  <p className="text-xs text-slate-500">Emphasizing: Organization & Empathy</p>
                </div>
              </div>

              <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 font-serif text-slate-600 dark:text-slate-300 italic relative">
                <span className="absolute -top-3 -left-2 text-4xl text-slate-200 dark:text-slate-700">"</span>
                "Managing a weekly D&D group taught me <span className="bg-blue-100 dark:bg-blue-900/50 font-bold text-blue-700 dark:text-blue-300 px-1 rounded">conflict resolution</span> and the art of <span className="bg-blue-100 dark:bg-blue-900/50 font-bold text-blue-700 dark:text-blue-300 px-1 rounded">facilitating diverse groups</span> towards a shared goal..."
              </div>

              <div className="mt-4 flex gap-2">
                <span className="text-xs border border-blue-200 dark:border-blue-900 text-blue-600 dark:text-blue-400 px-2 py-1 rounded-full">Soft Skills</span>
                <span className="text-xs border border-blue-200 dark:border-blue-900 text-blue-600 dark:text-blue-400 px-2 py-1 rounded-full">Community</span>
              </div>
            </div>

            {/* Case B: Creative Focus */}
            <div className="group bg-slate-50 dark:bg-slate-950 rounded-2xl p-8 border border-slate-200 dark:border-slate-800 hover:border-purple-500 dark:hover:border-purple-500 transition-colors relative overflow-hidden">
              <div className="absolute top-0 right-0 bg-purple-600 text-white text-xs font-bold px-3 py-1 rounded-bl-lg">Target: Arts & Innovation</div>

              <div className="flex items-center gap-4 mb-6">
                <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center">
                  <PenTool className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <h4 className="font-bold text-lg">The "Creator" Angle</h4>
                  <p className="text-xs text-slate-500">Emphasizing: World-building & Writing</p>
                </div>
              </div>

              <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 font-serif text-slate-600 dark:text-slate-300 italic relative">
                <span className="absolute -top-3 -left-2 text-4xl text-slate-200 dark:text-slate-700">"</span>
                "As a Dungeon Master, I practiced <span className="bg-purple-100 dark:bg-purple-900/50 font-bold text-purple-700 dark:text-purple-300 px-1 rounded">narrative design</span> and <span className="bg-purple-100 dark:bg-purple-900/50 font-bold text-purple-700 dark:text-purple-300 px-1 rounded">improvisational storytelling</span>, crafting complex worlds that engaged players for hours..."
              </div>

              <div className="mt-4 flex gap-2">
                <span className="text-xs border border-purple-200 dark:border-purple-900 text-purple-600 dark:text-purple-400 px-2 py-1 rounded-full">Creativity</span>
                <span className="text-xs border border-purple-200 dark:border-purple-900 text-purple-600 dark:text-purple-400 px-2 py-1 rounded-full">Writing</span>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* NEW: TECH STACK / UNDER THE HOOD */}
      <section className="py-24 bg-slate-900 text-white relative overflow-hidden">
        {/* Background circuit pattern */}
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#4b5563_1px,transparent_1px)] [background-size:16px_16px]"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-6">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Built with Modern AI Architecture</h2>
              <p className="text-slate-400 max-w-xl">
                We utilize a RAG (Retrieval-Augmented Generation) pipeline to ensure every essay is grounded in the real requirements of the scholarship.
              </p>
            </div>
            <div className="flex gap-2">
              <span className="px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs font-mono text-green-400">Anthropic Claude 3.5</span>
              <span className="px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs font-mono text-blue-400">Vector DB</span>
            </div>
          </div>

          {/* Tech Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">

            {/* Step 1: Ingest */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 p-6 rounded-xl">
              <div className="text-blue-500 mb-4 font-mono text-xs font-bold tracking-widest">01 INGESTION</div>
              <h3 className="font-bold text-lg mb-2">Web Scraper</h3>
              <p className="text-sm text-slate-400">
                Custom Python scraper extracts scholarship descriptions, "About Us" pages, and past winner bios.
              </p>
            </div>

            {/* Step 2: Vectorize */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 p-6 rounded-xl">
              <div className="text-purple-500 mb-4 font-mono text-xs font-bold tracking-widest">02 EMBEDDINGS</div>
              <h3 className="font-bold text-lg mb-2">Semantic Search</h3>
              <p className="text-sm text-slate-400">
                Text is converted into vector embeddings to find semantic matches between student stories and donor values.
              </p>
            </div>

            {/* Step 3: LLM Logic */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 p-6 rounded-xl relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="text-green-500 mb-4 font-mono text-xs font-bold tracking-widest relative">03 REASONING</div>
              <h3 className="font-bold text-lg mb-2 relative">Adaptive Weighting</h3>
              <p className="text-sm text-slate-400 relative">
                Claude 3.5 Sonnet analyzes the data to assign dynamic percentages to specific student traits.
              </p>
            </div>

            {/* Step 4: Output */}
            <div className="bg-slate-800/50 backdrop-blur border border-slate-700 p-6 rounded-xl">
              <div className="text-yellow-500 mb-4 font-mono text-xs font-bold tracking-widest">04 GENERATION</div>
              <h3 className="font-bold text-lg mb-2">Refined Drafting</h3>
              <p className="text-sm text-slate-400">
                Final output is generated using specific tone-matching prompts to mimic the organization's voice.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* IMPACT STATS */}
      <section className="py-20 bg-white/5 border-y border-white/10 relative overflow-hidden">
        {/* Decorative Circles */}
        <div className="absolute top-0 left-0 w-64 h-64 bg-white opacity-5 rounded-full -translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-white opacity-5 rounded-full translate-x-1/2 translate-y-1/2"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center text-white">
            <div className="p-6">
              <div className="text-5xl md:text-6xl font-black mb-2 tracking-tight">3.5<span className="text-2xl opacity-80">hrs</span></div>
              <p className="font-medium text-white/70 text-lg">Saved per application</p>
            </div>
            <div className="p-6 border-y md:border-y-0 md:border-x border-white/20">
              <div className="text-5xl md:text-6xl font-black mb-2 tracking-tight">85<span className="text-2xl opacity-80">%</span></div>
              <p className="font-medium text-white/70 text-lg">Better tone matching score</p>
            </div>
            <div className="p-6">
              <div className="text-5xl md:text-6xl font-black mb-2 tracking-tight">24<span className="text-2xl opacity-80">/7</span></div>
              <p className="font-medium text-white/70 text-lg">Personalized guidance</p>
            </div>
          </div>
        </div>
      </section>

      {/* NEW: ETHICS & SAFETY */}
      <section className="py-24 bg-slate-50 dark:bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col lg:flex-row items-center gap-16">

            {/* Left Content */}
            <div className="lg:w-1/2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-bold uppercase tracking-wide mb-6">
                <ShieldCheck className="w-4 h-4" /> Ethical AI Standard
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">Your Voice. Just Louder.</h2>
              <p className="text-lg text-slate-600 dark:text-slate-400 mb-6 leading-relaxed">
                ScholarMatch isn't a "cheat code"—it's a translation layer. We don't invent stories for you; we help you articulate your own experiences in a way that committees understand.
              </p>

              <div className="space-y-4">
                <div className="flex gap-4">
                  <div className="mt-1 w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/50 flex items-center justify-center shrink-0">
                    <Check className="w-4 h-4 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <h4 className="font-bold">Anti-Plagiarism Checks</h4>
                    <p className="text-sm text-slate-500">Every draft is scanned to ensure originality before you ever see it.</p>
                  </div>
                </div>
                <div className="flex gap-4">
                  <div className="mt-1 w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/50 flex items-center justify-center shrink-0">
                    <Check className="w-4 h-4 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <h4 className="font-bold">Human-in-the-Loop</h4>
                    <p className="text-sm text-slate-500">We encourage students to edit the final output. The AI provides the structure; you provide the soul.</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Visual */}
            <div className="lg:w-1/2 relative">
              <div className="absolute inset-0 bg-gradient-to-tr from-green-500 to-blue-500 rounded-2xl blur-2xl opacity-20"></div>
              <div className="relative bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl p-8 shadow-2xl">
                <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-100 dark:border-slate-800">
                  <span className="font-bold text-slate-500">Authenticity Score</span>
                  <span className="text-green-500 font-bold">99.8%</span>
                </div>
                <div className="space-y-2">
                  <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full w-[80%] bg-slate-300 dark:bg-slate-700 rounded-full"></div>
                  </div>
                  <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full w-[60%] bg-slate-300 dark:bg-slate-700 rounded-full"></div>
                  </div>
                  <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full w-[90%] bg-slate-300 dark:bg-slate-700 rounded-full"></div>
                  </div>

                  {/* Floating Badge */}
                  <div className="absolute -bottom-6 -right-6 bg-white dark:bg-slate-800 p-4 rounded-xl shadow-lg border border-slate-100 dark:border-slate-700 flex items-center gap-3 animate-bounce">
                    <ShieldCheck className="w-8 h-8 text-green-500" />
                    <div>
                      <p className="text-xs text-slate-500 font-bold uppercase">AI Integrity</p>
                      <p className="font-bold text-slate-900 dark:text-white">Verified</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* NEW: X-RAY VISION (Replaces Roadmap) */}
      <section className="py-24 bg-slate-50 dark:bg-slate-900/50 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <span className="text-purple-600 dark:text-purple-400 font-bold tracking-wider uppercase text-sm">Pattern Recognition Engine</span>
            <h2 className="text-3xl md:text-5xl font-bold mt-2">We See What Humans Miss</h2>
            <p className="text-slate-600 dark:text-slate-400 mt-4 max-w-2xl mx-auto">
              Scholarship descriptions are vague. Our AI scans years of winner data to reveal the <strong>hidden weighting criteria</strong> that actually determines the winner.
            </p>
          </div>

          <div className="relative">
            {/* Central Connector Line */}
            <div className="absolute left-1/2 top-0 bottom-0 w-px bg-slate-300 dark:bg-slate-700 hidden md:block"></div>
            <div className="absolute left-1/2 top-1/2 -translate-y-1/2 -translate-x-1/2 z-10 hidden md:flex w-12 h-12 bg-white dark:bg-slate-900 rounded-full border-4 border-purple-500 items-center justify-center">
              <ArrowRight className="w-6 h-6 text-purple-500" />
            </div>

            <div className="grid md:grid-cols-2 gap-12 md:gap-24 items-center">

              {/* Left Side: What the Student Sees (The Problem) */}
              <div className="relative group opacity-70 hover:opacity-100 transition-opacity blur-[0.5px] hover:blur-0 duration-500">
                <div className="absolute -top-10 left-0 text-xs font-bold uppercase tracking-widest text-slate-400">Human View</div>
                <div className="bg-white dark:bg-slate-950 p-8 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm relative">
                  {/* Ribbon */}
                  <div className="absolute top-0 right-0 bg-slate-200 dark:bg-slate-800 text-slate-500 text-xs px-3 py-1 rounded-bl-lg font-bold">
                    Generic Description
                  </div>

                  <h3 className="font-serif text-xl font-bold mb-4 text-slate-800 dark:text-slate-200">The 2025 Future Leader Grant</h3>
                  <div className="space-y-3 text-sm text-slate-500 font-serif leading-relaxed">
                    <p>We are looking for <span className="bg-slate-200 dark:bg-slate-800">exceptional students</span> who demonstrate <span className="bg-slate-200 dark:bg-slate-800">strong leadership</span> and a commitment to <span className="bg-slate-200 dark:bg-slate-800">academic excellence</span>.</p>
                    <p>Applicants should submit a 500-word essay describing their goals and how this scholarship will help them achieve their dreams.</p>
                  </div>

                  <div className="mt-6 flex gap-2">
                    <span className="px-3 py-1 bg-slate-100 dark:bg-slate-800 rounded-full text-xs text-slate-500">Requirements: GPA 3.5+</span>
                    <span className="px-3 py-1 bg-slate-100 dark:bg-slate-800 rounded-full text-xs text-slate-500">Essay Required</span>
                  </div>
                </div>
              </div>

              {/* Right Side: What AI Sees (The Solution) */}
              <div className="relative">
                <div className="absolute -top-10 left-0 text-xs font-bold uppercase tracking-widest text-purple-500">AI X-Ray View</div>
                <div className="bg-white dark:bg-slate-950 p-8 rounded-2xl border-2 border-purple-500 shadow-2xl shadow-purple-500/20 relative overflow-hidden">

                  {/* Scanning Line Animation */}
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent opacity-50 animate-pulse"></div>

                  <div className="absolute top-0 right-0 bg-purple-600 text-white text-xs px-3 py-1 rounded-bl-lg font-bold flex items-center gap-1">
                    <Sparkles className="w-3 h-3" /> Insights Detected
                  </div>

                  <h3 className="font-sans text-xl font-bold mb-6 text-slate-900 dark:text-white flex items-center gap-2">
                    Hidden Scoring Weights
                  </h3>

                  <div className="space-y-5">
                    {/* Bar 1 */}
                    <div>
                      <div className="flex justify-between text-xs font-bold mb-1">
                        <span className="text-slate-600 dark:text-slate-300">Community Impact (Not Grades)</span>
                        <span className="text-purple-600">High Priority (60%)</span>
                      </div>
                      <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2.5">
                        <div className="bg-purple-600 h-2.5 rounded-full w-[60%] shadow-[0_0_10px_rgba(147,51,234,0.5)]"></div>
                      </div>
                      <p className="text-[10px] text-slate-400 mt-1">AI Note: Past 5 winners all led non-profits.</p>
                    </div>

                    {/* Bar 2 */}
                    <div>
                      <div className="flex justify-between text-xs font-bold mb-1">
                        <span className="text-slate-600 dark:text-slate-300">Resilience / Grit</span>
                        <span className="text-blue-500">Medium Priority (30%)</span>
                      </div>
                      <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2.5">
                        <div className="bg-blue-500 h-2.5 rounded-full w-[30%]"></div>
                      </div>
                    </div>

                    {/* Bar 3 */}
                    <div>
                      <div className="flex justify-between text-xs font-bold mb-1">
                        <span className="text-slate-600 dark:text-slate-300 opacity-50">Academic GPA</span>
                        <span className="text-slate-400">Low Priority (10%)</span>
                      </div>
                      <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2.5">
                        <div className="bg-slate-400 h-2.5 rounded-full w-[10%]"></div>
                      </div>
                    </div>
                  </div>

                  {/* Action Box */}
                  <div className="mt-6 bg-purple-50 dark:bg-purple-900/20 p-3 rounded-lg border border-purple-100 dark:border-purple-800 flex items-start gap-3">
                    <Brain className="w-5 h-5 text-purple-600 shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs font-bold text-purple-700 dark:text-purple-300 uppercase mb-0.5">Strategy Recommendation</p>
                      <p className="text-xs text-slate-600 dark:text-slate-400 leading-snug">
                        "Don't focus on your 4.0 GPA. Instead, lead the essay with the story of the fundraising event you organized."
                      </p>
                    </div>
                  </div>

                </div>
              </div>

            </div>
          </div>
        </div>
      </section>

      {/* NEW: TEAM SECTION */}
      <section className="py-20 border-t border-slate-200 dark:border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-12">Built by Team Velocity</h2>

          <div className="flex flex-wrap justify-center gap-12">

            {/* Team Member 1 */}
            <div className="flex flex-col items-center">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 mb-4 p-1">
                <div className="w-full h-full bg-white dark:bg-slate-900 rounded-full flex items-center justify-center">
                  <User className="w-10 h-10 text-slate-400" />
                </div>
              </div>
              <h3 className="font-bold text-lg">Harmanpreet Singh</h3>
              <p className="text-blue-600 dark:text-blue-400 text-sm mb-1">Full Stack Engineer</p>
              <a href='https://github.com/HarmanPreet-Singh-XYT' className="flex gap-2 opacity-50">
                <Github className="w-4 h-4 hover:text-blue-400" />
              </a>
            </div>

            {/* Team Member 2 */}
            <div className="flex flex-col items-center">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 mb-4 p-1">
                <div className="w-full h-full bg-white dark:bg-slate-900 rounded-full flex items-center justify-center">
                  <Brain className="w-10 h-10 text-slate-400" />
                </div>
              </div>
              <h3 className="font-bold text-lg">Elliot Sones</h3>
              <p className="text-purple-600 dark:text-purple-400 text-sm mb-1">AI & ML Engineer</p>
              <a href='https://github.com/Elliot-Sones' className="flex gap-2 opacity-50">
                <Github className="w-4 h-4 hover:text-blue-400" />
              </a>
            </div>

            {/* Team Member 3 */}
            <div className="flex flex-col items-center">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 mb-4 p-1">
                <div className="w-full h-full bg-white dark:bg-slate-900 rounded-full flex items-center justify-center">
                  <Brain className="w-10 h-10 text-slate-400" />
                </div>
              </div>
              <h3 className="font-bold text-lg">Steric</h3>
              <p className="text-purple-600 dark:text-purple-400 text-sm mb-1">AI & ML Engineer</p>
              <a href='https://github.com/stericishere' className="flex gap-2 opacity-50">
                <Github className="w-4 h-4 hover:text-blue-400" />
              </a>
            </div>

            {/* Team Member 4 */}
            <div className="flex flex-col items-center">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-green-500 to-teal-600 mb-4 p-1">
                <div className="w-full h-full bg-white dark:bg-slate-900 rounded-full flex items-center justify-center">
                  <PenTool className="w-10 h-10 text-slate-400" />
                </div>
              </div>
              <h3 className="font-bold text-lg">xh-ma(Therese)</h3>
              <p className="text-green-600 dark:text-green-400 text-sm mb-1">UI/UX & Product</p>
              <div className="flex gap-2 opacity-50">
                <Github className="w-4 h-4 hover:text-blue-400" />
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="bg-black pt-20 pb-10 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-10 mb-16">

            {/* Brand Column */}
            <div className="col-span-2 md:col-span-1">
              <div className="flex items-center gap-2 mb-4">
                <div className="bg-white/10 p-2 rounded-lg border border-white/20">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <span className="font-bold text-xl tracking-tight text-white">ScholarMatch</span>
              </div>
              <p className="text-white/60 text-sm leading-relaxed mb-6">
                AI that helps students win scholarships by understanding the hidden values of every committee.
              </p>
              <div className="flex gap-4">
                <a href="https://github.com/HarmanPreet-Singh-XYT/Anthropic_Hackathon_2025" className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/60 hover:bg-white/10 hover:text-white transition-all">
                  <Github className="w-5 h-5" />
                </a>
              </div>
            </div>

            {/* Links Columns */}
            <div>
              <h4 className="font-semibold mb-6 text-white">Product</h4>
              <ul className="space-y-4 text-sm text-white/50">
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="/start" className="hover:text-white transition-colors">Live Demo</a></li>
                <li><a href="/outreach" className="hover:text-white transition-colors">Outreach</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-6 text-white">Resources</h4>
              <ul className="space-y-4 text-sm text-white/50">
                <li><a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a></li>
                <li><a href="https://github.com/HarmanPreet-Singh-XYT/Anthropic_Hackathon_2025" className="hover:text-white transition-colors">Documentation</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-6 text-white">Hackathon</h4>
              <ul className="space-y-4 text-sm text-white/50">
                <li><a href="https://github.com/HarmanPreet-Singh-XYT/Anthropic_Hackathon_2025" className="hover:text-white transition-colors">Github Repo</a></li>
                <li><span className="text-white/30">Agentiiv 2025</span></li>
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-white/40 text-sm">
              © {new Date().getFullYear()} ScholarMatch AI. Built for Agentiiv Hackathon.
            </p>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse shadow-lg shadow-green-400/50"></span>
              <span className="text-white/40 text-xs font-medium uppercase tracking-wider">Systems Operational</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;