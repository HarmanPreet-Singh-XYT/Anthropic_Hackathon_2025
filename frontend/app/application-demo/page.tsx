"use client"

import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, FileText } from 'lucide-react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

// Mock data for demonstration
const MOCK_DATA = {
    essay: `As a first-generation college student from a small rural town in Montana, I've learned that resilience isn't just about bouncing back—it's about using challenges as stepping stones to greater heights. Growing up, my family faced financial hardships that many would consider insurmountable. My father worked three jobs to keep our household afloat, while my mother managed a small community garden that fed not just our family, but many of our neighbors who struggled similarly.

This environment shaped my understanding of community, perseverance, and the transformative power of education. When I discovered computer science in my junior year of high school, it wasn't just a subject—it was a revelation. Here was a field where creativity met logic, where problems could be solved through innovation, and where a single person with determination could create tools that impact thousands.

I founded a coding club at my high school, starting with just three members meeting in the library after school. Within two years, we grew to 40 students and launched a community website that connected local farmers with food banks, reducing waste and fighting hunger. This project taught me that technology isn't just about writing code—it's about understanding people's needs and crafting solutions that make tangible differences in their lives.`,
    resume: `• Developed and launched a full-stack web platform connecting 15+ local farmers with regional food banks, reducing food waste by 30% and serving over 500 families in need

• Founded and led high school coding club from 3 to 40 members, establishing curriculum focused on practical community problem-solving and securing $2,000 in grants for equipment

• Balanced 20+ hours of weekly employment with rigorous academic schedule, demonstrating exceptional time management while maintaining 3.9 GPA and leading multiple extracurricular initiatives

• Provided free mathematics tutoring to 15+ underserved students, developing adaptive teaching methods that improved average test scores by 25% and fostered STEM interest in rural community`,
};

export default function ApplicationDemoPage() {
    const [isExporting, setIsExporting] = useState(false);
    const contentRef = useRef<HTMLDivElement>(null);

    // Export to PDF function
    const handleExportPDF = async () => {
        if (!contentRef.current) return;

        setIsExporting(true);
        try {
            const canvas = await html2canvas(contentRef.current, {
                scale: 2,
                backgroundColor: '#050505',
                logging: false,
            });

            const imgData = canvas.toDataURL('image/png');
            const pdf = new jsPDF({
                orientation: 'portrait',
                unit: 'mm',
                format: 'a4'
            });

            const imgWidth = 210;
            const imgHeight = (canvas.height * imgWidth) / canvas.width;

            pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
            pdf.save('scholarship-application.pdf');

        } catch (error) {
            console.error('Error exporting PDF:', error);
        } finally {
            setIsExporting(false);
        }
    };

    return (
        <div className="h-screen bg-[#050505] text-white font-sans selection:bg-white/20 overflow-hidden relative flex flex-col items-center justify-center">

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
            </div>

            {/* Main Content */}
            <div className="relative z-10 w-full max-w-6xl px-6" ref={contentRef}>

                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="text-center mb-8"
                >
                    <div className="inline-flex items-center justify-center mb-3">
                        <Sparkles className="w-10 h-10 text-white fill-white" />
                    </div>
                    <h1 className="text-4xl md:text-5xl font-medium tracking-tight mb-2">
                        Your Application
                    </h1>
                    <p className="text-zinc-500 text-base font-light tracking-wide">
                        Ready to impress
                    </p>
                </motion.div>

                {/* Two Column Layout */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, delay: 0.2 }}
                    className="grid grid-cols-2 gap-6 mb-8"
                >
                    {/* Essay Section */}
                    <div className="bg-[#0f0f0f]/90 backdrop-blur-xl border border-white/10 rounded-[20px] p-6 shadow-2xl">
                        <div className="flex items-center gap-2 mb-4">
                            <div className="w-1.5 h-1.5 rounded-full bg-white" />
                            <h2 className="text-[10px] font-bold tracking-[0.15em] text-white uppercase">Essay</h2>
                        </div>

                        <div className="bg-[#1a1a1a]/60 border border-white/5 rounded-xl p-5 h-[400px] overflow-y-auto">
                            <p className="text-zinc-400 text-sm leading-relaxed whitespace-pre-wrap">
                                {MOCK_DATA.essay || 'Your essay will appear here...'}
                            </p>
                        </div>
                    </div>

                    {/* Resume Section */}
                    <div className="bg-[#0f0f0f]/90 backdrop-blur-xl border border-white/10 rounded-[20px] p-6 shadow-2xl">
                        <div className="flex items-center gap-2 mb-4">
                            <div className="w-1.5 h-1.5 rounded-full bg-white" />
                            <h2 className="text-[10px] font-bold tracking-[0.15em] text-white uppercase">Resume</h2>
                        </div>

                        <div className="bg-[#1a1a1a]/60 border border-white/5 rounded-xl p-5 h-[400px] overflow-y-auto">
                            <p className="text-zinc-400 text-sm leading-relaxed whitespace-pre-wrap">
                                {MOCK_DATA.resume || 'Your resume will appear here...'}
                            </p>
                        </div>
                    </div>
                </motion.div>

                {/* Export Button */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.6 }}
                    className="flex justify-center"
                >
                    <button
                        onClick={handleExportPDF}
                        disabled={isExporting}
                        className="h-12 px-6 rounded-xl font-medium text-sm flex items-center justify-center gap-2 bg-white text-black hover:bg-zinc-200 hover:scale-[1.01] active:scale-[0.99] shadow-lg shadow-white/10 transition-all duration-300 disabled:opacity-50"
                    >
                        <FileText className="w-4 h-4" />
                        {isExporting ? 'Exporting...' : 'Export PDF'}
                    </button>
                </motion.div>
            </div>
        </div>
    );
}
