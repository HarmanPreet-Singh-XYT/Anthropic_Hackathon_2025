"use client"

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Zap, CheckCircle2, ArrowRight, ChevronDown, Loader2, AlertCircle } from 'lucide-react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ParticleBackground } from '@/components/ParticleBackground';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

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
    confidence: number;
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

    const [keywordsExpanded, setKeywordsExpanded] = useState(true);
    const [resumeExpanded, setResumeExpanded] = useState(true);

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

            const newAiMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, newAiMsg]);

            if (data.is_complete) {
                await handleCompleteInterview();
            }

        } catch (err) {
            console.error('Error sending message:', err);
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

            localStorage.setItem('bridge_story', data.bridge_story);
            localStorage.setItem('session_id', sessionId || '');

            setInterviewSession(prev => prev ? { ...prev, isComplete: true } : null);
            setShowCompletion(true);

        } catch (err) {
            console.error('Error completing interview:', err);
        }
    };

    const handleSkipInterview = async () => {
        if (!sessionId) return;

        try {
            const formData = new FormData();
            formData.append('session_id', sessionId);
            formData.append('bridge_story', '');

            const response = await fetch(`${API_URL}/api/workflow/resume`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to resume workflow');
            }

            localStorage.removeItem('bridge_story');
            localStorage.removeItem('session_id');
            router.push(`/application?session=${sessionId}`);

        } catch (err) {
            console.error('Error skipping interview:', err);
            router.push(`/application?session=${sessionId}`);
        }
    };

    const handleContinueToApplication = async () => {
        const bridgeStory = localStorage.getItem('bridge_story');
        const storedSessionId = localStorage.getItem('session_id');

        if (!bridgeStory || !storedSessionId) {
            console.error('Missing bridge story or session ID');
            return;
        }

        try {
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

            router.push(`/application?session=${storedSessionId}`);

        } catch (err) {
            console.error('Error continuing to application:', err);
        }
    };

    // Calculate overall progress
    const overallProgress = interviewSession
        ? (interviewSession.gaps.reduce((sum, gap) => sum + gap.confidence, 0) / interviewSession.gaps.length) * 100
        : 0;

    if (isLoading) {
        return (
            <div className="min-h-screen bg-black text-white flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-white" />
                    <p className="text-gray-400">Initializing interview...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-black text-white flex items-center justify-center">
                <div className="text-center max-w-md">
                    <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                    <h2 className="text-2xl font-medium mb-2">Error</h2>
                    <p className="text-gray-400 mb-6">{error}</p>
                    <button
                        onClick={() => router.push('/')}
                        className="px-6 py-2 bg-white text-black rounded-xl hover:bg-gray-200 transition"
                    >
                        Return Home
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="h-screen bg-black text-white font-sans selection:bg-white/20 overflow-hidden relative">

            <ParticleBackground />

            {/* Animated Mesh Gradient Background */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <motion.div
                    animate={{
                        x: [0, 200, 0],
                        y: [0, -150, 0],
                        scale: [1, 1.2, 1],
                    }}
                    transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
                    className="absolute -top-40 -left-40 w-[600px] h-[600px] rounded-full"
                    style={{
                        background: 'radial-gradient(circle, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 40%, transparent 70%)',
                        filter: 'blur(60px)',
                    }}
                />
                <motion.div
                    animate={{
                        x: [0, -150, 0],
                        y: [0, 200, 0],
                        scale: [1, 1.3, 1],
                    }}
                    transition={{ duration: 30, repeat: Infinity, ease: "easeInOut" }}
                    className="absolute -bottom-40 -right-40 w-[700px] h-[700px] rounded-full"
                    style={{
                        background: 'radial-gradient(circle, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.04) 40%, transparent 70%)',
                        filter: 'blur(70px)',
                    }}
                />
            </div>

            <div className="min-h-[800px] w-full p-6 relative">
                <div className="max-w-[1150px] mx-auto min-h-full py-8">
                    <div className="grid grid-cols-3 gap-5 min-h-[700px]">
                        {/* Chat Section */}
                        <div className="col-span-2 relative flex flex-col">
                            {/* Rotating gradient border */}
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                                className="absolute -inset-[2px] rounded-3xl opacity-50"
                                style={{
                                    background: 'linear-gradient(60deg, rgba(255,255,255,0.3), transparent, rgba(255,255,255,0.2), transparent)',
                                }}
                            />

                            <motion.div
                                initial={{ opacity: 0, x: -30 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.1 }}
                                whileHover={{ y: -3 }}
                                className="relative h-full bg-black/50 backdrop-blur-3xl border border-white/20 rounded-3xl p-6 flex flex-col overflow-hidden max-h-[700px]"
                                style={{ boxShadow: '0 0 60px rgba(255,255,255,0.1)' }}
                            >
                                <div className="relative z-10 mb-4 flex items-center gap-3 flex-shrink-0">
                                    <motion.div
                                        animate={{
                                            scale: [1, 1.1, 1],
                                            rotate: [0, 5, -5, 0]
                                        }}
                                        transition={{ duration: 3, repeat: Infinity }}
                                    >
                                        <div className="w-3 h-3 bg-white rounded-full shadow-lg shadow-white/50" />
                                    </motion.div>
                                    <h2 className="text-white text-xl tracking-tight" style={{ fontWeight: 200 }}>
                                        AI Assistant
                                    </h2>
                                </div>

                                <div className="relative flex-1 overflow-y-auto space-y-4 mb-4 pr-2 min-h-0">
                                    <AnimatePresence initial={false}>
                                        {messages.map((message, index) => (
                                            <motion.div
                                                key={message.id}
                                                initial={{ opacity: 0, y: 20, x: message.role === 'user' ? 20 : -20, scale: 0.95 }}
                                                animate={{ opacity: 1, y: 0, x: 0, scale: 1 }}
                                                transition={{
                                                    type: "spring",
                                                    stiffness: 300,
                                                    damping: 25,
                                                    delay: index * 0.05
                                                }}
                                                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                            >
                                                <motion.div
                                                    whileHover={{ scale: 1.01, y: -1 }}
                                                    className={`relative max-w-[85%] rounded-3xl p-5 ${message.role === 'user'
                                                        ? 'bg-white text-black'
                                                        : 'bg-white/5 text-white backdrop-blur-sm border border-white/20'
                                                        }`}
                                                    style={{
                                                        borderRadius: message.role === 'user' ? '24px 24px 4px 24px' : '24px 24px 24px 4px',
                                                        boxShadow: message.role === 'user'
                                                            ? '0 8px 32px rgba(255,255,255,0.2)'
                                                            : '0 4px 20px rgba(0,0,0,0.3)'
                                                    }}
                                                >
                                                    <span className="relative text-sm">{message.content}</span>
                                                </motion.div>
                                            </motion.div>
                                        ))}

                                        {isTyping && (
                                            <motion.div
                                                initial={{ opacity: 0, y: 20 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                className="flex justify-start"
                                            >
                                                <div className="bg-white/5 backdrop-blur-sm border border-white/20 rounded-3xl p-5 flex gap-1">
                                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                                                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                                                </div>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                    <div ref={messagesEndRef} />
                                </div>

                                <div className="relative flex gap-3 flex-shrink-0">
                                    <div className="flex-1 relative group">
                                        <Input
                                            value={inputValue}
                                            onChange={(e) => setInputValue(e.target.value)}
                                            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                                            placeholder="Type your message..."
                                            className="relative py-6 px-5 bg-white/5 border-white/20 text-white placeholder:text-gray-600 focus:border-white/30 focus:bg-white/10 rounded-full"
                                        />
                                    </div>

                                    <Button
                                        onClick={handleSendMessage}
                                        disabled={!inputValue.trim()}
                                        className="h-full px-7 bg-white text-black hover:bg-gray-100 rounded-full disabled:opacity-30"
                                    >
                                        <Send className="h-5 w-5" />
                                    </Button>
                                </div>
                            </motion.div>
                        </div>

                        {/* Context Section - Gap Analysis */}
                        <div className="space-y-5 flex flex-col min-h-0">
                            <motion.div
                                initial={{ opacity: 0, x: 30, rotateY: 20 }}
                                animate={{ opacity: 1, x: 0, rotateY: 0 }}
                                transition={{ delay: 0.3 }}
                                whileHover={{ scale: 1.03, rotateY: -5 }}
                                className="relative flex-1 flex flex-col min-h-0"
                                style={{ transformStyle: 'preserve-3d' }}
                            >
                                <motion.div
                                    animate={{ rotate: -360 }}
                                    transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                                    className="absolute -inset-[2px] rounded-3xl opacity-40"
                                    style={{
                                        background: 'linear-gradient(240deg, rgba(255,255,255,0.25), transparent, rgba(255,255,255,0.25))',
                                    }}
                                />

                                <div className="relative bg-black/50 backdrop-blur-3xl border border-white/20 rounded-3xl p-5 overflow-hidden flex flex-col min-h-0">
                                    <button
                                        onClick={() => setKeywordsExpanded(!keywordsExpanded)}
                                        className="relative z-10 w-full flex items-center justify-between mb-3 flex-shrink-0"
                                    >
                                        <div className="flex items-center gap-3">
                                            <motion.div
                                                animate={{ scale: [1, 1.3, 1] }}
                                                transition={{ duration: 2, repeat: Infinity, delay: 0.3 }}
                                                className="w-2 h-2 bg-white rounded-full"
                                            />
                                            <h3 className="text-white tracking-widest text-xs uppercase">Requirements</h3>
                                            <span className="px-2 py-1 bg-white/20 text-white text-xs rounded-full backdrop-blur-sm">
                                                {interviewSession?.gaps.length || 0}
                                            </span>
                                        </div>
                                        <ChevronDown className={`h-5 w-5 text-gray-400 transition-transform ${keywordsExpanded ? '' : 'rotate-180'}`} />
                                    </button>

                                    <AnimatePresence>
                                        {keywordsExpanded && (
                                            <motion.ul
                                                initial={{ opacity: 0, height: 0 }}
                                                animate={{ opacity: 1, height: "auto" }}
                                                exit={{ opacity: 0, height: 0 }}
                                                transition={{ duration: 0.3 }}
                                                className="relative z-10 space-y-3 overflow-y-auto flex-1 min-h-0"
                                            >
                                                {interviewSession?.gaps.map((gap, index) => (
                                                    <motion.li
                                                        key={gap.keyword}
                                                        initial={{ opacity: 0, x: -20, scale: 0.9 }}
                                                        animate={{ opacity: 1, x: 0, scale: 1 }}
                                                        transition={{
                                                            delay: index * 0.08,
                                                            type: "spring",
                                                            stiffness: 300
                                                        }}
                                                        className="relative"
                                                    >
                                                        <div className="relative bg-gradient-to-r from-white/8 to-white/5 rounded-2xl p-4 border border-white/10 overflow-hidden">
                                                            <p className="text-white text-sm mb-2">{gap.keyword}</p>
                                                            <div className="flex items-center gap-2 mb-2">
                                                                <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                                                                    <motion.div
                                                                        className="h-full bg-gradient-to-r from-purple-500 to-blue-500"
                                                                        initial={{ width: 0 }}
                                                                        animate={{ width: `${gap.confidence * 100}%` }}
                                                                        transition={{ duration: 0.5 }}
                                                                    />
                                                                </div>
                                                                <span className="text-xs text-white tabular-nums">{Math.round(gap.confidence * 100)}%</span>
                                                            </div>
                                                            <p className="text-gray-400 text-xs">Priority: {Math.round(gap.weight * 100)}%</p>
                                                        </div>
                                                    </motion.li>
                                                ))}
                                            </motion.ul>
                                        )}
                                    </AnimatePresence>

                                    {/* Overall Progress */}
                                    {interviewSession && (
                                        <div className="mt-6 pt-6 border-t border-white/10">
                                            <div className="flex justify-between text-sm mb-2">
                                                <span className="text-gray-400">Overall Progress</span>
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

                                            <div className="mt-4 text-center">
                                                <button
                                                    onClick={handleSkipInterview}
                                                    className="text-xs text-gray-600 hover:text-gray-400 transition-colors duration-300 underline"
                                                >
                                                    skip interview
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
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
                            className="bg-black/90 border border-white/20 rounded-3xl p-8 max-w-lg w-full"
                        >
                            <div className="text-center">
                                <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <CheckCircle2 className="w-8 h-8 text-green-500" />
                                </div>
                                <h2 className="text-2xl font-medium mb-2">Interview Complete!</h2>
                                <p className="text-gray-400 mb-6">
                                    I've gathered all the information needed to create an amazing application.
                                </p>

                                <div className="bg-white/5 rounded-2xl p-4 mb-6 space-y-2">
                                    {interviewSession.gaps.map(gap => (
                                        <div key={gap.keyword} className="flex justify-between text-sm">
                                            <span className="text-gray-300">{gap.keyword}</span>
                                            <span className="text-green-400 font-medium tabular-nums">
                                                {Math.round(gap.confidence * 100)}%
                                            </span>
                                        </div>
                                    ))}
                                </div>

                                <button
                                    onClick={handleContinueToApplication}
                                    className="w-full h-12 bg-white text-black rounded-xl font-medium hover:bg-gray-200 transition flex items-center justify-center gap-2"
                                >
                                    Continue to Your Application <ArrowRight className="w-4 h-4" />
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
