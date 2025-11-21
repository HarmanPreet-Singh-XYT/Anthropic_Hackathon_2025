"use client"
import React, { useState, ReactNode } from 'react';
import { ArrowRight, CheckCircle2, Sparkles, Target, Briefcase, GraduationCap, Trophy, Zap, Layers } from 'lucide-react';

interface Angle {
  id: string;
  label: string;
  text: string;
  isOptimized: boolean;
}

interface Story {
  id: number;
  title: string;
  type: string;
  icon: ReactNode;
  matchScore: number;
  matchColor: 'green' | 'yellow' | 'red';
  reason: string;
  angles: Angle[];
}

interface SelectedAngles {
  [key: number]: string;
}

const studentStories: Story[] = [
  {
    id: 1,
    title: "Varsity Robotics Team Captain",
    type: "Leadership",
    icon: <Trophy className="w-5 h-5" />,
    matchScore: 95,
    matchColor: "green",
    reason: "Strong alignment with 'Innovation' and 'Leadership' criteria.",
    angles: [
      { id: "a1", label: "Technical Focus", text: "Designed a pneumatic lift system using CAD; improved robot efficiency by 15%.", isOptimized: false },
      { id: "a2", label: "Leadership Angle (Recommended)", text: "Managed a team of 15 peers, resolving conflict during crunch time and mentoring junior members.", isOptimized: true }
    ]
  },
  {
    id: 2,
    title: "Summer Job at McDonald's",
    type: "Work Experience",
    icon: <Briefcase className="w-5 h-5" />,
    matchScore: 78,
    matchColor: "yellow",
    reason: "Generic work experience, but can be reframed for 'Resilience'.",
    angles: [
      { id: "b1", label: "Standard Description", text: "Took orders, managed cash register, and ensured dining room cleanliness.", isOptimized: false },
      { id: "b2", label: "Resilience Angle (Recommended)", text: "Maintained composure during understaffed shifts, learning to prioritize tasks under extreme pressure.", isOptimized: true }
    ]
  },
  {
    id: 3,
    title: "High School Debate Club",
    type: "Extracurricular",
    icon: <GraduationCap className="w-5 h-5" />,
    matchScore: 45,
    matchColor: "red",
    reason: "Low relevance. This scholarship prioritizes 'Action' over 'Argumentation'.",
    angles: [
      { id: "c1", label: "Standard Description", text: "Competed in regional tournaments; won 3rd place in State Finals.", isOptimized: false }
    ]
  }
];

interface UsersIconProps {
  className?: string;
}

const UsersIcon: React.FC<UsersIconProps> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
  </svg>
);

const NarrativeMatcher: React.FC = () => {
  const [selectedStories, setSelectedStories] = useState<number[]>([1]);
  const [selectedAngles, setSelectedAngles] = useState<SelectedAngles>({ 1: "a2", 2: "b2", 3: "c1" });
  const [darkMode, setDarkMode] = useState<boolean>(false);

  const toggleStory = (id: number): void => {
    if (selectedStories.includes(id)) {
      setSelectedStories(selectedStories.filter(s => s !== id));
    } else {
      if (selectedStories.length < 3) {
        setSelectedStories([...selectedStories, id]);
      }
    }
  };

  const setAngle = (storyId: number, angleId: string): void => {
    setSelectedAngles(prev => ({ ...prev, [storyId]: angleId }));
  };

  return (
    <div className={`${darkMode ? 'dark' : ''}`}>
      <div className="min-h-screen transition-colors duration-500 font-sans bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 pb-20">
        
        <nav className="sticky top-0 z-50 backdrop-blur-xl border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 px-6 py-4">
          <div className="max-w-6xl mx-auto flex justify-between items-center">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm font-medium text-slate-400">
                <span className="flex items-center justify-center w-6 h-6 rounded-full border border-slate-300 dark:border-slate-700">1</span>
                <span className="hidden sm:inline">Analysis</span>
              </div>
              <div className="w-8 h-px bg-slate-300 dark:bg-slate-700"></div>
              <div className="flex items-center gap-2 text-sm font-bold text-indigo-600 dark:text-indigo-400">
                <span className="flex items-center justify-center w-6 h-6 rounded-full bg-indigo-600 text-white shadow-lg shadow-indigo-500/30">2</span>
                <span>Strategy</span>
              </div>
              <div className="w-8 h-px bg-slate-300 dark:bg-slate-700"></div>
              <div className="flex items-center gap-2 text-sm font-medium text-slate-400">
                <span className="flex items-center justify-center w-6 h-6 rounded-full border border-slate-300 dark:border-slate-700">3</span>
                <span className="hidden sm:inline">Draft</span>
              </div>
            </div>
            <button onClick={() => setDarkMode(!darkMode)} className="text-xs text-slate-400 hover:text-slate-600 uppercase font-bold tracking-wider border border-slate-200 dark:border-slate-800 px-3 py-1 rounded-full">
              {darkMode ? "Light" : "Dark"}
            </button>
          </div>
        </nav>

        <main className="max-w-6xl mx-auto p-6 md:p-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          <div className="lg:col-span-4 space-y-6">
            <div className="lg:sticky lg:top-24 space-y-6">
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Construct Your Narrative</h1>
                <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">Select the experiences that align with the scholarship's hidden priorities.</p>
              </div>

              <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-lg shadow-slate-200/50 dark:shadow-none border border-slate-200 dark:border-slate-800">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <Target className="w-4 h-4" /> Target Criteria
                </h3>
                <div className="space-y-4">
                  <div className="flex items-center gap-3 p-3 rounded-xl bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-800/30">
                    <div className="bg-white dark:bg-indigo-800 p-2 rounded-lg text-indigo-600 dark:text-indigo-300 shadow-sm">
                      <UsersIcon className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="font-bold text-indigo-900 dark:text-indigo-100 text-sm">Community Impact</div>
                      <div className="text-xs text-indigo-600 dark:text-indigo-400 font-medium">Weight: 45%</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 p-3 rounded-xl bg-purple-50 dark:bg-purple-900/20 border border-purple-100 dark:border-purple-800/30">
                    <div className="bg-white dark:bg-purple-800 p-2 rounded-lg text-purple-600 dark:text-purple-300 shadow-sm">
                      <Zap className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="font-bold text-purple-900 dark:text-purple-100 text-sm">Resilience / Grit</div>
                      <div className="text-xs text-purple-600 dark:text-purple-400 font-medium">Weight: 30%</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="hidden lg:block bg-slate-900 dark:bg-slate-800 text-white rounded-2xl p-6 shadow-xl">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-slate-400">Selected Stories</span>
                  <span className="text-xl font-bold text-white">{selectedStories.length} / 3</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2 mb-4">
                  <div className="bg-indigo-500 h-2 rounded-full transition-all duration-300" style={{ width: `${(selectedStories.length / 3) * 100}%` }}></div>
                </div>
                <button className={`w-full py-3 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all ${selectedStories.length > 0 ? 'bg-indigo-500 hover:bg-indigo-400 text-white shadow-lg shadow-indigo-500/50' : 'bg-slate-700 text-slate-500 cursor-not-allowed'}`}>
                  Draft Application <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <div className="lg:col-span-8 space-y-4">
            {studentStories.map((story) => {
              const isSelected = selectedStories.includes(story.id);
              
              let badgeColor = "bg-red-100 dark:bg-red-500/20 text-red-700 dark:text-red-300 border-red-200 dark:border-red-500/30";
              let dotColor = "bg-red-500";
              if (story.matchColor === 'green') {
                badgeColor = "bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-500/30";
                dotColor = "bg-emerald-500";
              } else if (story.matchColor === 'yellow') {
                badgeColor = "bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-500/30";
                dotColor = "bg-amber-500";
              }

              return (
                <div key={story.id} className={`relative group rounded-2xl border transition-all duration-300 ${isSelected ? 'bg-white dark:bg-slate-900 border-indigo-500 dark:border-indigo-500 ring-1 ring-indigo-500 shadow-xl shadow-indigo-100 dark:shadow-none' : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 hover:border-indigo-300 dark:hover:border-slate-600'}`}>
                  <div className="absolute top-4 right-4">
                    <button onClick={() => toggleStory(story.id)} className={`w-6 h-6 rounded-full border flex items-center justify-center transition-colors ${isSelected ? 'bg-indigo-600 border-indigo-600 text-white' : 'bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-600 text-transparent hover:border-indigo-400'}`}>
                      <CheckCircle2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="p-6">
                    <div className="flex items-start gap-4 mb-4 pr-8">
                      <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 shadow-sm border border-slate-100 dark:border-slate-700">
                        {story.icon}
                      </div>
                      <div>
                        <h3 className="font-bold text-lg text-slate-900 dark:text-white leading-tight mb-1">{story.title}</h3>
                        <div className="flex items-center gap-2">
                          <div className={`px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wide border flex items-center gap-1.5 ${badgeColor}`}>
                            <div className={`w-1.5 h-1.5 rounded-full ${dotColor}`}></div>
                            {story.matchScore}% Match
                          </div>
                          <span className="text-xs text-slate-400 dark:text-slate-500 font-medium">{story.type}</span>
                        </div>
                      </div>
                    </div>

                    <div className="mb-5 pl-16">
                      <p className="text-xs text-slate-500 dark:text-slate-400 italic">
                        <span className="font-semibold text-slate-700 dark:text-slate-300 not-italic">AI Insight: </span>{story.reason}
                      </p>
                    </div>

                    <div className="h-px bg-slate-100 dark:bg-slate-800 w-full mb-5"></div>

                    <div>
                      <div className="flex items-center gap-2 mb-3">
                        <Layers className="w-4 h-4 text-indigo-500" />
                        <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Choose Narrative Angle</span>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {story.angles.map((angle) => {
                          const isActive = selectedAngles[story.id] === angle.id;
                          return (
                            <div key={angle.id} onClick={() => { setAngle(story.id, angle.id); if (!isSelected) toggleStory(story.id); }} className={`relative cursor-pointer p-3 rounded-xl border transition-all duration-200 ${isActive ? 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-200 dark:border-indigo-500/50' : 'bg-slate-50 dark:bg-slate-800/50 border-transparent hover:border-slate-200 dark:hover:border-slate-700'}`}>
                              <div className="flex justify-between items-center mb-1.5">
                                <span className={`text-xs font-bold ${isActive ? 'text-indigo-700 dark:text-indigo-300' : 'text-slate-600 dark:text-slate-400'}`}>{angle.label}</span>
                                {angle.isOptimized && <Sparkles className="w-3 h-3 text-amber-500" />}
                              </div>
                              <p className={`text-sm leading-snug ${isActive ? 'text-indigo-900 dark:text-indigo-100' : 'text-slate-500 dark:text-slate-500'}`}>{angle.text}</p>
                              <div className={`absolute top-3 right-3 w-3 h-3 rounded-full border ${isActive ? 'bg-indigo-500 border-indigo-500' : 'bg-transparent border-slate-300 dark:border-slate-600'}`}></div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 p-4 z-50">
            <button className={`w-full py-3 rounded-xl font-bold text-white shadow-lg flex items-center justify-center gap-2 ${selectedStories.length > 0 ? 'bg-indigo-600' : 'bg-slate-400'}`}>
              Draft Application ({selectedStories.length}) <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </main>
      </div>
    </div>
  );
};

export default NarrativeMatcher;