"use client"

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ArrowRight, CheckCircle2, AlertCircle, TrendingUp } from 'lucide-react';
import { useRouter } from 'next/navigation';

// --- Types ---
interface MatchComponent {
    name: string;
    score: number;
    weight: number;
}

interface MatchData {
    overall_score: number;
    status: 'strong_match' | 'good_match' | 'needs_improvement';
    components: MatchComponent[];
    gaps: string[];
}

// --- Mock Data ---
const MOCK_MATCH_DATA: MatchData = {
    overall_score: 0.75,
    status: 'strong_match',
    components: [
        { name: 'Leadership', score: 0.85, weight: 0.35 },
        { name: 'Academic Excellence', score: 0.90, weight: 0.25 },
        { name: 'Community Service', score: 0.60, weight: 0.25 },
        { name: 'Innovation', score: 0.70, weight: 0.15 },
    ],
    gaps: ['Community Service']
};

export default function MatchmakerPage() {
    const [matchData, setMatchData] = useState<MatchData | null>(null);
    const [animatedScore, setAnimatedScore] = useState(0);
    const router = useRouter();

    // Load match data on mount
    useEffect(() => {
        // Simulate loading delay
        setTimeout(() => {
            setMatchData(MOCK_MATCH_DATA);
        }, 300);
    }, []);

    // Animate overall score
    useEffect(() => {
        if (!matchData) return;

        const duration = 1500;
        const steps = 60;
        const increment = matchData.overall_score / steps;
        let current = 0;

        const interval = setInterval(() => {
            current += increment;
            if (current >= matchData.overall_score) {
                setAnimatedScore(matchData.overall_score);
                clearInterval(interval);
            } else {
                setAnimatedScore(current);
            }
        }, duration / steps);

        return () => clearInterval(interval);
    }, [matchData]);

    const getStatusConfig = (score: number) => {
        if (score >= 0.8) {
            return {
                text: 'Strong Match',
                color: 'text-green-400',
                bgColor: 'bg-green-500/20',
                borderColor: 'border-green-500/30',
                icon: CheckCircle2
            };
        } else if (score >= 0.6) {
            return {
                text: 'Good Match',
                color: 'text-yellow-400',
                bgColor: 'bg-yellow-500/20',
                borderColor: 'border-yellow-500/30',
                icon: TrendingUp
            };
        } else {
            return {
                text: 'Needs Improvement',
                color: 'text-red-400',
                bgColor: 'bg-red-500/20',
                borderColor: 'border-red-500/30',
                icon: AlertCircle
            };
        }
    };

    const getComponentColor = (score: number) => {
        if (score >= 0.8) return 'bg-green-500';
        if (score >= 0.6) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    const getComponentDotColor = (score: number) => {
        if (score >= 0.8) return 'bg-green-500';
        if (score >= 0.6) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    if (!matchData) {
        return (
            <div className="min-h-screen bg-[#050505] text-white flex items-center justify-center">
                <div className="text-center">
                    <div className="w-12 h-12 border-4 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4" />
                    <p className="text-zinc-500">Analyzing your match...</p>
                </div>
            </div>
        );
    }

    const statusConfig = getStatusConfig(matchData.overall_score);
    const StatusIcon = statusConfig.icon;

    return (
        <div className="min-h-screen bg-[#050505] text-white font-sans selection:bg-white/20 overflow-hidden relative flex flex-col items-center justify-center">

            {/* Background Stars/Particles */}
            <div className="absolute inset-0 z-0 pointer-events-none">
                {[...Array(20)].map((_, i) => (
                    <div
                        key={i}
                        className="absolute rounded-full bg-white opacity-20 animate-pulse"
                        style={{
                            top: `${Math.random() * 100}%`,
                            left: `${Math.random() * 100}%`,
                            width: `${Math.random() * 3 + 1}px`,
                            height: `${Math.random() * 3 + 1}px`,
                            animationDuration: `${Math.random() * 3 + 2}s`,
                            animationDelay: `${Math.random() * 2}s`
                        }}
                    />
                ))}

                {/* Subtle Glows */}
                <div className="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-[150px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-[150px]" />
            </div>

            <div className="relative z-10 w-full max-w-3xl px-6 flex flex-col items-center">

                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="text-center mb-12"
                >
                    <div className="inline-flex items-center justify-center mb-6">
                        <Sparkles className="w-12 h-12 text-white fill-white" />
                    </div>
                    <h1 className="text-5xl md:text-6xl font-medium tracking-tight mb-4">
                        Your Application Match
                    </h1>
                    <p className="text-zinc-500 text-lg font-light tracking-wide">
                        Ready to impress
                    </p>
                </motion.div>

                {/* Main Card */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
                    className="w-full bg-[#111111]/80 backdrop-blur-2xl border border-white/10 rounded-[32px] p-8 md:p-10 shadow-2xl shadow-black/50 relative overflow-hidden"
                >
                    {/* Inner Glow */}
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-1 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-50" />

                    <div className="space-y-10">

                        {/* Overall Score Section */}
                        <div className="text-center space-y-6">
                            {/* Circular Progress */}
                            <div className="relative inline-flex items-center justify-center">
                                {/* Background Circle */}
                                <svg className="w-48 h-48 transform -rotate-90">
                                    <circle
                                        cx="96"
                                        cy="96"
                                        r="88"
                                        stroke="currentColor"
                                        strokeWidth="8"
                                        fill="none"
                                        className="text-white/10"
                                    />
                                    {/* Progress Circle */}
                                    <motion.circle
                                        cx="96"
                                        cy="96"
                                        r="88"
                                        stroke="currentColor"
                                        strokeWidth="8"
                                        fill="none"
                                        strokeLinecap="round"
                                        className={statusConfig.color}
                                        initial={{ strokeDasharray: "0 552" }}
                                        animate={{ strokeDasharray: `${animatedScore * 552} 552` }}
                                        transition={{ duration: 1.5, ease: "easeOut" }}
                                    />
                                </svg>

                                {/* Center Text */}
                                <div className="absolute inset-0 flex flex-col items-center justify-center">
                                    <div className="text-6xl font-bold tracking-tight">
                                        {Math.round(animatedScore * 100)}%
                                    </div>
                                    <div className="text-sm text-zinc-500 mt-1">Match Score</div>
                                </div>
                            </div>

                            {/* Status Badge */}
                            <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${statusConfig.bgColor} border ${statusConfig.borderColor}`}>
                                <StatusIcon className={`w-4 h-4 ${statusConfig.color}`} />
                                <span className={`text-sm font-medium ${statusConfig.color}`}>
                                    {statusConfig.text}
                                </span>
                            </div>
                        </div>

                        {/* Divider */}
                        <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

                        {/* Component Breakdown */}
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 text-xs font-bold tracking-widest text-zinc-400 uppercase">
                                <div className="w-2 h-2 rounded-full bg-white" />
                                Component Alignment
                            </div>

                            <div className="space-y-4">
                                {matchData.components.map((component, index) => (
                                    <motion.div
                                        key={component.name}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                                        className="space-y-2"
                                    >
                                        {/* Component Header */}
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <div className={`w-2 h-2 rounded-full ${getComponentDotColor(component.score)}`} />
                                                <span className="text-zinc-200 font-medium">{component.name}</span>
                                                <span className="text-xs text-zinc-500">
                                                    (weight: {Math.round(component.weight * 100)}%)
                                                </span>
                                            </div>
                                            <span className="text-zinc-400 font-medium tabular-nums">
                                                {Math.round(component.score * 100)}%
                                            </span>
                                        </div>

                                        {/* Progress Bar */}
                                        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                            <motion.div
                                                className={`h-full ${getComponentColor(component.score)} rounded-full`}
                                                initial={{ width: 0 }}
                                                animate={{ width: `${component.score * 100}%` }}
                                                transition={{ duration: 1, delay: 0.7 + index * 0.1, ease: "easeOut" }}
                                            />
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </div>

                        {/* Gaps Alert (if any) */}
                        {matchData.gaps.length > 0 && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 1.2 }}
                                className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-xl flex items-start gap-3"
                            >
                                <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                                <div className="flex-1">
                                    <p className="text-sm text-yellow-200 font-medium mb-1">
                                        Areas for Improvement
                                    </p>
                                    <p className="text-xs text-yellow-300/70">
                                        {matchData.gaps.join(', ')} could be strengthened in your application.
                                        Our AI will help you address these gaps.
                                    </p>
                                </div>
                            </motion.div>
                        )}

                        {/* Action Button */}
                        <motion.button
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 1.4 }}
                            onClick={() => router.push('/ai-help')}
                            className="w-full h-16 rounded-xl font-medium text-lg flex items-center justify-center gap-2 bg-white text-black hover:bg-zinc-200 hover:scale-[1.01] active:scale-[0.99] shadow-lg shadow-white/10 transition-all duration-300"
                        >
                            Continue to AI Help <ArrowRight className="w-5 h-5" />
                        </motion.button>

                    </div>
                </motion.div>
            </div>
        </div>
    );
}
