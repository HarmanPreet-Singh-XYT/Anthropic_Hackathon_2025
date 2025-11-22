import { useState } from 'react';
import { FileDown, Download, Sparkles } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { motion } from 'framer-motion';
import { jsPDF } from 'jspdf';

interface OutputPageProps {
    sessionData: {
        hasResume: boolean;
        hasScholarship: boolean;
        sessionId?: string;
        readyForOutput: boolean;
    };
    onBack: () => void;
}

export function OutputPage({ sessionData, onBack }: OutputPageProps) {
    const [essay, setEssay] = useState('');
    const [resume, setResume] = useState('');
    const [isLoading, setIsLoading] = useState(true);

    const exportAsPDF = () => {
        const doc = new jsPDF();

        // Add title
        doc.setFontSize(20);
        doc.text('SCHOLARSHIP APPLICATION', 20, 20);

        // Add essay section
        doc.setFontSize(16);
        doc.text('Essay', 20, 40);
        doc.setFontSize(12);
        const essayLines = doc.splitTextToSize(essay || 'Essay content will be generated...', 170);
        doc.text(essayLines, 20, 50);

        // Add resume section
        const resumeY = 50 + (essayLines.length * 7) + 20;
        doc.setFontSize(16);
        doc.text('Resume', 20, resumeY);
        doc.setFontSize(12);
        const resumeLines = doc.splitTextToSize(resume || 'Resume content will be generated...', 170);
        doc.text(resumeLines, 20, resumeY + 10);

        // Save the PDF
        doc.save('scholarship-application.pdf');
    };

    const exportAsDOCX = () => {
        // Export as LaTeX format
        const latexContent = `\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage[margin=1in]{geometry}

\\title{Scholarship Application}
\\author{}
\\date{}

\\begin{document}

\\maketitle

\\section*{Essay}
${essay || 'Essay content will be generated...'}

\\section*{Resume}
${resume || 'Resume content will be generated...'}

\\end{document}`;

        const blob = new Blob([latexContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'scholarship-application.tex';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    // Fetch generated content from backend
    useState(() => {
        const fetchOutput = async () => {
            try {
                // TODO: Call backend API to get generated essay and resume
                // For now, show loading state
                setIsLoading(true);

                // Simulate API call
                setTimeout(() => {
                    setEssay('Your personalized scholarship essay will appear here ...');
                    setResume('Your optimized resume will appear here...');
                    setIsLoading(false);
                }, 2000);
            } catch (error) {
                console.error('Error fetching output:', error);
                setEssay('Error generating essay. Please try again.');
                setResume('Error generating resume. Please try again.');
                setIsLoading(false);
            }
        };

        fetchOutput();
    });

    return (
        <div className="min-h-[800px] w-full p-6">
            <div className="max-w-[1150px] mx-auto py-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-6 text-center relative"
                >
                    <div className="relative inline-block">
                        <motion.div
                            animate={{
                                rotate: [0, 15, -15, 0],
                                scale: [1, 1.2, 1]
                            }}
                            transition={{ duration: 4, repeat: Infinity }}
                            className="relative"
                        >
                            <motion.div
                                animate={{
                                    scale: [1, 1.5, 1],
                                    opacity: [0.3, 0.6, 0.3]
                                }}
                                transition={{ duration: 2, repeat: Infinity }}
                                className="absolute inset-0 bg-white rounded-full blur-3xl pointer-events-none"
                            />
                            <Sparkles className="relative h-10 w-10 text-white mx-auto mb-3" />
                        </motion.div>
                    </div>

                    <motion.h1
                        className="text-white tracking-tight mb-2"
                        style={{
                            fontSize: '2.5rem',
                            fontWeight: 200,
                            textShadow: '0 0 40px rgba(255,255,255,0.3)'
                        }}
                        animate={{
                            textShadow: [
                                '0 0 40px rgba(255,255,255,0.3)',
                                '0 0 60px rgba(255,255,255,0.5)',
                                '0 0 40px rgba(255,255,255,0.3)',
                            ]
                        }}
                        transition={{ duration: 2, repeat: Infinity }}
                    >
                        Your Application
                    </motion.h1>
                    <motion.p
                        className="text-gray-400"
                        animate={{ opacity: [0.6, 1, 0.6] }}
                        transition={{ duration: 3, repeat: Infinity }}
                    >
                        Ready to impress
                    </motion.p>
                </motion.div>

                <div className="grid grid-cols-2 gap-5 mb-5">
                    {/* Essay Editor */}
                    <motion.div
                        initial={{ opacity: 0, x: -30, rotateY: 15 }}
                        animate={{ opacity: 1, x: 0, rotateY: 0 }}
                        transition={{ delay: 0.1 }}
                        whileHover={{ scale: 1.02, rotateY: -3 }}
                        className="relative"
                        style={{ transformStyle: 'preserve-3d' }}
                    >
                        {/* Rotating gradient border */}
                        <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
                            className="absolute -inset-[2px] rounded-3xl opacity-50"
                            style={{
                                background: 'linear-gradient(90deg, rgba(255,255,255,0.3), transparent, rgba(255,255,255,0.2), transparent)',
                            }}
                        />

                        <motion.div
                            animate={{
                                boxShadow: [
                                    '0 0 40px rgba(255,255,255,0.1)',
                                    '0 0 60px rgba(255,255,255,0.15)',
                                    '0 0 40px rgba(255,255,255,0.1)',
                                ]
                            }}
                            transition={{ duration: 3, repeat: Infinity }}
                            className="absolute inset-0 rounded-3xl pointer-events-none"
                        />

                        <div className="relative bg-black/50 backdrop-blur-3xl border border-white/20 rounded-3xl p-6 overflow-hidden">
                            {/* Grid overlay */}
                            <div
                                className="absolute inset-0 opacity-10 pointer-events-none"
                                style={{
                                    backgroundImage: `
                    linear-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.08) 1px, transparent 1px)
                  `,
                                    backgroundSize: '20px 20px',
                                }}
                            />

                            <div className="relative z-10 flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                    <motion.div
                                        animate={{ scale: [1, 1.3, 1] }}
                                        transition={{ duration: 2, repeat: Infinity }}
                                        className="w-2 h-2 bg-white rounded-full"
                                    />
                                    <h2 className="text-white tracking-widest text-xs uppercase">Essay</h2>
                                </div>
                                <motion.span
                                    className="text-gray-500 text-xs"
                                    key={essay.length}
                                    initial={{ scale: 1.2, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                >
                                    {essay.length} chars
                                </motion.span>
                            </div>

                            <div className="relative">
                                <Textarea
                                    value={essay}
                                    onChange={(e) => setEssay(e.target.value)}
                                    className="relative h-[450px] font-serif text-sm resize-none bg-white/5 border-white/10 text-white placeholder:text-gray-600 focus:border-white/30 focus:bg-white/10 rounded-2xl transition-all"
                                    placeholder="Your essay will appear here..."
                                />
                            </div>
                        </div>
                    </motion.div>

                    {/* Resume Editor */}
                    <motion.div
                        initial={{ opacity: 0, x: 30, rotateY: -15 }}
                        animate={{ opacity: 1, x: 0, rotateY: 0 }}
                        transition={{ delay: 0.2 }}
                        whileHover={{ scale: 1.02, rotateY: 3 }}
                        className="relative"
                        style={{ transformStyle: 'preserve-3d' }}
                    >
                        {/* Rotating gradient border */}
                        <motion.div
                            animate={{ rotate: -360 }}
                            transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
                            className="absolute -inset-[2px] rounded-3xl opacity-50"
                            style={{
                                background: 'linear-gradient(180deg, rgba(255,255,255,0.3), transparent, rgba(255,255,255,0.2), transparent)',
                            }}
                        />

                        <motion.div
                            animate={{
                                boxShadow: [
                                    '0 0 40px rgba(255,255,255,0.1)',
                                    '0 0 60px rgba(255,255,255,0.15)',
                                    '0 0 40px rgba(255,255,255,0.1)',
                                ]
                            }}
                            transition={{ duration: 3, repeat: Infinity, delay: 0.5 }}
                            className="absolute inset-0 rounded-3xl pointer-events-none"
                        />

                        <div className="relative bg-black/50 backdrop-blur-3xl border border-white/20 rounded-3xl p-6 overflow-hidden">
                            {/* Grid overlay */}
                            <div
                                className="absolute inset-0 opacity-10 pointer-events-none"
                                style={{
                                    backgroundImage: `
                    linear-gradient(rgba(255, 255, 255, 0.08) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.08) 1px, transparent 1px)
                  `,
                                    backgroundSize: '20px 20px',
                                }}
                            />

                            <div className="relative z-10 flex items-center justify-between mb-3">
                                <div className="flex items-center gap-2">
                                    <motion.div
                                        animate={{ scale: [1, 1.3, 1] }}
                                        transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
                                        className="w-2 h-2 bg-white rounded-full"
                                    />
                                    <h2 className="text-white tracking-widest text-xs uppercase">Resume</h2>
                                </div>
                                <motion.span
                                    className="text-gray-500 text-xs"
                                    key={resume.split('\n').length}
                                    initial={{ scale: 1.2, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                >
                                    {resume.split('\n').length} lines
                                </motion.span>
                            </div>

                            <div className="relative">
                                <Textarea
                                    value={resume}
                                    onChange={(e) => setResume(e.target.value)}
                                    className="relative h-[450px] font-mono text-xs resize-none bg-white/5 border-white/10 text-white placeholder:text-gray-600 focus:border-white/30 focus:bg-white/10 rounded-2xl transition-all"
                                    placeholder="Your resume will appear here..."
                                />
                            </div>
                        </div>
                    </motion.div>
                </div>

                {/* Export Buttons */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="relative"
                >
                    {/* Rotating gradient border */}
                    <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                        className="absolute -inset-[2px] rounded-3xl opacity-40"
                        style={{
                            background: 'linear-gradient(270deg, rgba(255,255,255,0.25), transparent, rgba(255,255,255,0.25), transparent)',
                        }}
                    />

                    <motion.div
                        animate={{
                            boxShadow: [
                                '0 0 30px rgba(255,255,255,0.1)',
                                '0 0 50px rgba(255,255,255,0.15)',
                                '0 0 30px rgba(255,255,255,0.1)',
                            ]
                        }}
                        transition={{ duration: 3, repeat: Infinity }}
                        className="absolute inset-0 rounded-3xl pointer-events-none"
                    />

                    <div className="relative bg-black/50 backdrop-blur-3xl border border-white/20 rounded-3xl p-6 overflow-hidden">
                        {/* Animated background blobs */}
                        <motion.div
                            className="absolute top-0 right-1/4 w-40 h-40 bg-white/5 rounded-full blur-3xl pointer-events-none"
                            animate={{
                                x: [0, 50, 0],
                                y: [0, -30, 0],
                                scale: [1, 1.2, 1],
                            }}
                            transition={{ duration: 8, repeat: Infinity }}
                        />

                        <div className="relative z-10 flex gap-5 items-center justify-center">
                            <motion.div
                                whileHover={{ scale: 1.08, y: -5, rotateZ: 2 }}
                                whileTap={{ scale: 0.95 }}
                            >
                                <div className="relative">
                                    <motion.div
                                        animate={{
                                            boxShadow: [
                                                '0 0 20px rgba(255,255,255,0.3)',
                                                '0 0 40px rgba(255,255,255,0.5)',
                                                '0 0 20px rgba(255,255,255,0.3)',
                                            ]
                                        }}
                                        transition={{ duration: 2, repeat: Infinity }}
                                        className="absolute inset-0 rounded-2xl blur-xl bg-white/20 pointer-events-none"
                                    />

                                    <Button
                                        size="lg"
                                        className="relative w-[220px] py-6 bg-white text-black hover:bg-gray-100 rounded-2xl overflow-hidden group"
                                        onClick={exportAsPDF}
                                    >
                                        {/* Shimmer effect */}
                                        <motion.div
                                            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent pointer-events-none"
                                            animate={{
                                                x: ['-100%', '100%'],
                                            }}
                                            transition={{ duration: 2, repeat: Infinity, repeatDelay: 1 }}
                                        />

                                        <span className="relative flex items-center justify-center">
                                            <FileDown className="mr-2 h-5 w-5" />
                                            Export PDF
                                        </span>
                                    </Button>
                                </div>
                            </motion.div>

                            <motion.div
                                whileHover={{ scale: 1.08, y: -5, rotateZ: -2 }}
                                whileTap={{ scale: 0.95 }}
                            >
                                <div className="relative">
                                    <motion.div
                                        animate={{
                                            boxShadow: [
                                                '0 0 15px rgba(255,255,255,0.2)',
                                                '0 0 30px rgba(255,255,255,0.3)',
                                                '0 0 15px rgba(255,255,255,0.2)',
                                            ]
                                        }}
                                        transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
                                        className="absolute inset-0 rounded-2xl blur-lg bg-white/10 pointer-events-none"
                                    />

                                    <Button
                                        size="lg"
                                        variant="outline"
                                        className="relative w-[220px] py-6 bg-transparent border-white/30 text-white hover:bg-white/10 hover:border-white/40 rounded-2xl overflow-hidden group"
                                        onClick={exportAsDOCX}
                                    >
                                        {/* Shimmer effect */}
                                        <motion.div
                                            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 pointer-events-none"
                                            animate={{
                                                x: ['-100%', '100%'],
                                            }}
                                            transition={{ duration: 1.5, repeat: Infinity }}
                                        />

                                        <span className="relative flex items-center justify-center">
                                            <Download className="mr-2 h-5 w-5" />
                                            Export LaTeX
                                        </span>
                                    </Button>
                                </div>
                            </motion.div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}