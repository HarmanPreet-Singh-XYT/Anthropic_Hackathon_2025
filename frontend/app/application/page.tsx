"use client"

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// Added LayoutGrid to imports for the dashboard icon
import { Sparkles, FileDown, Loader2, CheckCircle, Copy, ArrowRight, LayoutGrid } from 'lucide-react';
import { useRouter, useSearchParams } from 'next/navigation';
import TiptapEditor from '@/components/Editor';
import { exportMarkdownToPDF } from '@/app/actions/export';

// --- Types ---
interface ApplicationData {
    essay?: string;
    resume_optimizations?: Array<{
        original: string;
        optimized: string;
        weight: number;
    }>;
    strategy_note?: string;
    full_resume_markdown?: string;
}

type TabType = 'essay' | 'improvements' | 'resume';

export default function ApplicationPage() {
    const [applicationData, setApplicationData] = useState<ApplicationData | null>(null);
    const [activeTab, setActiveTab] = useState<TabType>('essay');
    const [isExporting, setIsExporting] = useState(false);
    const [exportSuccess, setExportSuccess] = useState(false);
    const [copiedResume, setCopiedResume] = useState(false);
    const [copiedEssay, setCopiedEssay] = useState(false);
    const [resumeContent, setResumeContent] = useState('');
    const router = useRouter();
    const searchParams = useSearchParams();
    const session_id = searchParams!.get('session');
    const contentRef = useRef<HTMLDivElement>(null);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    useEffect(() => {
        if (!session_id) return;

        const fetchData = async () => {
            try {
                const response = await fetch(`${API_URL}/api/workflow/status/${session_id}`);
                if (!response.ok) throw new Error("Failed to fetch data");

                const data = await response.json();
                console.log(data);

                if (data.status === "complete" && data.result) {
                    const appData = {
                        essay: data.result.essay_draft,
                        resume_optimizations: data.result.resume_optimizations?.optimizations || [], // ← Changed
                        strategy_note: data.result.strategy_note,
                        full_resume_markdown: data.result.optimized_resume_markdown
                    };
                    setApplicationData(appData);
                    // Initialize resume content
                    if (appData.full_resume_markdown) {
                        setResumeContent(appData.full_resume_markdown);
                    }
                } else if (data.status === "waiting_for_input") {
                    router.push(`/ai-help?session=${session_id}`);
                } else if (data.status === "processing" || data.status === "processing_resume") {
                    setTimeout(fetchData, 2000);
                }
            } catch (e) {
                console.error("Error fetching application data:", e);
            }
        };

        fetchData();
    }, [session_id, router]);


    const handleExportPDF = async () => {
        if (!resumeContent) {
            console.warn('No resume content to export');
            return;
        }

        setIsExporting(true);
        
        try {
            // Call the server action
            const result = await exportMarkdownToPDF(resumeContent);

            if (!result.success || !result.data) {
                throw new Error(result.error || 'Failed to generate PDF');
            }

            // Convert base64 to blob
            const binaryString = atob(result.data);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            const blob = new Blob([bytes], { type: 'application/pdf' });

            // Create download link
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `resume-${new Date().toISOString().split('T')[0]}.pdf`;
            
            // Trigger download
            document.body.appendChild(a);
            a.click();
            
            // Cleanup
            document.body.removeChild(a);
            setTimeout(() => URL.revokeObjectURL(url), 100);

            // Show success message
            setExportSuccess(true);
            setTimeout(() => setExportSuccess(false), 3000);

        } catch (error) {
            console.error('Error exporting PDF:', error);
        } finally {
            setIsExporting(false);
        }
    };


    const handleCopyResume = () => {
        if (!applicationData?.resume_optimizations) return;
        const text = applicationData.resume_optimizations
            .map(opt => opt.optimized)
            .join('\n');
        navigator.clipboard.writeText(text);
        setCopiedResume(true);
        setTimeout(() => setCopiedResume(false), 2000);
    };

    const handleCopyEssay = () => {
        if (!applicationData?.essay) return;
        navigator.clipboard.writeText(applicationData.essay);
        setCopiedEssay(true);
        setTimeout(() => setCopiedEssay(false), 2000);
    };

    const handleCopyResumeMarkdown = () => {
        navigator.clipboard.writeText(resumeContent);
        setCopiedResume(true);
        setTimeout(() => setCopiedResume(false), 2000);
    };

    if (!applicationData) {
        return (
            <div className="min-h-screen bg-[#050505] text-white flex items-center justify-center">
                <div className="text-center">
                    <div className="w-12 h-12 border-4 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-zinc-500">Generating your application...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="h-screen overflow-hidden bg-[#050505] text-white font-sans selection:bg-white/20 relative flex flex-col">
            {/* Background Stars/Particles */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                {[...Array(30)].map((_, i) => (
                    <motion.div
                        key={i}
                        className="absolute rounded-full bg-white"
                        initial={{
                            opacity: 0,
                            top: `${Math.random() * 100}%`,
                            left: `${Math.random() * 100}%`,
                        }}
                        animate={{
                            opacity: [0.1, 0.4, 0.1],
                            scale: [1, 1.5, 1],
                        }}
                        transition={{
                            duration: Math.random() * 3 + 2,
                            repeat: Infinity,
                            delay: Math.random() * 2,
                        }}
                        style={{
                            width: `${Math.random() * 3 + 1}px`,
                            height: `${Math.random() * 3 + 1}px`,
                        }}
                    />
                ))}
                <div className="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-[150px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-[150px]" />
            </div>


            {/* Main Content - Fixed Layout */}
            <div className="relative z-10 max-w-6xl mx-auto px-6 h-full flex flex-col">
                {/* Header - Fixed */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="text-center py-6 flex-shrink-0"
                >
                    <div className="inline-flex items-center justify-center mb-3">
                        <Sparkles className="w-10 h-10 text-white fill-white" />
                    </div>
                    <h1 className="text-4xl md:text-5xl font-medium tracking-tight mb-2">
                        Your Application
                    </h1>
                    <p className="text-zinc-400 text-base font-light tracking-wide">
                        Ready to impress
                    </p>
                </motion.div>

                {/* Combined Content Section - Scrollable */}
                <div ref={contentRef} className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent pb-6">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="bg-[#111111]/80 backdrop-blur-2xl border border-white/10 rounded-[24px] p-8 shadow-2xl shadow-black/50 relative overflow-hidden"
                    >
                        {/* Inner Glow */}
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-1 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-50" />

                        {/* Header with Tabs on Right */}
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center gap-3">
                                <div className="w-2 h-2 rounded-full bg-white" />
                                <h2 className="text-xs font-bold tracking-widest text-white uppercase">
                                    {activeTab === 'essay' ? 'Essay' : activeTab === 'improvements' ? 'Improvements' : 'Resume'}
                                </h2>
                            </div>

                            {/* Tab Buttons - Right Aligned */}
                            <div className="flex items-center gap-1 bg-[#0a0a0a]/80 border border-white/10 rounded-xl p-1">
                                <button
                                    onClick={() => setActiveTab('essay')}
                                    className={`px-4 py-2 text-xs font-medium rounded-lg transition-all duration-300 ${activeTab === 'essay'
                                        ? 'bg-white text-black shadow-lg'
                                        : 'text-zinc-400 hover:text-white hover:bg-white/5'
                                        }`}
                                >
                                    Essay
                                </button>
                                <button
                                    onClick={() => setActiveTab('improvements')}
                                    className={`px-4 py-2 text-xs font-medium rounded-lg transition-all duration-300 ${activeTab === 'improvements'
                                        ? 'bg-white text-black shadow-lg'
                                        : 'text-zinc-400 hover:text-white hover:bg-white/5'
                                        }`}
                                >
                                    Improvements
                                </button>
                                <button
                                    onClick={() => setActiveTab('resume')}
                                    className={`px-4 py-2 text-xs font-medium rounded-lg transition-all duration-300 ${activeTab === 'resume'
                                        ? 'bg-white text-black shadow-lg'
                                        : 'text-zinc-400 hover:text-white hover:bg-white/5'
                                        }`}
                                >
                                    Resume
                                </button>
                            </div>
                        </div>

                        {/* Content Area */}
                        <AnimatePresence mode="wait">
                            {activeTab === 'essay' ? (
                                <motion.div
                                    key="essay"
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 20 }}
                                    transition={{ duration: 0.3 }}
                                >
                                    <div className="bg-[#0a0a0a]/50 border border-white/5 rounded-xl p-6 min-h-[400px] relative">
                                        {/* Copy Button inside box */}
                                        {<button
                                            onClick={handleCopyEssay}
                                            className="absolute top-4 right-4 text-xs flex items-center gap-2 text-zinc-400 hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-white/10"
                                        >
                                            {copiedEssay ? <CheckCircle className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
                                            {copiedEssay ? "Copied" : "Copy"}
                                        </button>}

                                        {applicationData.essay ? (
                                            <div className="prose prose-invert max-w-none">
                                                <p className="text-zinc-300 leading-relaxed whitespace-pre-wrap font-light text-base">
                                                    {applicationData.essay}
                                                </p>
                                            </div>
                                        ) : (
                                            <p className="text-zinc-500 italic">Your essay will appear here...</p>
                                        )}
                                    </div>

                                    {applicationData.strategy_note && (
                                        <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                                            <p className="text-xs text-blue-300/80 font-medium mb-1">Strategy Note</p>
                                            <p className="text-sm text-blue-200/60">{applicationData.strategy_note}</p>
                                        </div>
                                    )}
                                </motion.div>
                            ) : activeTab === 'improvements' ? (
                                <motion.div
                                    key="improvements"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    transition={{ duration: 0.3 }}
                                >
                                    <div className="bg-[#0a0a0a]/50 border border-white/5 rounded-xl p-6 min-h-[400px]">
                                        {applicationData.resume_optimizations && applicationData.resume_optimizations.length > 0 ? (
                                            <div className="space-y-6">
                                                {applicationData.resume_optimizations.map((opt, index) => (
                                                    <div key={index} className="space-y-3">
                                                        <div>
                                                            <p className="text-xs text-zinc-500 mb-2">Original</p>
                                                            <p className="text-sm text-zinc-400 line-through opacity-60">{opt.original}</p>
                                                        </div>
                                                        <div>
                                                            <p className="text-xs text-green-400 mb-2 flex items-center gap-2">
                                                                Optimized
                                                                <span className="text-[10px] px-2 py-0.5 bg-green-500/20 border border-green-500/30 rounded-full">
                                                                    Weight: {Math.round(opt.weight * 100)}%
                                                                </span>
                                                            </p>
                                                            <p className="text-sm text-zinc-200">{opt.optimized}</p>
                                                        </div>
                                                        {index < applicationData.resume_optimizations!.length - 1 && (
                                                            <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-zinc-500 italic">Your resume improvements will appear here...</p>
                                        )}
                                    </div>
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="resume"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    transition={{ duration: 0.3 }}
                                >
                                    <div className="bg-[#0a0a0a]/50 border border-white/5 rounded-xl overflow-hidden min-h-[500px] relative">
                                        {resumeContent ? (
                                            <div className="h-[500px]">
                                                <TiptapEditor
                                                    initialMarkdown={resumeContent}
                                                    onChange={(newMarkdown) => {
                                                        setResumeContent(newMarkdown);
                                                    }}
                                                />
                                            </div>
                                        ) : (
                                            <div className="flex items-center justify-center h-[500px]">
                                                <p className="text-zinc-500 italic">Your resume will appear here...</p>
                                            </div>
                                        )}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </motion.div>
                </div>

                {/* Export and Action Buttons - Fixed at Bottom */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.6 }}
                    className="flex justify-center gap-4 flex-wrap py-4 flex-shrink-0"
                >
                    {/* Dashboard Button (Added) */}
                    <button
                        onClick={() => router.push('/dashboard')}
                        className="group relative h-12 px-6 rounded-xl font-medium text-sm flex items-center justify-center gap-2 bg-[#111111] text-zinc-400 border border-white/10 hover:bg-white/5 hover:text-white transition-all duration-300"
                    >
                        <LayoutGrid className="w-4 h-4" />
                        Dashboard
                    </button>

                    <button
                        onClick={handleExportPDF}
                        disabled={isExporting}
                        className="group relative h-12 px-6 rounded-xl font-medium text-sm flex items-center justify-center gap-2 bg-white text-black hover:bg-zinc-100 disabled:bg-zinc-700 disabled:text-zinc-400 hover:scale-[1.02] active:scale-[0.98] shadow-2xl shadow-white/20 transition-all duration-300 overflow-hidden"
                    >
                        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 via-blue-500/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                        <span className="relative z-10 flex items-center gap-2">
                            {isExporting ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Exporting...
                                </>
                            ) : exportSuccess ? (
                                <>
                                    <CheckCircle className="w-4 h-4" />
                                    Exported!
                                </>
                            ) : (
                                <>
                                    <FileDown className="w-4 h-4" />
                                    Export PDF
                                </>
                            )}
                        </span>
                    </button>

                    <button
                        onClick={() => router.push(`/outreach?session_id=${session_id}`)}
                        className="group relative h-12 px-6 rounded-xl font-medium text-sm flex items-center justify-center gap-2 bg-[#111111] text-white border border-white/10 hover:bg-white/5 hover:scale-[1.02] active:scale-[0.98] transition-all duration-300"
                    >
                        <span className="relative z-10 flex items-center gap-2">
                            <Sparkles className="w-4 h-4 text-blue-400" />
                            Draft Email
                        </span>
                    </button>

                    <button
                        onClick={() => {
                            const resumeSessionId = localStorage.getItem('resume_session_id');
                            if (resumeSessionId) {
                                router.push(`/start?resume_session=${resumeSessionId}`);
                            } else {
                                router.push('/start');
                            }
                        }}
                        className="group relative h-12 px-6 rounded-xl font-medium text-sm flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white                        hover:from-purple-700 hover:to-blue-700 hover:scale-[1.02] active:scale-[0.98] shadow-xl shadow-purple-500/30 transition-all duration-300"
                    >
                        <span className="relative z-10 flex items-center gap-2">
                            <ArrowRight className="w-4 h-4" />
                            Submit Another Application
                        </span>
                    </button>
                </motion.div>
            </div>
        </div>
    );
}