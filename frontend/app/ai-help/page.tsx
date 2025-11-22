"use client"

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, Bot, User, CheckCircle2, ArrowRight } from 'lucide-react';
import { useRouter, useSearchParams } from 'next/navigation';

// --- Types ---
type Message = {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
};

type GapProgress = {
    keyword: string;
    weight: number;
    confidence: number; // 0.0-1.0
    status: 'not_started' | 'in_progress' | 'complete';
    evidenceCollected: string[];
};

type InterviewSession = {
    interviewId: string;
    sessionId: string;
    gaps: GapProgress[];
    weightedKeywords: Record<string, number>;
    isComplete: boolean;
};

export default function AIHelpPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const sessionId = searchParams?.get('session');

    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [interviewSession, setInterviewSession] = useState<InterviewSession | null>(null);
    const [showCompletion, setShowCompletion] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    // Initialize interview on mount
    useEffect(() => {
        if (!sessionId) {
            setError("No session ID provided");
            setIsLoading(false);
            return;
        }

        const initializeInterview = async () => {
            try {
                const formData = new FormData();
                formData.append('session_id', sessionId);

                const response = await fetch(`${API_URL}/api/interview/start`, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`Failed to start interview: ${response.statusText}`);
                }

                const data = await response.json();

                setInterviewSession({
                    interviewId: data.interview_id,
                    sessionId: sessionId,
                    gaps: data.gaps.map((gap: any) => ({
                        keyword: gap.keyword,
                        weight: gap.weight,
                        confidence: gap.current_confidence,
                        status: gap.status,
                        evidenceCollected: []
                    })),
                    weightedKeywords: data.weighted_keywords,
                    isComplete: false
                });

                // Add first question to messages
                setMessages([{
                    id: '1',
                    role: 'assistant',
                    content: data.first_question,
                    timestamp: new Date()
                }]);

                setIsLoading(false);

            } catch (err) {
                console.error('Error initializing interview:', err);
                setError(err instanceof Error ? err.message : 'Failed to initialize interview');
                setIsLoading(false);
            }
        };

        initializeInterview();
    }, [sessionId, API_URL]);

    const handleSendMessage = async () => {
        if (!inputValue.trim() || !interviewSession) return;

        const newUserMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: inputValue,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, newUserMsg]);
        setInputValue('');
        setIsTyping(true);

        try {
            const formData = new FormData();
            formData.append('interview_id', interviewSession.interviewId);
            formData.append('message', newUserMsg.content);

            const response = await fetch(`${API_URL}/api/interview/message`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to process message');
            }

            const data = await response.json();

            // Update gap confidences
            setInterviewSession(prev => {
                if (!prev) return prev;
                return {
                    ...prev,
                    gaps: prev.gaps.map(gap => ({
                        ...gap,
                        confidence: data.gap_updates[gap.keyword]?.confidence || gap.confidence,
                        status: data.gap_updates[gap.keyword]?.status || gap.status,
                        evidenceCollected: data.gap_updates[gap.keyword]?.evidence_collected || []
                    }))
                };
            });

            // Add AI response
            const newAiMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, newAiMsg]);

            // Check if interview is complete
            if (data.is_complete) {
                await handleCompleteInterview();
            }

        } catch (err) {
            console.error('Error sending message:', err);
            // Show error message
            const errorMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, errorMsg]);
        }

        setIsTyping(false);
    };

    const handleCompleteInterview = async () => {
        if (!interviewSession) return;

        try {
            const formData = new FormData();
            formData.append('interview_id', interviewSession.interviewId);

            const response = await fetch(`${API_URL}/api/interview/complete`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to complete interview');
            }

            const data = await response.json();

            // Store bridge story for next phase
            localStorage.setItem('bridge_story', data.bridge_story);
            localStorage.setItem('session_id', sessionId || '');

            setInterviewSession(prev => prev ? { ...prev, isComplete: true } : null);
            setShowCompletion(true);

        } catch (err) {
            console.error('Error completing interview:', err);
        }
    };

    const handleSkipInterview = () => {
        localStorage.removeItem('bridge_story');
        localStorage.removeItem('session_id');
        router.push(`/application?session=${sessionId}`);
    };

    const handleContinueToApplication = async () => {
        const bridgeStory = localStorage.getItem('bridge_story');
        const storedSessionId = localStorage.getItem('session_id');

        if (!bridgeStory || !storedSessionId) {
            console.error('Missing bridge story or session ID');
            return;
        }

        try {
            // Resume workflow with bridge story
            const formData = new FormData();
            formData.append('session_id', storedSessionId);
            formData.append('bridge_story', bridgeStory);

            const response = await fetch(`${API_URL}/api/workflow/resume`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to resume workflow');
            }

            // Navigate to application page
            router.push(`/application?session=${storedSessionId}`);

        } catch (err) {
            console.error('Error continuing to application:', err);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    // Calculate overall progress
    const overallProgress = interviewSession
        ? (interviewSession.gaps.reduce((sum, gap) => sum + gap.confidence, 0) / interviewSession.gaps.length) * 100
        : 0;

    if (isLoading) {
        return (
            <div className="min-h-screen bg-[#050505] text-white flex items-center justify-center">
                <div className="text-center">
                    <div className="w-12 h-12 border-4 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-zinc-500">Initializing interview...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-[#050505] text-white flex items-center justify-center">
                <div className="text-center max-w-md">
                    <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span className="text-3xl">⚠️</span>
                    </div>
                    <h2 className="text-2xl font-medium mb-2">Error</h2>
                    <p className="text-zinc-400 mb-6">{error}</p>
                    <button
                        onClick={() => router.push('/')}
                        className="px-6 py-2 bg-white text-black rounded-xl hover:bg-zinc-200 transition"
                    >
                        Return Home
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#050505] text-white font-sans selection:bg-white/20 relative flex flex-col pt-32 pb-10 px-4 md:px-6">

            {/* Background Effects */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                <div className="absolute top-[-20%] left-[-10%] w-[800px] h-[800px] bg-purple-500/5 rounded-full blur-[150px]" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] bg-blue-500/5 rounded-full blur-[150px]" />
                {/* Stars */}
                {[...Array(15)].map((_, i) => (
                    <div
                        key={i}
                        className="absolute rounded-full bg-white opacity-20 animate-pulse"
                        style={{
                            top: `${Math.random() * 100}%`,
                            left: `${Math.random() * 100}%`,
                            width: `${Math.random() * 2 + 1}px`,
                            height: `${Math.random() * 2 + 1}px`,
                            animationDuration: `${Math.random() * 4 + 2}s`,
                        }}
                    />
                ))}
            </div>

            <div className="relative z-10 w-full max-w-7xl mx-auto h-[80vh] flex flex-col">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full">

                    {/* LEFT COLUMN: CHAT INTERFACE */}
                    <div className="lg:col-span-8 flex flex-col h-full">

                        {/* Chat Container */}
                        <div className="flex-1 bg-[#111111]/60 backdrop-blur-xl border border-white/10 rounded-[32px] flex flex-col overflow-hidden shadow-2xl relative">

                            {/* Header */}
                            <div className="h-20 border-b border-white/5 flex items-center px-8 justify-between bg-white/5">
                                <div className="flex items-center gap-3">
                                    <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
                                    <h2 className="text-xl font-medium tracking-tight">AI Assistant</h2>
                                </div>
                                <div className="flex items-center gap-2 text-xs font-mono text-zinc-500 bg-black/20 px-3 py-1 rounded-full border border-white/5">
                                    <Sparkles className="w-3 h-3 text-purple-400" />
                                    <span>MODEL: CLAUDE 3.5 SONNET</span>
                                </div>
                            </div>

                            {/* Messages Area */}
                            <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                                {messages.map((msg) => (
                                    <motion.div
                                        key={msg.id}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                    >
                                        <div className={`flex max-w-[80%] gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>

                                            {/* Avatar */}
                                            <div className={`
                        w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0
                        ${msg.role === 'assistant' ? 'bg-white/10 text-white' : 'bg-zinc-800 text-zinc-400'}
                      `}>
                                                {msg.role === 'assistant' ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
                                            </div>

                                            {/* Bubble */}
                                            <div className={`
                        p-5 rounded-2xl text-sm leading-relaxed shadow-lg
                        ${msg.role === 'assistant'
                                                    ? 'bg-[#1A1A1A] border border-white/5 text-zinc-200 rounded-tl-none'
                                                    : 'bg-white text-black rounded-tr-none font-medium'}
                      `}>
                                                {msg.content}
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}

                                {isTyping && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="flex w-full justify-start"
                                    >
                                        <div className="flex max-w-[80%] gap-4">
                                            <div className="w-10 h-10 rounded-full bg-white/10 text-white flex items-center justify-center flex-shrink-0">
                                                <Bot className="w-5 h-5" />
                                            </div>
                                            <div className="bg-[#1A1A1A] border border-white/5 p-5 rounded-2xl rounded-tl-none flex gap-1 items-center h-[60px]">
                                                <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                                                <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                                                <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                                            </div>
                                        </div>
                                    </motion.div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>

                            {/* Input Area */}
                            <div className="p-6 bg-gradient-to-t from-black/40 to-transparent">
                                <div className="relative group">
                                    <textarea
                                        value={inputValue}
                                        onChange={(e) => setInputValue(e.target.value)}
                                        onKeyDown={handleKeyDown}
                                        placeholder="Type your message..."
                                        className="w-full bg-[#0A0A0A] border border-white/10 rounded-2xl pl-6 pr-14 py-4 text-zinc-300 placeholder:text-zinc-600 focus:outline-none focus:border-white/20 focus:bg-[#0F0F0F] transition-all resize-none h-[60px] min-h-[60px] max-h-[120px]"
                                    />
                                    <button
                                        onClick={handleSendMessage}
                                        disabled={!inputValue.trim()}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-white/10 hover:bg-white text-white hover:text-black rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        <Send className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                        </div>
                    </div>

                    {/* RIGHT COLUMN: GAP PROGRESS SIDEBAR */}
                    <div className="lg:col-span-4 flex flex-col gap-6 h-full overflow-y-auto pb-6 scrollbar-hide">

                        {/* Gap Progress Card */}
                        <div className="bg-[#111111]/60 backdrop-blur-xl border border-white/10 rounded-[32px] p-6 flex-1 flex flex-col relative overflow-hidden">
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center gap-2 text-xs font-bold tracking-widest text-zinc-400 uppercase">
                                    <div className="w-2 h-2 rounded-full bg-white" />
                                    Gap Analysis
                                </div>
                            </div>

                            <div className="space-y-3 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-white/10">
                                {interviewSession?.gaps.map((gap, index) => (
                                    <motion.div
                                        key={gap.keyword}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{
                                            opacity: 1,
                                            x: 0,
                                            borderColor: gap.confidence >= 0.75
                                                ? 'rgba(34, 197, 94, 0.3)'  // green
                                                : gap.confidence >= 0.4
                                                    ? 'rgba(234, 179, 8, 0.3)'  // yellow
                                                    : 'rgba(239, 68, 68, 0.3)'  // red
                                        }}
                                        transition={{ duration: 0.5, delay: index * 0.1 }}
                                        className="p-4 rounded-2xl border bg-white/5"
                                    >
                                        <div className="flex items-start justify-between mb-2">
                                            <h4 className="font-medium text-sm text-zinc-200">{gap.keyword}</h4>
                                            <div className="flex items-center gap-2">
                                                <span className="text-xs text-zinc-400 tabular-nums">
                                                    {Math.round(gap.confidence * 100)}%
                                                </span>
                                                <div className={`w-2 h-2 rounded-full ${gap.status === 'complete' ? 'bg-green-500' :
                                                    gap.status === 'in_progress' ? 'bg-yellow-500 animate-pulse' :
                                                        'bg-red-500'
                                                    }`} />
                                            </div>
                                        </div>

                                        {/* Progress bar */}
                                        <div className="h-1.5 bg-white/10 rounded-full overflow-hidden mb-2">
                                            <motion.div
                                                className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                                                initial={{ width: 0 }}
                                                animate={{ width: `${gap.confidence * 100}%` }}
                                                transition={{ duration: 0.5 }}
                                            />
                                        </div>

                                        {/* Weight indicator */}
                                        <div className="text-xs text-zinc-500">
                                            Priority: {Math.round(gap.weight * 100)}%
                                        </div>

                                        {/* Evidence collected */}
                                        {gap.evidenceCollected.length > 0 && (
                                            <div className="mt-2 text-xs text-zinc-400">
                                                ✓ {gap.evidenceCollected.length} point{gap.evidenceCollected.length > 1 ? 's' : ''} collected
                                            </div>
                                        )}
                                    </motion.div>
                                ))}
                            </div>

                            {/* Overall Progress */}
                            {interviewSession && (
                                <div className="mt-6 pt-6 border-t border-white/10">
                                    <div className="flex justify-between text-sm mb-2">
                                        <span className="text-zinc-400">Overall Progress</span>
                                        <span className="text-white font-medium tabular-nums">
                                            {Math.round(overallProgress)}%
                                        </span>
                                    </div>
                                    <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                                        <motion.div
                                            className="h-full bg-gradient-to-r from-green-400 to-blue-500"
                                            animate={{ width: `${overallProgress}%` }}
                                            transition={{ duration: 0.5 }}
                                        />
                                    </div>

                                    {/* Skip button - barely noticeable */}
                                    <div className="mt-4 text-center">
                                        <button
                                            onClick={handleSkipInterview}
                                            className="text-xs text-zinc-600 hover:text-zinc-400 transition-colors duration-300 underline"
                                        >
                                            skip interview
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>

                    </div>

                </div>
            </div>

            {/* Completion Modal */}
            <AnimatePresence>
                {showCompletion && interviewSession && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6"
                    >
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            className="bg-[#111] border border-white/10 rounded-3xl p-8 max-w-lg w-full"
                        >
                            <div className="text-center">
                                <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <CheckCircle2 className="w-8 h-8 text-green-500" />
                                </div>
                                <h2 className="text-2xl font-medium mb-2">Interview Complete!</h2>
                                <p className="text-zinc-400 mb-6">
                                    I've gathered all the information needed to create an amazing application.
                                </p>

                                {/* Final scores */}
                                <div className="bg-white/5 rounded-2xl p-4 mb-6 space-y-2">
                                    {interviewSession.gaps.map(gap => (
                                        <div key={gap.keyword} className="flex justify-between text-sm">
                                            <span className="text-zinc-300">{gap.keyword}</span>
                                            <span className="text-green-400 font-medium tabular-nums">
                                                {Math.round(gap.confidence * 100)}%
                                            </span>
                                        </div>
                                    ))}
                                </div>

                                <div className="flex flex-col gap-3">
                                    <button
                                        onClick={handleContinueToApplication}
                                        className="w-full h-12 bg-white text-black rounded-xl font-medium hover:bg-zinc-200 transition flex items-center justify-center gap-2"
                                    >
                                        Continue to Your Application <ArrowRight className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={handleSkipInterview}
                                        className="w-full h-12 bg-gray-600 text-white rounded-xl font-medium hover:bg-gray-500 transition flex items-center justify-center gap-2"
                                    >
                                        Skip Interview
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
