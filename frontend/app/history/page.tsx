"use client"

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { FileText, Calendar, Award, ArrowRight, Loader2, AlertCircle } from 'lucide-react';
import { ParticleBackground } from '@/components/ParticleBackground';

interface Application {
    workflow_session_id: string;
    scholarship_url: string;
    status: string;
    created_at: string;
    match_score?: number;
    had_interview: boolean;
}

export default function HistoryPage() {
    const [applications, setApplications] = useState<Application[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const resumeSessionId = localStorage.getItem('resume_session_id');

                if (!resumeSessionId) {
                    setError('No resume session found');
                    setLoading(false);
                    return;
                }

                const response = await fetch(`${API_URL}/api/applications/history/${resumeSessionId}`);

                if (!response.ok) {
                    throw new Error('Failed to fetch application history');
                }

                const data = await response.json();
                setApplications(data.applications || []);
            } catch (err) {
                console.error('Error fetching history:', err);
                setError(err instanceof Error ? err.message : 'Failed to load history');
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, [API_URL]);

    const formatDate = (isoString: string) => {
        try {
            const date = new Date(isoString);
            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch {
            return 'Unknown date';
        }
    };

    const getMatchColor = (score?: number) => {
        if (!score) return 'text-gray-400';
        if (score >= 0.8) return 'text-green-400';
        if (score >= 0.6) return 'text-yellow-400';
        return 'text-orange-400';
    };

    return (
        <div className="min-h-screen bg-black text-white font-sans selection:bg-white/20 overflow-hidden relative">
            <ParticleBackground />

            <div className="relative z-10 max-w-5xl mx-auto px-6 py-12">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-12"
                >
                    <h1 className="text-5xl font-light tracking-tight mb-3">
                        Application History
                    </h1>
                    <p className="text-gray-400">Track all your scholarship applications</p>
                </motion.div>

                {/* Content */}
                {loading ? (
                    <div className="flex items-center justify-center py-20">
                        <Loader2 className="w-8 h-8 animate-spin text-white/50" />
                    </div>
                ) : error ? (
                    <div className="flex flex-col items-center justify-center py-20 text-center">
                        <AlertCircle className="w-16 h-16 text-red-400 mb-4" />
                        <p className="text-red-300 mb-4">{error}</p>
                        <button
                            onClick={() => router.push('/start')}
                            className="px-6 py-3 bg-white/10 hover:bg-white/20 rounded-xl transition-colors"
                        >
                            Go to Start Page
                        </button>
                    </div>
                ) : applications.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20 text-center">
                        <FileText className="w-16 h-16 text-gray-600 mb-4" />
                        <p className="text-gray-400 mb-6">No applications yet</p>
                        <button
                            onClick={() => router.push('/start')}
                            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 rounded-xl transition-all"
                        >
                            Submit Your First Application
                        </button>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {applications.map((app, index) => (
                            <motion.div
                                key={app.workflow_session_id}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.1 }}
                                className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all cursor-pointer"
                                onClick={() => router.push(`/application?session=${app.workflow_session_id}`)}
                            >
                                <div className="flex items-start justify-between gap-4 flex-wrap">
                                    <div className="flex-1 min-w-[200px]">
                                        <h3 className="text-lg font-medium mb-2 line-clamp-2">
                                            {new URL(app.scholarship_url).hostname}
                                        </h3>
                                        <p className="text-sm text-gray-400 mb-3 truncate">
                                            {app.scholarship_url}
                                        </p>
                                        <div className="flex items-center gap-4 flex-wrap text-sm">
                                            <div className="flex items-center gap-2">
                                                <Calendar className="w-4 h-4 text-gray-500" />
                                                <span className="text-gray-400">{formatDate(app.created_at)}</span>
                                            </div>
                                            {app.match_score !== undefined && (
                                                <div className="flex items-center gap-2">
                                                    <Award className={`w-4 h-4 ${getMatchColor(app.match_score)}`} />
                                                    <span className={getMatchColor(app.match_score)}>
                                                        {Math.round(app.match_score * 100)}% Match
                                                    </span>
                                                </div>
                                            )}
                                            {app.had_interview && (
                                                <span className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded-full">
                                                    Interviewed
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    <ArrowRight className="w-5 h-5 text-gray-500 flex-shrink-0 mt-2" />
                                </div>
                            </motion.div>
                        ))}

                        {/* New Application Button */}
                        <motion.button
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: applications.length * 0.1 + 0.2 }}
                            onClick={() => {
                                const resumeSessionId = localStorage.getItem('resume_session_id');
                                router.push(`/start?resume_session=${resumeSessionId}`);
                            }}
                            className="w-full py-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 rounded-xl font-medium transition-all hover:scale-[1.02] active:scale-[0.98]"
                        >
                            + Submit Another Application
                        </motion.button>
                    </div>
                )}
            </div>
        </div>
    );
}
