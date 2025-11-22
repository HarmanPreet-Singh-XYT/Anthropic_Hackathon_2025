import { useState } from 'react';
import { Upload, Link as LinkIcon, Zap, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { motion } from 'framer-motion';
import { uploadResume } from '@/lib/api';

interface InputPageProps {
    onContinue: (data: { hasResume: boolean; hasScholarship: boolean; sessionId?: string }) => void;
}

export function InputPage({ onContinue }: InputPageProps) {
    const [file, setFile] = useState<File | null>(null);
    const [url, setUrl] = useState('');
    const [dragActive, setDragActive] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-[800px] w-full p-6 relative">
            <div className="w-full max-w-[620px] space-y-6 relative z-10 py-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1, type: "spring", stiffness: 100 }}
                    className="text-center space-y-4"
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
                        <motion.div
                            animate={{
                                opacity: [0.5, 1, 0.5],
                            }}
                            transition={{ duration: 3, repeat: Infinity }}
                            className="absolute inset-0 blur-3xl"
                            style={{
                                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
                                backgroundSize: '200% 100%',
                            }}
                        />
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
                    className="relative"
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
                        className="absolute inset-0 rounded-3xl bg-gradient-to-br from-white/5 to-white/10"
                    />

                    <div className="relative bg-black/60 backdrop-blur-3xl border border-white/20 rounded-3xl p-8 space-y-6 overflow-hidden">
                        {/* Animated grid overlay */}
                        <div
                            className="absolute inset-0 opacity-20"
                            style={{
                                backgroundImage: `
                  linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
                  linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px)
                `,
                                backgroundSize: '30px 30px',
                            }}
                        />

                        {/* Resume Upload */}
                        <div className="relative z-10">
                            <label className="block text-white mb-3 text-xs tracking-widest uppercase flex items-center gap-2">
                                <motion.div
                                    animate={{ scale: [1, 1.2, 1] }}
                                    transition={{ duration: 2, repeat: Infinity }}
                                    className="w-2 h-2 bg-white rounded-full"
                                />
                                Resume Upload
                            </label>
                            <motion.div
                                whileHover={{ scale: 1.02, rotateX: 5 }}
                                transition={{ type: "spring", stiffness: 400 }}
                                className="relative group"
                                style={{ transformStyle: 'preserve-3d' }}
                            >
                                {/* Animated border effect */}
                                <motion.div
                                    className="absolute -inset-[1px] rounded-2xl"
                                    animate={{
                                        background: [
                                            'linear-gradient(45deg, rgba(255,255,255,0.2), rgba(255,255,255,0.05))',
                                            'linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.05))',
                                            'linear-gradient(225deg, rgba(255,255,255,0.2), rgba(255,255,255,0.05))',
                                            'linear-gradient(315deg, rgba(255,255,255,0.2), rgba(255,255,255,0.05))',
                                        ]
                                    }}
                                    transition={{ duration: 4, repeat: Infinity }}
                                />

                                <div
                                    className={`relative rounded-2xl p-12 text-center transition-all ${dragActive
                                        ? 'bg-white/15 border-2 border-white/50'
                                        : file
                                            ? 'bg-gradient-to-br from-white/10 to-white/5 border-2 border-white/30'
                                            : 'bg-white/5 border-2 border-dashed border-white/20 hover:border-white/40'
                                        }`}
                                    onDragEnter={handleDrag}
                                    onDragLeave={handleDrag}
                                    onDragOver={handleDrag}
                                    onDrop={handleDrop}
                                >
                                    <input
                                        type="file"
                                        accept=".pdf,.doc,.docx,.tex"
                                        onChange={handleFileChange}
                                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                                        aria-label="Upload resume file"
                                    />

                                    {/* Floating upload icon */}
                                    <motion.div
                                        animate={{
                                            y: [0, -12, 0],
                                            rotate: [0, 5, -5, 0],
                                        }}
                                        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                                        className="pointer-events-none"
                                    >
                                        <div className="relative inline-block">
                                            <motion.div
                                                animate={{
                                                    scale: [1, 1.5, 1],
                                                    opacity: [0.3, 0.6, 0.3],
                                                }}
                                                transition={{ duration: 2, repeat: Infinity }}
                                                className="absolute inset-0 bg-white rounded-full blur-xl"
                                            />
                                            <Upload className={`relative mx-auto h-12 w-12 mb-4 ${file ? 'text-white' : 'text-gray-400'}`} strokeWidth={1.5} />
                                        </div>
                                    </motion.div>

                                    {file ? (
                                        <motion.div
                                            initial={{ opacity: 0, scale: 0.8, y: 20 }}
                                            animate={{ opacity: 1, scale: 1, y: 0 }}
                                            transition={{ type: "spring" }}
                                            className="pointer-events-none"
                                        >
                                            <p className="text-white text-lg mb-1">{file.name}</p>
                                            <p className="text-gray-400 text-sm">
                                                {(file.size / 1024).toFixed(2)} KB
                                            </p>
                                        </motion.div>
                                    ) : (
                                        <div className="pointer-events-none">
                                            <p className="text-gray-200 text-lg mb-2">
                                                Drop your resume here
                                            </p>
                                            <p className="text-gray-500 text-sm">
                                                PDF • DOC • DOCX • LaTeX
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        </div>

                        {/* URL Input */}
                        <div className="relative z-10">
                            <label htmlFor="scholarship-url" className="block text-white mb-3 text-xs tracking-widest uppercase flex items-center gap-2">
                                <motion.div
                                    animate={{ scale: [1, 1.2, 1] }}
                                    transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
                                    className="w-2 h-2 bg-white rounded-full"
                                />
                                Scholarship URL
                            </label>
                            <div className="relative group">
                                {/* Glowing border on focus */}
                                <motion.div
                                    className="absolute -inset-[1px] rounded-2xl opacity-0 group-focus-within:opacity-100 transition-opacity"
                                    style={{
                                        background: 'linear-gradient(90deg, rgba(255,255,255,0.3), rgba(255,255,255,0.1), rgba(255,255,255,0.3))',
                                    }}
                                    animate={{
                                        backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
                                    }}
                                    transition={{ duration: 3, repeat: Infinity }}
                                />

                                <div className="relative flex items-center">
                                    <LinkIcon className="absolute left-4 h-5 w-5 text-gray-400 z-10" />
                                    <Input
                                        id="scholarship-url"
                                        type="url"
                                        placeholder="https://example.com/scholarship"
                                        value={url}
                                        onChange={(e) => setUrl(e.target.value)}
                                        className="relative pl-12 pr-4 py-6 bg-white/5 border-white/20 text-white placeholder:text-gray-600 focus:border-white/40 focus:bg-white/10 rounded-2xl transition-all"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Error Message */}
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="p-4 bg-red-500/10 border border-red-500/30 rounded-2xl"
                            >
                                <p className="text-red-200 text-sm">{error}</p>
                            </motion.div>
                        )}

                        {/* Continue Button */}
                        <motion.div
                            whileHover={{ scale: 1.03, y: -2 }}
                            whileTap={{ scale: 0.97 }}
                        >
                            <div className="relative group">
                                {/* Glowing effect */}
                                <motion.div
                                    animate={{
                                        boxShadow: [
                                            '0 0 20px rgba(255,255,255,0.3)',
                                            '0 0 40px rgba(255,255,255,0.5)',
                                            '0 0 20px rgba(255,255,255,0.3)',
                                        ]
                                    }}
                                    transition={{ duration: 2, repeat: Infinity }}
                                    className="absolute inset-0 rounded-2xl blur-xl bg-white/20"
                                />

                                <Button
                                    disabled={(!file && !url) || isLoading}
                                    onClick={async () => {
                                        setIsLoading(true);
                                        setError(null);
                                        try {
                                            let sessionId;
                                            // Upload resume if provided
                                            if (file) {
                                                try {
                                                    await uploadResume(file);
                                                } catch (err) {
                                                    console.warn('Resume upload failed:', err);
                                                    // Continue anyway - backend might not be running
                                                }
                                            }
                                            // Start Scout workflow if URL provided
                                            if (url) {
                                                try {
                                                    const formData = new FormData();
                                                    formData.append('scholarship_url', url);
                                                    const response = await fetch('http://localhost:8000/api/scout/start', {
                                                        method: 'POST',
                                                        body: formData,
                                                    });
                                                    const data = await response.json();
                                                    sessionId = data.session_id;
                                                } catch (err) {
                                                    console.warn('Scout workflow failed:', err);
                                                    // Continue anyway - backend might not be running
                                                }
                                            }
                                            // Always continue to chat even if backend calls fail
                                            onContinue({ hasResume: !!file, hasScholarship: !!url, sessionId });
                                        } catch (err) {
                                            // This should rarely happen now
                                            console.error('Unexpected error:', err);
                                            setError(err instanceof Error ? err.message : 'An error occurred');
                                            setIsLoading(false);
                                        }
                                    }}
                                    className="relative w-full py-7 text-lg bg-white text-black hover:bg-gray-100 rounded-2xl disabled:opacity-30 disabled:cursor-not-allowed overflow-hidden group"
                                >
                                    {/* Shimmer effect */}
                                    <motion.div
                                        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                                        animate={{
                                            x: ['-100%', '100%'],
                                        }}
                                        transition={{ duration: 2, repeat: Infinity, repeatDelay: 1 }}
                                    />

                                    <span className="relative flex items-center justify-center gap-3">
                                        {isLoading ? (
                                            <>
                                                <Loader2 className="w-5 h-5 animate-spin" />
                                                Processing...
                                            </>
                                        ) : (
                                            <>
                                                Continue to Chat
                                                <motion.span
                                                    animate={{ x: [0, 8, 0] }}
                                                    transition={{ duration: 1.5, repeat: Infinity }}
                                                >
                                                    →
                                                </motion.span>
                                            </>
                                        )}
                                    </span>
                                </Button>
                            </div>
                        </motion.div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}