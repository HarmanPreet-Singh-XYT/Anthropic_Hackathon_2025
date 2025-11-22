"use client"

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ArrowRight, CheckCircle2, AlertCircle, TrendingUp } from 'lucide-react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ParticleBackground } from '@/components/ParticleBackground';

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
// --- Mock Data Removed ---

export default function MatchmakerPage() {
    const [matchData, setMatchData] = useState<MatchData | null>(null);
    const [animatedScore, setAnimatedScore] = useState(0);
    const router = useRouter();

    // Load match data on mount
    const searchParams = useSearchParams();
    const session_id = searchParams.get('session');
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // Load match data on mount
    useEffect(() => {
        if (!session_id) return;

        const fetchData = async () => {
            try {
                console.log("Fetching status for:", session_id);
                const response = await fetch(`${API_URL}/api/workflow/status/${session_id}`);
                if (!response.ok) throw new Error("Failed to fetch data");

                const data = await response.json();
                console.log("Status data:", data);

                // Handle both "complete" and "waiting_for_input" statuses
                if ((data.status === "complete" || data.status === "waiting_for_input") && data.result && data.result.matchmaker_results) {
                    console.log("[Matchmaker] Results received:", data.result.matchmaker_results);
                    const results = data.result.matchmaker_results;

                    // Map backend data to frontend structure
                    const components: MatchComponent[] = Object.entries(results.weighted_values || {}).map(([name, weight]) => {
                        // Find score for this component if available in keyword_match_details
                        const detail = results.keyword_match_details?.[name];
                        const score = detail ? detail.best_match_score : 0;

                        return {
                            name: name,
                            score: score,
                            weight: Number(weight)
                        };
                    });

                    // Set match data
                    console.log("[Matchmaker] Setting match data with components:", components);
                    setMatchData({
                        overall_score: results.match_score || 0,
                        status: (results.match_score || 0) >= 0.8 ? 'strong_match' : (results.match_score || 0) >= 0.6 ? 'good_match' : 'needs_improvement',
                        components: components,
                        gaps: results.gaps || []
                    });
                } else if (data.status === "processing") {
                    console.log("[Matchmaker] Still processing...");
                    // Still processing, poll again
                    setTimeout(fetchData, 2000);
                } else {
                    console.warn("[Matchmaker] Unexpected status or missing data:", data);
                }
            } catch (e) {
                console.error("Error fetching match data:", e);
            }
        };

        fetchData();
    }, [session_id]);

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
        <div className="h-screen bg-black text-white font-sans selection:bg-white/20 overflow-hidden relative flex flex-col items-center justify-center">

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

            <div className="relative z-10 w-full max-w-3xl px-6 flex flex-col items-center py-4">

                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="text-center mb-6"
                >
                    <div className="inline-flex items-center justify-center mb-3">
                        <Sparkles className="w-10 h-10 text-white fill-white" />
                    </div>
                    <h1 className="text-4xl md:text-5xl font-medium tracking-tight mb-2">
                        Your Application Match
                    </h1>
                    <p className="text-zinc-500 text-base font-light tracking-wide">
                        Ready to impress
                    </p>
                </motion.div>

                {/* Main Card */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
                    className="w-full bg-[#111111]/80 backdrop-blur-2xl border border-white/10 rounded-[24px] p-6 md:p-8 shadow-2xl shadow-black/50 relative overflow-hidden"
                >
                    {/* Inner Glow */}
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-1 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-50" />

                    <div className="space-y-6">

                        {/* Overall Score Section */}
                        <div className="flex items-center justify-center gap-8">
                            {/* Circular Progress */}
                            <div className="relative inline-flex items-center justify-center">
                                {/* Background Circle */}
                                <svg className="w-36 h-36 transform -rotate-90">
                                    <circle
                                        cx="72"
                                        cy="72"
                                        r="66"
                                        stroke="currentColor"
                                        strokeWidth="6"
                                        fill="none"
                                        className="text-white/10"
                                    />
                                    {/* Progress Circle */}
                                    <motion.circle
                                        cx="72"
                                        cy="72"
                                        r="66"
                                        stroke="currentColor"
                                        strokeWidth="6"
                                        fill="none"
                                        strokeLinecap="round"
                                        className={statusConfig.color}
                                        initial={{ strokeDasharray: "0 414" }}
                                        animate={{ strokeDasharray: `${animatedScore * 414} 414` }}
                                        transition={{ duration: 1.5, ease: "easeOut" }}
                                    />
                                </svg>

                                {/* Center Text */}
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="text-5xl font-bold tracking-tight">
                                        {Math.round(animatedScore * 100)}%
                                    </div>
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
                        <div className="space-y-3">
                            <div className="flex items-center gap-2 text-xs font-bold tracking-widest text-zinc-400 uppercase">
                                <div className="w-2 h-2 rounded-full bg-white" />
                                Component Alignment
                            </div>

                            <div className="space-y-3">
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
                                                {isNaN(component.score) ? '0' : Math.round(component.score * 100)}%
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

                        {/* Action Button */}
                        <motion.button
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 1.4 }}
                            onClick={() => {
                                if (matchData.gaps.length === 0) {
                                    // No gaps, skip interview and go to application
                                    // We need to trigger resume with empty story first
                                    const resumeWorkflow = async () => {
                                        try {
                                            const formData = new FormData();
                                            formData.append('session_id', session_id!);
                                            formData.append('bridge_story', '');
                                            await fetch(`${API_URL}/api/workflow/resume`, { method: 'POST', body: formData });
                                            router.push(`/application?session=${session_id}`);
                                        } catch (e) {
                                            console.error("Error resuming workflow:", e);
                                            router.push(`/application?session=${session_id}`);
                                        }
                                    };
                                    resumeWorkflow();
                                } else {
                                    router.push(`/ai-help?session=${session_id}`);
                                }
                            }}
                            className="w-full h-12 rounded-xl font-medium text-base flex items-center justify-center gap-2 bg-white text-black hover:bg-zinc-200 hover:scale-[1.01] active:scale-[0.99] shadow-lg shadow-white/10 transition-all duration-300"
                        >
                            {matchData.gaps.length === 0 ? (
                                <>Continue to Application <ArrowRight className="w-4 h-4" /></>
                            ) : (
                                <>Continue to AI Help <ArrowRight className="w-4 h-4" /></>
                            )}
                        </motion.button>

                    </div>
                </motion.div>
            </div>
        </div>
    );
}
