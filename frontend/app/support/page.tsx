"use client"
import React, { useState, useEffect } from 'react';
import {
  MessageSquare, Mail, Terminal, MapPin,
  Send, ArrowRight, FileText, Github,
  HelpCircle, CheckCircle2, AlertCircle, Loader2,
  Moon, Sun, Brain, Shield, Globe, Users,
  Activity, Book, ChevronRight, Copy, Paperclip
} from 'lucide-react';
import { Navigation } from '@/components/Navigation';

const ContactPage = () => {
  const [isDark, setIsDark] = useState(true);
  const [formStatus, setFormStatus] = useState<'idle' | 'sending' | 'success'>('idle');
  const [selectedTopic, setSelectedTopic] = useState('tech');
  const [copiedEmail, setCopiedEmail] = useState(false);

  // Fake "Live" metrics for the dashboard feel
  const [latency, setLatency] = useState(45);

  useEffect(() => {
    const interval = setInterval(() => {
      setLatency(prev => prev + (Math.random() > 0.5 ? 2 : -2));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const toggleTheme = () => setIsDark(!isDark);

  const handleCopyEmail = () => {
    navigator.clipboard.writeText('enterprise@scholarfit.ai');
    setCopiedEmail(true);
    setTimeout(() => setCopiedEmail(false), 2000);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setFormStatus('sending');
    setTimeout(() => setFormStatus('success'), 2000);
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDark ? 'dark bg-slate-950' : 'bg-slate-50'}`}>
      <div className="font-sans selection:bg-purple-500/30 selection:text-purple-600 dark:selection:text-purple-300 dark:text-slate-100 transition-colors duration-300">

        {/* Navbar */}
        <Navigation variant="default" />

        {/* Hero Section with Stylized Map Background */}
        <div className="relative pt-32 pb-20 overflow-hidden">
          {/* Abstract Dot Map Background */}
          <div className="absolute inset-0 opacity-10 dark:opacity-20 pointer-events-none">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-[radial-gradient(circle,theme(colors.blue.500)_1px,transparent_1px)] bg-[size:16px_16px] [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_70%)]" />
          </div>

          <div className="relative max-w-7xl mx-auto px-6 text-center z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700/50 text-purple-700 dark:text-purple-300 text-xs font-bold font-mono tracking-wider mb-8">
              <span className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" />
              MISSION CONTROL CENTER
            </div>

            <h1 className="text-5xl md:text-7xl font-black text-slate-900 dark:text-white tracking-tighter mb-6">
              How can we <br />
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-purple-600 to-pink-500 animate-gradient-x">
                accelerate your pipeline?
              </span>
            </h1>

            <p className="text-xl text-slate-600 dark:text-slate-400 font-medium max-w-2xl mx-auto leading-relaxed">
              Connect with our engineering team, browse the knowledge base, or join the community of scholars.
            </p>
          </div>
        </div>

        {/* Quick Access "Bento" Grid */}
        <div className="max-w-7xl mx-auto px-6 mb-24">
          <div className="grid md:grid-cols-4 gap-4">

            {/* Documentation - Large Block */}
            <div className="md:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-8 rounded-3xl hover:border-blue-400 transition-all cursor-pointer group relative overflow-hidden">
              <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity transform group-hover:scale-110 duration-500">
                <Book className="w-32 h-32 text-blue-600" />
              </div>
              <div className="relative z-10">
                <div className="w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mb-6">
                  <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Knowledge Base</h3>
                <p className="text-slate-500 dark:text-slate-400 mb-6 max-w-sm">Detailed guides on RAG configuration, prompt engineering for the Ghostwriter, and API references.</p>
                <div className="flex gap-2">
                  <span className="px-3 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-xs font-mono font-bold text-slate-600 dark:text-slate-300">v2.4 Docs</span>
                  <span className="px-3 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-xs font-mono font-bold text-slate-600 dark:text-slate-300">Quickstart</span>
                </div>
              </div>
            </div>

            {/* Community */}
            <div className="bg-slate-900 p-8 rounded-3xl border border-slate-800 hover:border-purple-500 transition-all cursor-pointer group flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-6">
                  <div className="w-10 h-10 rounded-xl bg-purple-900/30 flex items-center justify-center">
                    <Users className="w-5 h-5 text-purple-400" />
                  </div>
                  <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-white transition-colors transform group-hover:translate-x-1" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">Discord</h3>
                <p className="text-slate-400 text-sm">Join 5,000+ scholars and devs.</p>
              </div>
              <div className="flex -space-x-3 mt-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="w-8 h-8 rounded-full bg-slate-700 border-2 border-slate-900" />
                ))}
                <div className="w-8 h-8 rounded-full bg-slate-800 border-2 border-slate-900 flex items-center justify-center text-[10px] text-white font-bold">+2k</div>
              </div>
            </div>

            {/* Status */}
            <div className="bg-white dark:bg-slate-900 p-8 rounded-3xl border border-slate-200 dark:border-slate-800 hover:border-green-500/50 transition-all group">
              <div className="flex items-center justify-between mb-6">
                <div className="w-10 h-10 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
                  <Activity className="w-5 h-5 text-green-600 dark:text-green-400" />
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                  </span>
                  <span className="text-xs font-bold text-green-600 dark:text-green-400">OPERATIONAL</span>
                </div>
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">System Status</h3>
              <div className="space-y-3 mt-4">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">Scout Agent</span>
                  <span className="text-green-500 font-mono">100%</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">Vector DB</span>
                  <span className="text-green-500 font-mono">99.9%</span>
                </div>
                <div className="w-full h-1 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div className="w-[99%] h-full bg-green-500 rounded-full" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Split */}
        <div className="max-w-7xl mx-auto px-6 grid lg:grid-cols-12 gap-12 lg:gap-24 pb-24">

          {/* Left Column: Context & Methods */}
          <div className="lg:col-span-5 space-y-12">
            <div>
              <h2 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight mb-6">
                Direct Uplink
              </h2>
              <p className="text-slate-600 dark:text-slate-400 leading-relaxed mb-8">
                For complex inquiries involving the RAG pipeline, enterprise API limits, or multi-agent orchestration errors, please use the secure form.
              </p>

              <div className="space-y-6">
                {/* Sales Card */}
                <div className="flex items-start gap-4 p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800">
                  <div className="mt-1 w-10 h-10 rounded-lg bg-white dark:bg-slate-800 shadow-sm flex items-center justify-center flex-shrink-0">
                    <Shield className="w-5 h-5 text-purple-600" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-bold text-slate-900 dark:text-white">Enterprise Sales</h4>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mb-2">For high-volume academic institutions.</p>
                    <button
                      onClick={handleCopyEmail}
                      className="text-sm font-mono font-bold text-purple-600 dark:text-purple-400 flex items-center gap-2 hover:opacity-80"
                    >
                      enterprise@scholarfit.ai
                      {copiedEmail ? <CheckCircle2 className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    </button>
                  </div>
                </div>

                {/* HQ Card */}
                <div className="flex items-start gap-4 p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800">
                  <div className="mt-1 w-10 h-10 rounded-lg bg-white dark:bg-slate-800 shadow-sm flex items-center justify-center flex-shrink-0">
                    <MapPin className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900 dark:text-white">Global HQ</h4>
                    <p className="text-sm text-slate-500 dark:text-slate-400 font-mono mt-1">
                      37.7749° N, 122.4194° W<br />
                      San Francisco, CA
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Meet the Engineers Section (Humanizing) */}
            <div className="pt-8 border-t border-slate-200 dark:border-slate-800">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-6">Built by Engineers</h4>
              <div className="flex items-center gap-4">
                <div className="flex -space-x-3">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className={`w-10 h-10 rounded-full border-2 border-white dark:border-slate-950 bg-gradient-to-br ${i % 2 === 0 ? 'from-blue-400 to-blue-600' : 'from-purple-400 to-purple-600'}`}></div>
                  ))}
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  <span className="font-bold text-slate-900 dark:text-white">12+ contributors</span> from MIT, Stanford & OpenAI alumni network.
                </p>
              </div>
            </div>
          </div>

          {/* Right Column: The "Smart" Form */}
          <div className="lg:col-span-7">
            <div className="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 md:p-12 shadow-2xl shadow-blue-500/10 border border-slate-200 dark:border-slate-800 relative overflow-hidden">
              {/* Decorative Gradient Top */}
              <div className="absolute top-0 left-0 right-0 h-2 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500" />

              {formStatus === 'success' ? (
                <div className="text-center py-20 animate-fade-in-up">
                  <div className="w-24 h-24 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
                    <CheckCircle2 className="w-12 h-12 text-green-600 dark:text-green-400" />
                  </div>
                  <h3 className="text-3xl font-black text-slate-900 dark:text-white mb-4">Signal Received</h3>
                  <p className="text-lg text-slate-600 dark:text-slate-400 max-w-md mx-auto mb-8">
                    Ticket <span className="font-mono bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">#SF-9921</span> has been queued. Our triage agent is analyzing your request.
                  </p>
                  <button onClick={() => setFormStatus('idle')} className="text-blue-600 font-bold hover:underline">Send another transmission</button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-8">
                  <div className="flex justify-between items-center mb-8">
                    <h3 className="text-2xl font-bold text-slate-900 dark:text-white">Secure Transmission</h3>
                    <div className="flex gap-2">
                      {['tech', 'billing', 'sales'].map((topic) => (
                        <button
                          key={topic}
                          type="button"
                          onClick={() => setSelectedTopic(topic)}
                          className={`px-4 py-2 rounded-full text-xs font-bold uppercase tracking-wide transition-all ${selectedTopic === topic
                            ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-900'
                            : 'bg-slate-100 dark:bg-slate-800 text-slate-500 hover:bg-slate-200 dark:hover:bg-slate-700'
                            }`}
                        >
                          {topic}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-slate-500 uppercase tracking-wider pl-1">Name</label>
                      <input type="text" className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl px-5 py-4 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all font-medium" placeholder="Alex Chen" required />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-bold text-slate-500 uppercase tracking-wider pl-1">Work Email</label>
                      <input type="email" className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl px-5 py-4 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all font-medium" placeholder="alex@university.edu" required />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-bold text-slate-500 uppercase tracking-wider pl-1">Subject</label>
                    <input
                      type="text"
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl px-5 py-4 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all font-medium"
                      placeholder={selectedTopic === 'tech' ? "e.g., Vector Embeddings failing to sync" : "e.g., Inquiry about University bulk pricing"}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-bold text-slate-500 uppercase tracking-wider pl-1">Message</label>
                    <textarea
                      rows={6}
                      className="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl px-5 py-4 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all font-medium resize-none"
                      placeholder="Describe the anomaly in detail..."
                      required
                    />
                  </div>

                  {/* Technical Toggles (The "Debug" Mode feel) */}
                  {selectedTopic === 'tech' && (
                    <div className="bg-slate-50 dark:bg-slate-950/50 rounded-xl p-4 border border-slate-200 dark:border-slate-800 flex items-center gap-4">
                      <div className="p-2 bg-slate-200 dark:bg-slate-800 rounded-lg">
                        <Terminal className="w-4 h-4 text-slate-600 dark:text-slate-400" />
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-bold text-slate-900 dark:text-white">Attach Session Logs</div>
                        <div className="text-xs text-slate-500">Auto-includes last 50 vector queries.</div>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" defaultChecked />
                        <div className="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 dark:peer-focus:ring-purple-800 rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-purple-600"></div>
                      </label>
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-4">
                    <button type="button" className="text-slate-500 hover:text-slate-900 dark:hover:text-white flex items-center gap-2 text-sm font-bold transition-colors">
                      <Paperclip className="w-4 h-4" /> Add Attachment
                    </button>

                    <button
                      type="submit"
                      disabled={formStatus === 'sending'}
                      className="px-8 py-4 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
                    >
                      {formStatus === 'sending' ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" /> Transmitting...
                        </>
                      ) : (
                        <>
                          Send Message <Send className="w-4 h-4" />
                        </>
                      )}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>

        {/* Footer - Consistent Circuit Board Theme */}
        <footer className="relative bg-slate-950 text-slate-400 overflow-hidden border-t border-slate-800">

          {/* Circuit Board Pattern Background */}
          <div className="absolute inset-0 opacity-[0.05]"
            style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%239C92AC' fill-opacity='1' fill-rule='evenodd'/%3E%3C/svg%3E")` }}
          />

          <div className="relative max-w-7xl mx-auto px-6 py-16 grid grid-cols-2 md:grid-cols-4 gap-12 text-sm">

            {/* Brand Column */}
            <div className="col-span-2 md:col-span-1 space-y-4">
              <div className="flex items-center gap-2 font-black text-white tracking-tighter">
                <Brain className="w-5 h-5 text-purple-500" />
                <span>ScholarMatch.ai</span>
              </div>
              <p className="text-slate-500 leading-relaxed">
                Empowering students to discover and amplify their authentic stories through AI.
              </p>
              <div className="flex gap-4 pt-2">
                <div className="w-8 h-8 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center hover:border-purple-500 hover:text-white transition-colors cursor-pointer">
                  <span className="font-bold">X</span>
                </div>
                <div className="w-8 h-8 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-center hover:border-blue-500 hover:text-white transition-colors cursor-pointer">
                  <span className="font-bold">in</span>
                </div>
              </div>
            </div>

            {/* Product Column */}
            <div>
              <h4 className="font-bold text-white mb-6 uppercase tracking-wider font-mono text-xs">Platform</h4>
              <ul className="space-y-3">
                <li className="hover:text-purple-400 transition-colors cursor-pointer">Agent Swarm</li>
                <li className="hover:text-purple-400 transition-colors cursor-pointer">RAG Pipeline</li>
                <li className="hover:text-purple-400 transition-colors cursor-pointer">Pricing</li>
                <li className="hover:text-purple-400 transition-colors cursor-pointer">Login</li>
              </ul>
            </div>

            {/* Resources Column */}
            <div>
              <h4 className="font-bold text-white mb-6 uppercase tracking-wider font-mono text-xs">Resources</h4>
              <ul className="space-y-3">
                <li className="hover:text-blue-400 transition-colors cursor-pointer">Documentation</li>
                <li className="hover:text-blue-400 transition-colors cursor-pointer">API Reference</li>
                <li className="hover:text-blue-400 transition-colors cursor-pointer">System Status</li>
                <li className="hover:text-blue-400 transition-colors cursor-pointer">Community</li>
              </ul>
            </div>

            {/* Legal Column */}
            <div>
              <h4 className="font-bold text-white mb-6 uppercase tracking-wider font-mono text-xs">Legal</h4>
              <ul className="space-y-3">
                <li className="hover:text-white transition-colors cursor-pointer">Privacy Policy</li>
                <li className="hover:text-white transition-colors cursor-pointer">Terms of Service</li>
                <li className="hover:text-white transition-colors cursor-pointer">Security</li>
              </ul>
            </div>
          </div>

          {/* Sub-footer */}
          <div className="relative border-t border-slate-800/50">
            <div className="max-w-7xl mx-auto px-6 py-8 flex flex-col md:flex-row justify-between items-center gap-4">
              <p className="text-slate-600 text-xs">
                © 2024 ScholarMatch AI Inc. All rights reserved.
              </p>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                <span className="text-xs font-mono text-green-500">SYSTEMS OPERATIONAL</span>
              </div>
            </div>
          </div>
        </footer>

      </div>
    </div>
  );
};

export default ContactPage;