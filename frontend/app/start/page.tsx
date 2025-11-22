"use client"

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Link2, Zap, ArrowRight, FileText, X, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { uploadResume } from '@/lib/api';

export default function StartPage() {
    const [file, setFile] = useState<File | null>(null);
    const [url, setUrl] = useState<string>('');
    const [isDragging, setIsDragging] = useState<boolean>(false);
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<{ message: string; chunks: number } | null>(null);
    const router = useRouter();

    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
        // Clear previous error/success
        setError(null);
        setSuccess(null);

        // Validate file type
        if (!f.name.toLowerCase().endsWith('.pdf')) {
            setError("Only PDF files are supported");
            return;
        }

        // Validate size
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
        if (!file && !url) return;

        setIsSubmitting(true);
        setError(null);
        setSuccess(null);

        try {
            // Create FormData for the workflow endpoint
            const formData = new FormData();
            formData.append('scholarship_url', url);
            if (file) {
                formData.append('resume_file', file);
            }

            // Step 1: Start Workflow
            const response = await fetch(`${API_URL}/api/workflow/start`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to start workflow');
            }

            const { session_id } = await response.json();
            console.log("[StartPage] Workflow started, session:", session_id);

            // Step 2: Poll for completion
            let completed = false;
            let pollCount = 0;
            const maxPolls = 60; // 2 minutes timeout (2s interval)

            while (!completed && pollCount < maxPolls) {
                await new Promise(resolve => setTimeout(resolve, 2000)); // Poll every 2s
                pollCount++;

                const statusResponse = await fetch(
                    `${API_URL}/api/workflow/status/${session_id}`
                );

                if (!statusResponse.ok) {
                    throw new Error('Failed to check workflow status');
                }

                const statusData = await statusResponse.json();
                console.log(`[StartPage] Poll #${pollCount}:`, statusData.status, statusData);

                if (statusData.status === 'processing') {
                    // Continue polling
                    continue;

                } else if (statusData.status === 'complete' || statusData.status === 'waiting_for_input') {
                    console.log("[StartPage] Workflow reached target state:", statusData.status);
                    completed = true;
                    setSuccess({
                        message: "Analysis complete!",
                        chunks: 0 // Not relevant for this flow
                    });

                    // Navigate to results
                    console.log("[StartPage] Navigating to matchmaker...");
                    await new Promise(resolve => setTimeout(resolve, 800));
                    router.push(`/matchmaker?session=${session_id}`);

                } else if (statusData.status === 'error') {
                    console.error("[StartPage] Workflow error:", statusData.error);
                    throw new Error(statusData.error || 'Workflow failed');
                }
            }

            if (!completed) {
                throw new Error("Workflow timed out");
            }

        } catch (err) {
            console.error("Workflow error:", err);
            setError(err instanceof Error ? err.message : "Failed to process. Please try again.");
        } finally {
            setIsSubmitting(false);
        }
    };


    return (
        <div className="min-h-screen bg-[#050505] text-white font-sans selection:bg-white/20 overflow-hidden relative flex flex-col items-center justify-center">

            {/* Background Stars/Particles */}
            <div className="absolute inset-0 z-0 pointer-events-none">
                {/* We can use a simple CSS solution or SVG for stars. 
             For now, let's use some absolute positioned divs with simple animations if needed, 
             or just a static nice background. 
             Let's try to mimic the 'stars' from the image with some small dots.
         */}
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
                <div className="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] bg-white/5 rounded-full blur-[150px]" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-white/5 rounded-full blur-[150px]" />
            </div>

            <div className="relative z-10 w-full max-w-2xl px-6 flex flex-col items-center">

                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="text-center mb-12"
                >
                    <div className="inline-flex items-center justify-center mb-6">
                        <Zap className="w-12 h-12 text-white fill-white" />
                    </div>
                    <h1 className="text-5xl md:text-6xl font-medium tracking-tight mb-4">
                        Scholarship Assistant
                    </h1>
                    <p className="text-zinc-500 text-lg font-light tracking-wide">
                        Transform your application into success
                    </p>
                </motion.div>

                {/* Main Card */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
                    className="w-full bg-[#111111]/80 backdrop-blur-2xl border border-white/10 rounded-[32px] p-8 md:p-10 shadow-2xl shadow-black/50 relative overflow-hidden group"
                >
                    {/* Inner Glow */}
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-1 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-50" />

                    <div className="space-y-8">

                        {/* Resume Upload */}
                        <div className="space-y-3">
                            <div className="flex items-center gap-2 text-xs font-bold tracking-widest text-zinc-400 uppercase">
                                <div className="w-2 h-2 rounded-full bg-white" />
                                Resume Upload
                            </div>

                            <div
                                onClick={() => document.getElementById('file-upload')?.click()}
                                onDragOver={handleDragOver}
                                onDragLeave={handleDragLeave}
                                onDrop={handleDrop}
                                className={`
                  relative h-48 rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent 
                  flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300
                  hover:bg-white/10 hover:border-white/20 group/upload
                  ${isDragging ? 'bg-white/10 border-white/30 scale-[1.02]' : ''}
                `}
                            >
                                <input
                                    id="file-upload"
                                    type="file"
                                    className="hidden"
                                    accept=".pdf,.doc,.docx,.latex"
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
                                            <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center group-hover/upload:scale-110 transition-transform duration-500">
                                                <Upload className="w-5 h-5 text-zinc-400 group-hover/upload:text-white transition-colors" />
                                            </div>
                                            <div className="space-y-1">
                                                <p className="text-lg font-medium text-zinc-300 group-hover/upload:text-white transition-colors">
                                                    Drop your resume here
                                                </p>
                                                <p className="text-sm text-zinc-500">
                                                    PDF • DOC • DOCX • LaTeX
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
                                            <div className="w-14 h-14 rounded-2xl bg-white text-black flex items-center justify-center shadow-lg shadow-white/10">
                                                <FileText className="w-7 h-7" />
                                            </div>
                                            <div className="text-center">
                                                <p className="text-white font-medium truncate max-w-[200px]">{file.name}</p>
                                                <p className="text-xs text-zinc-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                            </div>
                                            <button
                                                onClick={removeFile}
                                                className="mt-2 px-3 py-1.5 bg-white/10 hover:bg-white/20 rounded-full text-xs font-medium text-zinc-300 transition-colors flex items-center gap-1.5"
                                            >
                                                <X className="w-3 h-3" /> Remove
                                            </button>
                                        </motion.div>
                                    )}
                                </AnimatePresence>

                                {/* Shine effect */}
                                <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-white/0 via-white/5 to-white/0 opacity-0 group-hover/upload:opacity-100 transition-opacity pointer-events-none" />
                            </div>
                        </div>

                        {/* Scholarship URL */}
                        <div className="space-y-3">
                            <div className="flex items-center gap-2 text-xs font-bold tracking-widest text-zinc-400 uppercase">
                                <div className="w-2 h-2 rounded-full bg-white" />
                                Scholarship URL
                            </div>

                            <div className="relative group/input">
                                <div className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within/input:text-white transition-colors">
                                    <Link2 className="w-5 h-5" />
                                </div>
                                <input
                                    type="text"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    placeholder="https://example.com/scholarship"
                                    className="w-full h-14 bg-[#0A0A0A] border border-white/10 rounded-xl pl-12 pr-4 text-zinc-300 placeholder:text-zinc-600 focus:outline-none focus:border-white/30 focus:bg-[#0F0F0F] transition-all"
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
                                    <div className="flex-1">
                                        <p className="text-sm text-green-200 font-medium">{success.message}</p>
                                        <p className="text-xs text-green-300/70 mt-1">
                                            {success.chunks} chunks stored in vector database
                                        </p>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Action Button */}
                        <button
                            onClick={handleSubmit}
                            disabled={(!file && !url) || isSubmitting}
                            className={`
                w-full h-16 rounded-xl font-medium text-lg transition-all duration-300 flex items-center justify-center gap-2
                ${(!file && !url)
                                    ? 'bg-white/5 text-zinc-600 cursor-not-allowed'
                                    : isSubmitting
                                        ? 'bg-white/90 text-black cursor-wait'
                                        : 'bg-white text-black hover:bg-zinc-200 hover:scale-[1.01] active:scale-[0.99] shadow-lg shadow-white/10'}
              `}
                        >
                            {isSubmitting ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    Processing...
                                </>
                            ) : (
                                <>
                                    Continue to Chat <ArrowRight className="w-5 h-5" />
                                </>
                            )}
                        </button>

                    </div>
                </motion.div>
            </div>
        </div>
    );
}
