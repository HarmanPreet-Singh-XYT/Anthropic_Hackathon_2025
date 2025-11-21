"use client"
import React, { useState, ComponentType } from 'react';
import { Wand2, ArrowLeft, Download, Copy, MessageSquare, Zap, BarChart3, Sparkles, X, Bold, Italic, List, AlignLeft, ChevronDown, Clock, FileText, ThumbsUp } from 'lucide-react';

interface ScholarshipData {
  name: string;
  weights: {
    impact: number;
    resilience: number;
    creativity: number;
  };
}

interface Draft {
  score: number;
  text: string;
}

interface Drafts {
  generic: Draft;
  tailored: Draft;
}

interface Insight {
  title: string;
  type: string;
  weight: string;
  icon: ComponentType<{ className?: string }>;
  color: string;
  bg: string;
  explanation: string;
}

interface Insights {
  [key: string]: Insight;
}

const DRAFTS: Drafts = {
  generic: {
    score: 42,
    text: `<p class="mb-4">I am writing to apply for the Horizon Innovation Merit Award. I believe I am a good candidate because I get good grades and I am the captain of the Robotics Team.</p>
<p class="mb-4">In Robotics, we build robots to do tasks. It is hard work but I like it. We won a local competition last year. I also worked at McDonald's last summer. It was a busy job but I made money for college.</p>
<p>I also like to help my community. I volunteer sometimes at the library. I hope you consider me for this scholarship so I can study engineering.</p>`
  },
  tailored: {
    score: 96,
    text: `<p class="mb-4">Technological innovation is meaningless without the resilience to see it through. <span id="s1" class="highlight-sentence bg-purple-100 dark:bg-purple-900/40 text-purple-900 dark:text-purple-100 border-b-2 border-purple-400 cursor-pointer transition-all hover:bg-purple-200 dark:hover:bg-purple-800 px-1 rounded">As Captain of the Varsity Robotics Team, I didn't just design pneumatic lift systems; I managed a team of 15 peers through a critical failure the night before Regionals.</span></p>
<p class="mb-4"><span id="s2" class="highlight-sentence bg-indigo-100 dark:bg-indigo-900/40 text-indigo-900 dark:text-indigo-100 border-b-2 border-indigo-400 cursor-pointer transition-all hover:bg-indigo-200 dark:hover:bg-indigo-800 px-1 rounded">While my technical skills built the robot, it was my experience working the counter at McDonald's during understaffed rush hours that taught me how to lead under pressure.</span> That summer job was a crash course in conflict resolution that directly applied to our team's engineering challenges.</p>
<p><span id="s3" class="highlight-sentence bg-sky-100 dark:bg-sky-900/40 text-sky-900 dark:text-sky-100 border-b-2 border-sky-400 cursor-pointer transition-all hover:bg-sky-200 dark:hover:bg-sky-800 px-1 rounded">I am seeking the Horizon Award not just to fund my degree, but to join a community that values gritty, practical problem-solving over theoretical perfection.</span></p>`
  }
};

const INSIGHTS: Insights = {
  s1: {
    title: "Reframing Leadership",
    type: "Resilience Boost",
    weight: "30%",
    icon: Zap,
    color: "text-purple-600 dark:text-purple-400",
    bg: "bg-purple-100 dark:bg-purple-900/30",
    explanation: "We identified that this scholarship undervalues 'Technical Skill' (15%) but overvalues 'Resilience' (30%). By focusing on the 'critical failure' rather than the engineering design, we increased your match score by 15 points."
  },
  s2: {
    title: "Cross-Context Application",
    type: "Community Impact",
    weight: "45%",
    icon: BarChart3,
    color: "text-indigo-600 dark:text-indigo-400",
    bg: "bg-indigo-100 dark:bg-indigo-900/30",
    explanation: "Working at McDonald's is often seen as generic. We reframed it as 'Leadership Under Pressure' to directly hit the Community Impact criteria. This connects a low-value asset to a high-value requirement."
  },
  s3: {
    title: "Psychological Alignment",
    type: "Tone Matching",
    weight: "100%",
    icon: Sparkles,
    color: "text-sky-600 dark:text-sky-400",
    bg: "bg-sky-100 dark:bg-sky-900/30",
    explanation: "The scholarship description repeatedly used the phrase 'Action over Theory.' We mirrored this specific lexicon in the closing statement to subconsciously build rapport with the admission committee."
  }
};

type TabType = 'generic' | 'tailored';

const SmartDrafter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('tailored');
  const [selectedSentence, setSelectedSentence] = useState<string | null>(null);
  const [darkMode, setDarkMode] = useState<boolean>(false);
  const [isCopied, setIsCopied] = useState<boolean>(false);

  const handleTextClick = (e: React.MouseEvent<HTMLDivElement>): void => {
    const target = (e.target as HTMLElement).closest('.highlight-sentence');
    if (target) {
      setSelectedSentence(target.id);
    } else {
      setSelectedSentence(null);
    }
  };

  const handleCopy = (): void => {
    navigator.clipboard.writeText(DRAFTS[activeTab].text.replace(/<[^>]*>?/gm, ''));
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const currentInsight = selectedSentence ? INSIGHTS[selectedSentence] : null;

  return (
    <div className={`${darkMode ? 'dark' : ''}`}>
      <div className="min-h-screen transition-colors duration-500 font-sans bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col overflow-hidden">
        
        <nav className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-6 flex items-center justify-between z-20 shadow-sm">
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors text-slate-500">
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="flex flex-col">
              <h1 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                Scholarship Essay Draft
                <span className="px-2 py-0.5 rounded text-xs bg-indigo-100 text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-300 uppercase tracking-wide font-bold">
                  v2.1 Optimized
                </span>
              </h1>
              <span className="text-xs text-slate-500 dark:text-slate-400">Last saved: Just now</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button onClick={() => setDarkMode(!darkMode)} className="px-3 py-1.5 text-xs font-medium text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors">
               {darkMode ? "Light Mode" : "Dark Mode"}
            </button>
            <div className="h-6 w-px bg-slate-200 dark:bg-slate-700"></div>
            <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-lg transition-all shadow-md hover:shadow-lg">
               <Download className="w-3 h-3" /> Export PDF
            </button>
          </div>
        </nav>

        <main className="flex-1 max-w-7xl mx-auto w-full p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          <div className="lg:col-span-8 flex flex-col bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm overflow-hidden">
            
            <div className="h-14 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-4 bg-slate-50/50 dark:bg-slate-900">
              <div className="flex items-center gap-1 text-slate-400">
                 <button className="p-2 hover:bg-slate-200 dark:hover:bg-slate-800 rounded"><Bold className="w-4 h-4" /></button>
                 <button className="p-2 hover:bg-slate-200 dark:hover:bg-slate-800 rounded"><Italic className="w-4 h-4" /></button>
                 <div className="h-4 w-px bg-slate-300 dark:bg-slate-700 mx-1"></div>
                 <button className="p-2 hover:bg-slate-200 dark:hover:bg-slate-800 rounded"><AlignLeft className="w-4 h-4" /></button>
                 <button className="p-2 hover:bg-slate-200 dark:hover:bg-slate-800 rounded"><List className="w-4 h-4" /></button>
              </div>

              <div className="flex items-center bg-slate-200 dark:bg-slate-800 rounded-lg p-1">
                <button 
                  onClick={() => { setActiveTab('generic'); setSelectedSentence(null); }}
                  className={`px-4 py-1.5 text-xs font-bold rounded-md transition-all ${
                    activeTab === 'generic' 
                    ? 'bg-white dark:bg-slate-600 text-slate-900 dark:text-white shadow-sm' 
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700'
                  }`}
                >
                  Generic
                </button>
                <button 
                  onClick={() => setActiveTab('tailored')}
                  className={`px-4 py-1.5 text-xs font-bold rounded-md transition-all flex items-center gap-2 ${
                    activeTab === 'tailored' 
                    ? 'bg-indigo-600 text-white shadow-md' 
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700'
                  }`}
                >
                  <Wand2 className="w-3 h-3" /> Tailored
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto relative p-10 bg-white dark:bg-slate-900 transition-colors duration-300">
              {activeTab === 'tailored' && !selectedSentence && (
                <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 pointer-events-none">
                  <div className="bg-indigo-600 text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg flex items-center gap-2">
                    <MessageSquare className="w-3 h-3" /> Click highlighted text for AI insights
                  </div>
                </div>
              )}

              <div 
                 className={`max-w-3xl mx-auto text-lg leading-loose transition-opacity duration-300 ${
                   activeTab === 'generic' ? 'text-slate-500 dark:text-slate-500 opacity-80' : 'text-slate-800 dark:text-slate-200'
                 }`}
                 onClick={handleTextClick}
                 dangerouslySetInnerHTML={{ __html: DRAFTS[activeTab].text }}
              />
            </div>

            <div className="h-10 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 flex items-center justify-between px-6 text-xs text-slate-500 dark:text-slate-400">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1"><FileText className="w-3 h-3" /> 342 Words</span>
                <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> 2 min read</span>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={handleCopy} className="hover:text-indigo-500 flex items-center gap-1 transition-colors">
                   {isCopied ? <span className="text-green-500 font-bold">Copied!</span> : <><Copy className="w-3 h-3" /> Copy Text</>}
                </button>
              </div>
            </div>
          </div>

          <div className="lg:col-span-4 flex flex-col gap-6">
            
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm flex flex-col items-center relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-purple-500"></div>
              
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">Optimization Score</h3>
              
              <div className="relative w-32 h-32 mb-2">
                 <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="45" fill="transparent" stroke={darkMode ? "#1e293b" : "#f1f5f9"} strokeWidth="10" />
                    <circle 
                      cx="50" cy="50" r="45" 
                      fill="transparent" 
                      stroke={activeTab === 'tailored' ? "#4f46e5" : "#94a3b8"} 
                      strokeWidth="10" 
                      strokeDasharray="283" 
                      strokeDashoffset={283 - (283 * DRAFTS[activeTab].score) / 100}
                      strokeLinecap="round"
                      className="transition-all duration-1000 ease-out"
                    />
                 </svg>
                 <div className="absolute inset-0 flex flex-col items-center justify-center">
                   <span className={`text-3xl font-bold transition-all duration-500 ${
                     activeTab === 'tailored' ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400'
                   }`}>
                     {DRAFTS[activeTab].score}
                   </span>
                 </div>
              </div>
              
              <p className="text-sm text-slate-500 text-center">
                {activeTab === 'tailored' 
                  ? "Excellent! This draft hits 100% of the hidden criteria." 
                  : "This draft misses 2 key scholarship values."}
              </p>
            </div>

            <div className="flex-1 bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 relative overflow-hidden">
               
               <div className="flex items-center gap-2 mb-6">
                 <Zap className={`w-5 h-5 ${selectedSentence ? 'text-indigo-500' : 'text-slate-400'}`} />
                 <h3 className="font-bold text-slate-900 dark:text-white">X-Ray Insights</h3>
               </div>

               {!currentInsight ? (
                 <div className="h-full flex flex-col items-center justify-center text-center opacity-50 pb-10">
                    <div className="w-16 h-16 bg-white dark:bg-slate-800 rounded-full flex items-center justify-center mb-4 border border-slate-200 dark:border-slate-700">
                      <Sparkles className="w-8 h-8 text-indigo-400" />
                    </div>
                    <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Select a highlighted sentence <br/> to see the AI reasoning.</p>
                 </div>
               ) : (
                 <div>
                    <div className="flex items-center justify-between mb-4">
                       <span className={`text-xs font-bold uppercase tracking-wider px-2 py-1 rounded border ${currentInsight.color} ${currentInsight.bg} border-current opacity-80`}>
                         {currentInsight.type}
                       </span>
                       <button onClick={() => setSelectedSentence(null)} className="p-1 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-full transition-colors">
                         <X className="w-4 h-4 text-slate-400" />
                       </button>
                    </div>

                    <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-2 leading-tight">
                      {currentInsight.title}
                    </h4>

                    <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed mb-6">
                      {currentInsight.explanation}
                    </p>

                    <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 mb-6">
                       <div className="flex justify-between items-center mb-2">
                          <span className="text-xs font-bold text-slate-500 uppercase">Scholarship Weight</span>
                          <span className="text-sm font-bold text-slate-900 dark:text-white">
                            {currentInsight.weight}
                          </span>
                       </div>
                       <div className="w-full bg-slate-100 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-indigo-500 transition-all duration-1000 ease-out"
                            style={{ width: currentInsight.weight }}
                          ></div>
                       </div>
                    </div>

                    <div>
                      <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                        <Wand2 className="w-3 h-3" /> AI Rewrite Options
                      </div>
                      <div className="space-y-2">
                        <button className="w-full flex items-center justify-between p-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:border-indigo-500 dark:hover:border-indigo-500 group transition-all shadow-sm hover:shadow-md">
                          <span className="text-xs font-medium text-slate-600 dark:text-slate-300 group-hover:text-indigo-600 dark:group-hover:text-indigo-400">Make it more concise</span>
                          <ChevronDown className="w-3 h-3 text-slate-400 group-hover:text-indigo-500 -rotate-90" />
                        </button>
                        <button className="w-full flex items-center justify-between p-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:border-indigo-500 dark:hover:border-indigo-500 group transition-all shadow-sm hover:shadow-md">
                          <span className="text-xs font-medium text-slate-600 dark:text-slate-300 group-hover:text-indigo-600 dark:group-hover:text-indigo-400">Adjust tone: More Formal</span>
                          <ChevronDown className="w-3 h-3 text-slate-400 group-hover:text-indigo-500 -rotate-90" />
                        </button>
                      </div>
                      
                      <div className="flex justify-center gap-4 mt-4">
                         <button className="text-slate-400 hover:text-green-500 transition-colors"><ThumbsUp className="w-4 h-4" /></button>
                         <button className="text-slate-400 hover:text-red-500 transition-colors transform rotate-180"><ThumbsUp className="w-4 h-4" /></button>
                      </div>
                    </div>
                 </div>
               )}

               <div className="absolute top-0 right-0 -mt-10 -mr-10 w-40 h-40 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none"></div>
               <div className="absolute bottom-0 left-0 -mb-10 -ml-10 w-40 h-40 bg-purple-500/5 rounded-full blur-3xl pointer-events-none"></div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default SmartDrafter;