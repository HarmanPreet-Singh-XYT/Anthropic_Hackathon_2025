"use client"

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles, Copy, CheckCircle, ArrowLeft, Mail, AlertCircle } from 'lucide-react';
import Link from 'next/link';

function OutreachContent() {
    const searchParams = useSearchParams();
    const sessionId = searchParams.get('session_id');

    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<{
        subject: string;
        body: string;
        contact_email?: string;
        contact_name?: string;
    } | null>(null);

    const [copiedSubject, setCopiedSubject] = useState(false);
    const [copiedBody, setCopiedBody] = useState(false);

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    useEffect(() => {
        if (!sessionId) {
            setIsLoading(false);
            return;
        }

        const generateDraft = async () => {
            try {
                const response = await fetch(`${API_URL}/api/outreach/generate`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ session_id: sessionId }),
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Failed to generate email');
                }

                const data = await response.json();
                setResult(data);
            } catch (err: any) {
                console.error('Error:', err);
                setError(err.message || "Failed to generate draft. Please ensure you have completed the analysis phase first.");
            } finally {
                setIsLoading(false);
            }
        };

        generateDraft();
    }, [sessionId, API_URL]);

    const copyToClipboard = (text: string, isSubject: boolean) => {
        navigator.clipboard.writeText(text);
        if (isSubject) {
            setCopiedSubject(true);
            setTimeout(() => setCopiedSubject(false), 2000);
        } else {
            setCopiedBody(true);
            setTimeout(() => setCopiedBody(false), 2000);
        }
    };

    const handleSendEmail = () => {
        if (!result) return;

        const recipient = result.contact_email || "scholarship@example.com";
        const subject = encodeURIComponent(result.subject);
        const body = encodeURIComponent(result.body);

        window.location.href = `mailto:${recipient}?subject=${subject}&body=${body}`;
    };

    if (!sessionId) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh] text-center p-8">
                <AlertCircle className="w-16 h-16 text-yellow-500 mb-4" />
                <h2 className="text-2xl font-bold mb-2">Session Required</h2>
                <p className="text-zinc-400 max-w-md mb-8">
                    Please start a scholarship analysis first to generate a targeted outreach email.
                </p>
                <Link href="/" className="bg-white text-black px-6 py-3 rounded-xl font-bold hover:bg-zinc-200 transition-colors">
                    Go to Home
                </Link>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto px-6 py-12">
            {/* Header */}
            <div className="mb-12">
                <Link href="/" className="inline-flex items-center gap-2 text-zinc-500 hover:text-white transition-colors mb-6 text-sm">
                    <ArrowLeft className="w-4 h-4" />
                    Back to Home
                </Link>

                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    <h1 className="text-4xl md:text-5xl font-medium tracking-tight mb-3 flex items-center gap-4">
                        <Mail className="w-10 h-10 text-blue-400" />
                        Scholarship Outreach
                    </h1>
                    <p className="text-zinc-400 text-lg font-light tracking-wide max-w-2xl">
                        AI-drafted inquiry based on your profile and the scholarship's hidden criteria.
                    </p>
                </motion.div>
            </div>

            {isLoading ? (
                <div className="flex flex-col items-center justify-center py-20">
                    <div className="w-16 h-16 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mb-6" />
                    <p className="text-zinc-400 animate-pulse">Analyzing scholarship data & drafting email...</p>
                </div>
            ) : error ? (
                <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-8 text-center">
                    <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-red-400 mb-2">Generation Failed</h3>
                    <p className="text-zinc-400 mb-6">{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="bg-red-500/20 hover:bg-red-500/30 text-red-400 px-6 py-2 rounded-lg transition-colors"
                    >
                        Try Again
                    </button>
                </div>
            ) : result ? (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-8"
                >
                    {/* Contact Info Badge */}
                    {result.contact_email && (
                        <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 px-4 py-2 rounded-full text-blue-400 text-sm">
                            <CheckCircle className="w-4 h-4" />
                            Target: {result.contact_name || "Committee"} ({result.contact_email})
                        </div>
                    )}

                    {/* Subject Line */}
                    <div className="bg-[#111111]/80 backdrop-blur-xl border border-white/10 rounded-xl p-4 relative group">
                        <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                                onClick={() => copyToClipboard(result.subject, true)}
                                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                            >
                                {copiedSubject ? <CheckCircle className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4 text-zinc-400" />}
                            </button>
                        </div>
                        <p className="text-xs text-zinc-500 uppercase tracking-wider mb-1">Subject</p>
                        <p className="text-white font-medium text-lg">{result.subject}</p>
                    </div>

                    {/* Email Body */}
                    <div className="bg-[#111111]/80 backdrop-blur-xl border border-white/10 rounded-xl p-8 relative group min-h-[300px]">
                        <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                                onClick={() => copyToClipboard(result.body, false)}
                                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                            >
                                {copiedBody ? <CheckCircle className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4 text-zinc-400" />}
                            </button>
                        </div>
                        <p className="text-xs text-zinc-500 uppercase tracking-wider mb-6">Email Body</p>
                        <div className="prose prose-invert max-w-none">
                            <p className="text-zinc-300 whitespace-pre-wrap leading-relaxed text-lg">
                                {result.body}
                            </p>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-col sm:flex-row gap-4 pt-4">
                        <button
                            onClick={handleSendEmail}
                            className="flex-1 bg-white text-black font-bold text-lg py-4 rounded-xl hover:bg-zinc-200 transition-colors flex items-center justify-center gap-3 shadow-lg shadow-white/10"
                        >
                            <Send className="w-5 h-5" />
                            Send Email
                        </button>
                        <button
                            onClick={() => copyToClipboard(`${result.subject}\n\n${result.body}`, false)}
                            className="flex-1 bg-[#111111] text-white border border-white/10 font-medium text-lg py-4 rounded-xl hover:bg-white/5 transition-colors flex items-center justify-center gap-3"
                        >
                            <Copy className="w-5 h-5" />
                            Copy All
                        </button>
                    </div>
                </motion.div>
            ) : null}
        </div>
    );
}

export default function OutreachPage() {
    return (
        <div className="min-h-screen bg-[#050505] text-white font-sans selection:bg-white/20 relative overflow-hidden">
            {/* Background Elements */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                <div className="absolute top-[-10%] right-[-10%] w-[600px] h-[600px] bg-blue-500/5 rounded-full blur-[150px]" />
                <div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-purple-500/5 rounded-full blur-[150px]" />
            </div>

            <div className="relative z-10">
                <Suspense fallback={
                    <div className="flex items-center justify-center min-h-screen">
                        <div className="w-8 h-8 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    </div>
                }>
                    <OutreachContent />
                </Suspense>
            </div>
        </div>
    );
}
