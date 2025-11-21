"use client"
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Upload, Link2, Loader2, FileText, X, CheckCircle2, Sparkles } from 'lucide-react';
import { useTheme } from '@/context/ThemeContext';
import ThemeToggle from '@/components/ThemeToggle';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Utility for cleaner tailwind classes
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export default function ScholarshipAssistant() {
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState<string>('');
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [loadingStep, setLoadingStep] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const { darkMode } = useTheme();

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  // Theme handling
  useEffect(() => {
    if (darkMode) document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
  }, [darkMode]);

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
    const validTypes = ['.pdf', '.doc', '.docx', '.tex'];
    const extension = '.' + f.name.split('.').pop()?.toLowerCase();
    
    // Simple validation check (can be expanded)
    if (f.size > 5 * 1024 * 1024) { // 5MB limit
        setErrorMessage("File is too large. Max 5MB.");
        return;
    }
    
    setFile(f);
    setErrorMessage('');
    setStatus('idle');
  };

  const removeFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setFile(null);
  };

  // URL Logic
  const normalizeUrl = (str: string) => {
    const trimmed = str.trim();
    return (!trimmed.startsWith('http') && trimmed.length > 0) ? `https://${trimmed}` : trimmed;
  };

  const simulateLoadingSteps = () => {
    const steps = ["Parsing Resume...", "Analyzing Scholarship Criteria...", "Generating Application..."];
    let i = 0;
    setLoadingStep(steps[0]);
    const interval = setInterval(() => {
      i++;
      if (i < steps.length) setLoadingStep(steps[i]);
    }, 1500);
    return interval;
  };

  const handleContinue = async () => {
    if (!file || !url) {
      setErrorMessage('Please provide both a resume and a URL.');
      return;
    }

    const normalizedUrl = normalizeUrl(url);
    try {
      new URL(normalizedUrl);
    } catch {
      setErrorMessage('Please enter a valid URL.');
      return;
    }

    setStatus('loading');
    setErrorMessage('');
    const loadingInterval = simulateLoadingSteps();

    try {
      const formData = new FormData();
      formData.append('resume', file);
      formData.append('scholarship_url', normalizedUrl);

      const response = await fetch(`${BACKEND_URL}/api/scholarship-application`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(loadingInterval);

      if (!response.ok) throw new Error('Failed to process application');
      
      const data = await response.json();
      console.log('Success:', data);
      setStatus('success');

    } catch (err) {
      clearInterval(loadingInterval);
      console.error(err);
      setStatus('error');
      setErrorMessage('Connection failed. Please try again later.');
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center p-4 md:p-8 transition-colors duration-500 bg-[#FAFAFA] dark:bg-[#09090b] relative overflow-hidden">
      
      {/* Ambient Background Effects */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-blue-500/10 dark:bg-blue-500/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-purple-500/10 dark:bg-purple-500/20 rounded-full blur-[120px]" />
      </div>

      <div className="absolute top-6 right-6 z-50">
        <ThemeToggle />
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-xl relative z-10"
      >
        {/* Header Section */}
        <div className="text-center mb-8 space-y-3">
          <div className="inline-flex items-center justify-center p-2 bg-white dark:bg-zinc-900 rounded-2xl shadow-sm border border-zinc-200 dark:border-zinc-800 mb-4">
            <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400 mr-2" />
            <span className="text-sm font-semibold text-zinc-800 dark:text-zinc-200">AI-Powered Assistant</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-zinc-900 dark:text-white">
            Scholarship Assistant
          </h1>
          <p className="text-lg text-zinc-500 dark:text-zinc-400 max-w-md mx-auto">
            Drop your resume and a link. We'll handle the heavy lifting.
          </p>
        </div>

        {/* Main Card */}
        <Card className="overflow-hidden border-0 shadow-2xl bg-white/70 dark:bg-zinc-900/70 backdrop-blur-xl ring-1 ring-black/5 dark:ring-white/10">
          
          {/* Success Overlay */}
          <AnimatePresence>
            {status === 'success' && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 z-20 bg-white/90 dark:bg-zinc-950/90 flex flex-col items-center justify-center text-center p-8 backdrop-blur-sm"
              >
                <motion.div 
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.1, type: "spring" }}
                  className="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mb-6"
                >
                  <CheckCircle2 className="w-10 h-10 text-green-600 dark:text-green-400" />
                </motion.div>
                <h3 className="text-2xl font-bold text-zinc-900 dark:text-white mb-2">Application Generated!</h3>
                <p className="text-zinc-500 dark:text-zinc-400 mb-8 max-w-xs">
                  Your tailored scholarship application is ready for review.
                </p>
                <Button 
                  onClick={() => {
                    setStatus('idle');
                    setFile(null);
                    setUrl('');
                  }}
                  className="h-12 px-8 rounded-full bg-zinc-900 text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-200 transition-all"
                >
                  Start Another
                </Button>
              </motion.div>
            )}
          </AnimatePresence>

          <CardContent className="p-8 space-y-8">
            
            {/* Error Banner */}
            <AnimatePresence>
              {errorMessage && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="bg-red-50 dark:bg-red-950/30 text-red-600 dark:text-red-400 px-4 py-3 rounded-lg text-sm font-medium border border-red-100 dark:border-red-900/50 flex items-center"
                >
                  <span className="mr-2">⚠️</span> {errorMessage}
                </motion.div>
              )}
            </AnimatePresence>

            {/* File Upload Section */}
            <div className="space-y-3">
              <Label className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 uppercase tracking-wider">
                Resume
              </Label>
              
              {!file ? (
                <motion.div
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => document.getElementById('file-input')?.click()}
                  className={cn(
                    "relative group cursor-pointer flex flex-col items-center justify-center w-full h-48 rounded-2xl border-2 border-dashed transition-all duration-300",
                    isDragging 
                      ? "border-blue-500 bg-blue-50/50 dark:bg-blue-500/10" 
                      : "border-zinc-300 dark:border-zinc-700 hover:border-zinc-400 dark:hover:border-zinc-600 hover:bg-zinc-50 dark:hover:bg-zinc-800/50"
                  )}
                >
                  <input id="file-input" type="file" className="hidden" accept=".pdf,.doc,.docx" onChange={handleFileSelect} />
                  
                  <div className="p-4 bg-white dark:bg-zinc-800 rounded-full shadow-lg mb-4 group-hover:scale-110 transition-transform duration-300">
                    <Upload className="w-6 h-6 text-zinc-600 dark:text-zinc-300" />
                  </div>
                  <p className="text-sm font-medium text-zinc-700 dark:text-zinc-200">
                    Click to upload or drag & drop
                  </p>
                  <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                    PDF, DOCX (Max 5MB)
                  </p>
                </motion.div>
              ) : (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="relative w-full p-4 bg-zinc-50 dark:bg-zinc-800/50 border border-zinc-200 dark:border-zinc-700 rounded-xl flex items-center justify-between group"
                >
                  <div className="flex items-center gap-4 overflow-hidden">
                    <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
                      <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="truncate">
                      <p className="text-sm font-medium text-zinc-900 dark:text-white truncate">{file.name}</p>
                      <p className="text-xs text-zinc-500 dark:text-zinc-400">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={removeFile}
                    className="text-zinc-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </Button>
                </motion.div>
              )}
            </div>

            {/* URL Section */}
            <div className="space-y-3">
              <Label className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 uppercase tracking-wider">
                Scholarship Link
              </Label>
              <div className="relative group">
                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400 group-focus-within:text-blue-500 transition-colors">
                  <Link2 className="w-5 h-5" />
                </div>
                <Input
                  type="text"
                  placeholder="Paste the scholarship URL here..."
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                                    className="pl-10 h-14 bg-zinc-50 dark:bg-zinc-800/50 border-zinc-200 dark:border-zinc-700 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 dark:text-white rounded-xl text-base transition-all"
                />
              </div>
            </div>

            {/* Action Button */}
            <div className="pt-2">
              <Button
                onClick={handleContinue}
                disabled={status === 'loading' || !file || !url}
                className={cn(
                  "w-full h-14 text-lg font-medium rounded-xl relative overflow-hidden transition-all duration-300",
                  status === 'loading' 
                    ? "bg-zinc-100 text-zinc-400 dark:bg-zinc-800 dark:text-zinc-500 cursor-not-allowed"
                    : "bg-zinc-900 text-white hover:bg-zinc-800 hover:shadow-lg hover:-translate-y-0.5 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-200"
                )}
              >
                {/* Background Gradient Animation on Hover (only when active) */}
                {status !== 'loading' && (
                  <div className="absolute inset-0 bg-linear-to-r from-transparent via-white/10 to-transparent -translate-x-[100%] group-hover:animate-shimmer" />
                )}

                <div className="relative flex items-center justify-center gap-2">
                  {status === 'loading' ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <AnimatePresence mode="wait">
                        <motion.span
                          key={loadingStep}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                          className="min-w-[140px] text-left"
                        >
                          {loadingStep}
                        </motion.span>
                      </AnimatePresence>
                    </>
                  ) : (
                    <>
                      <span>Generate Application</span>
                      <Sparkles className="w-5 h-5" />
                    </>
                  )}
                </div>
              </Button>
            </div>

          </CardContent>
        </Card>

        {/* Footer Trust Badge */}
        <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="mt-8 text-center space-y-2"
        >
            <p className="text-xs text-zinc-400 dark:text-zinc-500 flex items-center justify-center gap-2">
               <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"/> 
               Secure Encryption • AI Model V4.0 • Privacy First
            </p>
        </motion.div>

      </motion.div>
    </div>
  );
}