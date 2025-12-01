"use client"

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Link2, Zap, ArrowRight, FileText, X, Loader2, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import { useRouter, useSearchParams } from 'next/navigation';
import { ParticleBackground } from '@/components/ParticleBackground';
import { uploadResume, startWorkflow, getWorkflowStatus } from '@/lib/api';
import { useAuthClient } from '@/hooks/useAuthClient'; // or wherever you place it
import { ProtectedRoute } from '@/components/ProtectedRoute';

export default function StartPage() {
    const [file, setFile] = useState<File | null>(null);
    const [url, setUrl] = useState<string>('');
    const [isDragging, setIsDragging] = useState<boolean>(false);
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<{ message: string; chunks: number } | null>(null);
    const [progress, setProgress] = useState<number>(0);
    const [progressStatus, setProgressStatus] = useState<string>('');

    // New state for resume session detection
    const [existingResumeSession, setExistingResumeSession] = useState<{
        session_id: string;
        chunks_count: number;
        valid: boolean;
    } | null>(null);
    const [useExistingResume, setUseExistingResume] = useState<boolean>(false);
    const [checkingSession, setCheckingSession] = useState<boolean>(true);

    // Use the client-side auth hook
    const { user, isLoading: isAuthLoading } = useAuthClient();

    const router = useRouter();
    const searchParams = useSearchParams();

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // Check for existing resume session on mount
    useEffect(() => {
        const checkExistingSession = async () => {
            try {
                // Check URL params first, then localStorage
                const urlResumeSession = searchParams.get('resume_session');
                const storedResumeSession = localStorage.getItem('resume_session_id');
                const resumeSessionId = urlResumeSession || storedResumeSession;

                if (!resumeSessionId) {
                    setCheckingSession(false);
                    return;
                }

                console.log('[StartPage] Checking for existing resume session:', resumeSessionId);

                // Validate the session with backend
                const response = await fetch(`${API_URL}/api/resume/session/${resumeSessionId}/validate`);

                if (!response.ok) {
                    console.log('[StartPage] Failed to validate session');
                    localStorage.removeItem('resume_session_id');
                    setCheckingSession(false);
                    return;
                }

                const data = await response.json();

                if (data.valid) {
                    console.log(`[StartPage] Found valid resume session with ${data.chunks_count} chunks`);
                    setExistingResumeSession({
                        session_id: data.session_id,
                        chunks_count: data.chunks_count,
                        valid: data.valid
                    });
                    setUseExistingResume(true);
                } else {
                    console.log('[StartPage] Resume session invalid, removing from storage');
                    localStorage.removeItem('resume_session_id');
                }
            } catch (err) {
                console.error('[StartPage] Error checking existing session:', err);
                localStorage.removeItem('resume_session_id');
            } finally {
                setCheckingSession(false);
            }
        };

        checkExistingSession();
    }, [searchParams, API_URL]);


    // Drag & Drop Handlers
    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) validateAndSetFile(droppedFile);
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) validateAndSetFile(selectedFile);
    };

    const validateAndSetFile = (f: File) => {
        setError(null);
        setSuccess(null);

        if (!f.name.toLowerCase().endsWith('.pdf')) {
            setError("Only PDF files are supported");
            return;
        }

        if (f.size > 5 * 1024 * 1024) {
            setError("File is too large. Max 5MB.");
            return;
        }

        if (f.size === 0) {
            setError("File is empty");
            return;
        }

        setFile(f);
    };

    const removeFile = (e: React.MouseEvent) => {
        e.stopPropagation();
        setFile(null);
        setError(null);
        setSuccess(null);
    };

    const handleSubmit = async () => {
        // Check authentication first
        if (!user || !user.sub) {
            setError('Please sign in to continue');
            // Trigger sign-in
            const { triggerSignIn } = await import('@/app/auth-actions');
            await triggerSignIn();
            return;
        }

        // Allow submission with only URL if using existing resume
        if (!useExistingResume && !file) return;
        if (!url) return;

        setIsSubmitting(true);
        setError(null);
        setSuccess(null);
        setProgress(0);
        setProgressStatus('Preparing your application...');

        try {
            let resumeSessionId: string;

            // Step 1: Handle resume - either upload new or use existing
            if (useExistingResume && existingResumeSession) {
                // Use existing resume session
                console.log("[StartPage] Using existing resume session:", existingResumeSession.session_id);
                resumeSessionId = existingResumeSession.session_id;
                setProgress(20);
                setProgressStatus('Using your existing resume...');
            } else if (file) {
                // Upload new resume
                console.log("[StartPage] Step 1: Uploading resume...");
                setProgress(10);
                setProgressStatus('Uploading your resume...');

                const uploadFormData = new FormData();
                uploadFormData.append('file', file);

                const uploadData = await uploadResume(file, user.sub);
                resumeSessionId = uploadData.metadata.session_id;

                console.log("[StartPage] Resume uploaded, session_id:", resumeSessionId);
                console.log(`[StartPage] Stored ${uploadData.chunks_stored} chunks`);

                // Store session_id for potential later use
                localStorage.setItem('resume_session_id', resumeSessionId);
                setProgress(20);
                setProgressStatus('Resume uploaded successfully!');
            } else {
                throw new Error('Resume file is required');
            }

            // Step 2: Start workflow with resume session_id
            console.log("[StartPage] Step 2: Starting workflow...");
            setProgress(30);
            setProgressStatus('Analyzing scholarship requirements...');

            const workflowFormData = new FormData();
            workflowFormData.append('scholarship_url', url);
            workflowFormData.append('resume_session_id', resumeSessionId);

            const { session_id: workflowSessionId } = await startWorkflow(url, resumeSessionId, user.sub);
            console.log("[StartPage] Workflow started");
            console.log(`  Resume session: ${resumeSessionId}`);
            console.log(`  Workflow session: ${workflowSessionId}`);

            setProgress(40);
            setProgressStatus('Extracting scholarship data...');

            // Step 3: Poll for completion
            let completed = false;
            let pollCount = 0;
            const maxPolls = 60;

            while (!completed && pollCount < maxPolls) {
                await new Promise(resolve => setTimeout(resolve, 2000));
                pollCount++;

                // Update progress during polling (40-90%)
                const pollingProgress = 40 + Math.min(50, (pollCount / maxPolls) * 50);
                setProgress(pollingProgress);

                if (pollCount < 10) {
                    setProgressStatus('Analyzing your qualifications...');
                } else if (pollCount < 20) {
                    setProgressStatus('Matching your profile with scholarship criteria...');
                } else if (pollCount < 30) {
                    setProgressStatus('Evaluating your fit...');
                } else {
                    setProgressStatus('Finalizing analysis...');
                }

                const statusData = await getWorkflowStatus(workflowSessionId, user.sub);
                console.log(`[StartPage] Poll #${pollCount}:`, statusData.status);

                if (statusData.status === 'processing') {
                    continue;
                } else if (statusData.status === 'complete' || statusData.status === 'waiting_for_input') {
                    console.log("[StartPage] Workflow reached target state:", statusData.status);
                    completed = true;
                    setProgress(100);
                    setProgressStatus('Analysis complete!');
                    setSuccess({
                        message: "Analysis complete!",
                        chunks: 0
                    });

                    console.log("[StartPage] Navigating to matchmaker...");
                    await new Promise(resolve => setTimeout(resolve, 800));
                    router.push(`/matchmaker?session=${workflowSessionId}`);

                } else if (statusData.status === 'error') {
                    console.error("[StartPage] Workflow error:", statusData.error);
                    throw new Error(statusData.error || 'Workflow failed');
                }
            }

            if (!completed) {
                throw new Error("Workflow timed out after 2 minutes");
            }

        } catch (err) {
            console.error("Workflow error:", err);
            setError(err instanceof Error ? err.message : "Failed to process. Please try again.");
            setProgress(0);
            setProgressStatus('');
        } finally {
            setIsSubmitting(false);
        }
    };

    // Show loading state while auth is being checked
    if (isAuthLoading) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-white animate-spin" />
            </div>
        );
    }

    // Allow access to the page regardless of auth status
    // Auth will be checked on submit
    return (
        <div className="min-h-screen bg-black text-white font-sans selection:bg-white/20 overflow-hidden relative flex flex-col items-center justify-center">

            <ParticleBackground />

            {/* Exit Button for Authenticated Users */}
            {user && (
                <button
                    onClick={() => router.push('/dashboard')}
                    className="absolute top-6 left-6 z-50 p-2 bg-white/10 hover:bg-white/20 rounded-full text-white/50 hover:text-white transition-all backdrop-blur-sm group flex items-center gap-2 pr-4"
                >
                    <div className="bg-white/10 p-1 rounded-full group-hover:bg-white/20">
                        <X className="w-4 h-4" />
                    </div>
                    <span className="text-xs font-bold uppercase tracking-wider">Exit</span>
                </button>
            )}

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

            {/* Show loading state while checking authentication */}
            {checkingSession ? (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="relative z-10 flex flex-col items-center gap-4"
                >
                    <Loader2 className="w-12 h-12 text-white animate-spin" />
                    <p className="text-gray-400 text-lg">Loading session...</p>
                </motion.div>
            ) : (
                <AnimatePresence mode="wait">
                    {isSubmitting ? (
                        <motion.div
                            key="progress"
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            className="relative z-10 w-full max-w-[700px] px-6 flex flex-col items-center justify-center space-y-8"
                        >
                            {/* Status Text */}
                            <motion.div
                                className="text-center space-y-4"
                                initial={{ opacity: 0, y: -20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 }}
                            >
                                <motion.h2
                                    className="text-4xl font-light tracking-tight"
                                    style={{
                                        textShadow: '0 0 60px rgba(255,255,255,0.3)',
                                    }}
                                    animate={{
                                        textShadow: [
                                            '0 0 60px rgba(255,255,255,0.3)',
                                            '0 0 80px rgba(255,255,255,0.5)',
                                            '0 0 60px rgba(255,255,255,0.3)',
                                        ]
                                    }}
                                    transition={{ duration: 2, repeat: Infinity }}
                                >
                                    {progressStatus}
                                </motion.h2>
                                <p className="text-gray-400 text-lg">
                                    This may take a moment...
                                </p>
                            </motion.div>

                            {/* Progress Bar Container */}
                            <motion.div
                                className="w-full space-y-4"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.3 }}
                            >
                                {/* Progress percentage */}
                                <div className="flex justify-between items-center text-sm">
                                    <span className="text-gray-400">Progress</span>
                                    <motion.span
                                        className="text-white font-medium"
                                        key={Math.floor(progress)}
                                        initial={{ scale: 1.2 }}
                                        animate={{ scale: 1 }}
                                    >
                                        {Math.floor(progress)}%
                                    </motion.span>
                                </div>

                                {/* Progress bar */}
                                <div className="relative h-4 bg-white/10 rounded-full overflow-hidden backdrop-blur-sm border border-white/20">
                                    {/* Animated background shimmer */}
                                    <motion.div
                                        className="absolute inset-0 opacity-30"
                                        style={{
                                            background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
                                        }}
                                        animate={{
                                            x: ['-100%', '200%'],
                                        }}
                                        transition={{
                                            duration: 2,
                                            repeat: Infinity,
                                            ease: 'linear',
                                        }}
                                    />

                                    {/* Progress fill */}
                                    <motion.div
                                        className="h-full bg-gradient-to-r from-white/90 to-white rounded-full relative overflow-hidden"
                                        initial={{ width: '0%' }}
                                        animate={{ width: `${progress}%` }}
                                        transition={{ duration: 0.5, ease: 'easeOut' }}
                                        style={{
                                            boxShadow: '0 0 20px rgba(255,255,255,0.5)',
                                        }}
                                    >
                                        {/* Shine effect on progress bar */}
                                        <motion.div
                                            className="absolute inset-0"
                                            style={{
                                                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent)',
                                            }}
                                            animate={{
                                                x: ['-100%', '200%'],
                                            }}
                                            transition={{
                                                duration: 1.5,
                                                repeat: Infinity,
                                                ease: 'linear',
                                            }}
                                        />
                                    </motion.div>
                                </div>
                            </motion.div>

                            {/* Animated dots */}
                            <motion.div
                                className="flex gap-2"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                transition={{ delay: 0.5 }}
                            >
                                {[0, 1, 2].map((i) => (
                                    <motion.div
                                        key={i}
                                        className="w-2 h-2 bg-white rounded-full"
                                        animate={{
                                            scale: [1, 1.5, 1],
                                            opacity: [0.3, 1, 0.3],
                                        }}
                                        transition={{
                                            duration: 1.5,
                                            repeat: Infinity,
                                            delay: i * 0.2,
                                        }}
                                    />
                                ))}
                            </motion.div>
                        </motion.div>
                    ) : (
                        <div className="relative z-10 w-full max-w-[620px] px-6 flex flex-col items-center" key="form">

                            {/* Header */}
                            <motion.div
                                initial={{ opacity: 0, y: 30 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1, type: "spring", stiffness: 100 }}
                                className="text-center space-y-4 mb-8"
                            >
                                {/* Animated icon container */}
                                <div className="relative inline-block">
                                    <motion.div
                                        animate={{
                                            rotate: 360,
                                            scale: [1, 1.2, 1],
                                        }}
                                        transition={{
                                            rotate: { duration: 20, repeat: Infinity, ease: "linear" },
                                            scale: { duration: 2, repeat: Infinity, ease: "easeInOut" }
                                        }}
                                        className="absolute inset-0 bg-gradient-to-r from-white/20 via-transparent to-white/20 rounded-full blur-2xl"
                                    />
                                    <motion.div
                                        animate={{
                                            y: [0, -15, 0],
                                            rotate: [0, 10, -10, 0],
                                        }}
                                        transition={{ duration: 4, repeat: Infinity }}
                                        className="relative"
                                    >
                                        <Zap className="h-16 w-16 text-white mx-auto drop-shadow-2xl" fill="white" strokeWidth={1} />
                                    </motion.div>
                                </div>

                                {/* Glowing title */}
                                <div className="relative">
                                    <motion.h1
                                        className="text-white tracking-tight relative"
                                        style={{
                                            fontSize: '2.75rem',
                                            fontWeight: 200,
                                            letterSpacing: '-0.03em',
                                            textShadow: '0 0 60px rgba(255,255,255,0.3)',
                                        }}
                                        animate={{
                                            textShadow: [
                                                '0 0 60px rgba(255,255,255,0.3)',
                                                '0 0 80px rgba(255,255,255,0.5)',
                                                '0 0 60px rgba(255,255,255,0.3)',
                                            ]
                                        }}
                                        transition={{ duration: 2, repeat: Infinity }}
                                    >
                                        Scholarship Assistant
                                    </motion.h1>
                                </div>
                                <motion.p
                                    className="text-gray-400"
                                    animate={{ opacity: [0.6, 1, 0.6] }}
                                    transition={{ duration: 3, repeat: Infinity }}
                                >
                                    Transform your application into success
                                </motion.p>
                            </motion.div>

                            {/* Main Card with 3D effect */}
                            <motion.div
                                initial={{ opacity: 0, y: 50, rotateX: 20 }}
                                animate={{ opacity: 1, y: 0, rotateX: 0 }}
                                transition={{ delay: 0.3, type: "spring", stiffness: 100 }}
                                whileHover={{
                                    y: -5,
                                    transition: { type: "spring", stiffness: 400 }
                                }}
                                className="relative w-full"
                                style={{ perspective: 1000 }}
                            >
                                {/* Rotating gradient border */}
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                                    className="absolute -inset-[2px] rounded-3xl opacity-70"
                                    style={{
                                        background: 'linear-gradient(45deg, rgba(255,255,255,0.3), transparent, rgba(255,255,255,0.3), transparent)',
                                    }}
                                />

                                {/* Glowing background layer */}
                                <motion.div
                                    animate={{
                                        boxShadow: [
                                            '0 0 40px rgba(255,255,255,0.1)',
                                            '0 0 80px rgba(255,255,255,0.2)',
                                            '0 0 40px rgba(255,255,255,0.1)',
                                        ]
                                    }}
                                    transition={{ duration: 3, repeat: Infinity }}
                                    className="absolute inset-0 rounded-3xl"
                                />

                                <div className="relative bg-black/70 backdrop-blur-3xl border border-white/20 rounded-3xl p-8 space-y-6">

                                    {/* Resume Upload */}
                                    <div className="space-y-3">
                                        <div className="flex items-center gap-2 text-xs font-bold tracking-widest text-gray-400 uppercase">
                                            <motion.div
                                                animate={{ scale: [1, 1.3, 1] }}
                                                transition={{ duration: 2, repeat: Infinity }}
                                                className="w-2 h-2 bg-white rounded-full"
                                            />
                                            Resume Upload
                                        </div>

                                        <div
                                            onClick={() => document.getElementById('file-upload')?.click()}
                                            onDragOver={handleDragOver}
                                            onDragLeave={handleDragLeave}
                                            onDrop={handleDrop}
                                            className={`
                                                    relative h-48 rounded-2xl border transition-all duration-300 cursor-pointer
                                                    flex flex-col items-center justify-center text-center
                                                    ${isDragging
                                                    ? 'border-white/40 bg-white/10 scale-[1.02]'
                                                    : 'border-white/20 bg-white/5 hover:bg-white/10 hover:border-white/30'
                                                }
                                                `}
                                        >
                                            <input
                                                id="file-upload"
                                                type="file"
                                                className="hidden"
                                                accept=".pdf"
                                                onChange={handleFileSelect}
                                            />

                                            <AnimatePresence mode="wait">
                                                {!file ? (
                                                    <motion.div
                                                        key="empty"
                                                        initial={{ opacity: 0 }}
                                                        animate={{ opacity: 1 }}
                                                        exit={{ opacity: 0 }}
                                                        className="flex flex-col items-center gap-4"
                                                    >
                                                        <motion.div
                                                            whileHover={{ scale: 1.1 }}
                                                            className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center"
                                                        >
                                                            <Upload className="w-6 h-6 text-white" />
                                                        </motion.div>
                                                        <div className="space-y-1">
                                                            <p className="text-lg font-medium text-white">
                                                                Drop your resume here
                                                            </p>
                                                            <p className="text-sm text-gray-400">
                                                                PDF files only
                                                            </p>
                                                        </div>
                                                    </motion.div>
                                                ) : (
                                                    <motion.div
                                                        key="file"
                                                        initial={{ opacity: 0, scale: 0.9 }}
                                                        animate={{ opacity: 1, scale: 1 }}
                                                        exit={{ opacity: 0, scale: 0.9 }}
                                                        className="flex flex-col items-center gap-3 z-10"
                                                    >
                                                        <div className="w-14 h-14 rounded-2xl bg-white text-black flex items-center justify-center shadow-lg">
                                                            <FileText className="w-7 h-7" />
                                                        </div>
                                                        <div className="text-center">
                                                            <p className="text-white font-medium truncate max-w-[200px]">{file.name}</p>
                                                            <p className="text-xs text-gray-400">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                                        </div>
                                                        <button
                                                            onClick={removeFile}
                                                            className="mt-2 px-3 py-1.5 bg-white/10 hover:bg-white/20 rounded-full text-xs font-medium text-gray-300 transition-colors flex items-center gap-1.5"
                                                        >
                                                            <X className="w-3 h-3" /> Remove
                                                        </button>
                                                    </motion.div>
                                                )}
                                            </AnimatePresence>
                                        </div>
                                    </div>

                                    {/* Scholarship URL */}
                                    <div className="space-y-3">
                                        <div className="flex items-center gap-2 text-xs font-bold tracking-widest text-gray-400 uppercase">
                                            <motion.div
                                                animate={{ scale: [1, 1.3, 1] }}
                                                transition={{ duration: 2, repeat: Infinity, delay: 0.3 }}
                                                className="w-2 h-2 bg-white rounded-full"
                                            />
                                            Scholarship URL
                                        </div>

                                        <div className="relative group">
                                            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-white transition-colors">
                                                <Link2 className="w-5 h-5" />
                                            </div>
                                            <input
                                                type="text"
                                                value={url}
                                                onChange={(e) => setUrl(e.target.value)}
                                                placeholder="https://example.com/scholarship"
                                                className="w-full h-14 bg-black/50 border border-white/20 rounded-xl pl-12 pr-4 text-white placeholder:text-gray-600 focus:outline-none focus:border-white/40 focus:bg-black/70 transition-all"
                                            />
                                        </div>
                                    </div>

                                    {/* Error Message */}
                                    <AnimatePresence>
                                        {error && (
                                            <motion.div
                                                initial={{ opacity: 0, y: -10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                exit={{ opacity: 0, y: -10 }}
                                                className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl flex items-center gap-3"
                                            >
                                                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                                                <p className="text-sm text-red-200">{error}</p>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>

                                    {/* Success Message */}
                                    <AnimatePresence>
                                        {success && (
                                            <motion.div
                                                initial={{ opacity: 0, y: -10 }}
                                                animate={{ opacity: 1, y: 0 }}
                                                exit={{ opacity: 0, y: -10 }}
                                                className="p-4 bg-green-500/10 border border-green-500/30 rounded-xl flex items-center gap-3"
                                            >
                                                <CheckCircle2 className="w-5 h-5 text-green-400 flex-shrink-0" />
                                                <p className="text-sm text-green-200 font-medium">{success.message}</p>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>

                                    {/* Action Button */}
                                    <motion.button
                                        onClick={handleSubmit}
                                        disabled={(!file && !url) || isSubmitting}
                                        whileHover={(!file && !url) || isSubmitting ? {} : { scale: 1.02 }}
                                        whileTap={(!file && !url) || isSubmitting ? {} : { scale: 0.98 }}
                                        className={`
                                                w-full h-14 rounded-xl font-medium text-lg transition-all duration-300 
                                                flex items-center justify-center gap-2
                                                ${(!file && !url)
                                                ? 'bg-white/10 text-gray-600 cursor-not-allowed'
                                                : isSubmitting
                                                    ? 'bg-white text-black cursor-wait'
                                                    : 'bg-white text-black hover:bg-gray-100 shadow-lg shadow-white/20'}
                                            `}
                                    >
                                        {isSubmitting ? (
                                            <>
                                                <Loader2 className="w-5 h-5 animate-spin" />
                                                Processing...
                                            </>
                                        ) : (
                                            <>
                                                Analyze <ArrowRight className="w-5 h-5" />
                                            </>
                                        )}
                                    </motion.button>

                                </div>
                            </motion.div>
                        </div>
                    )}
                </AnimatePresence>
            )}
        </div>
    );
}
