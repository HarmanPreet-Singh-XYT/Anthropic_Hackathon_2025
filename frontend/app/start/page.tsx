"use client"

import { useState } from "react";
import { InputPage } from "@/components/InputPage";
import { ChatPage } from "@/components/ChatPage";
import { OutputPage } from "@/components/OutputPage";
import { ParticleBackground } from "@/components/ParticleBackground";
import { motion, AnimatePresence } from "framer-motion";

export default function App() {
    const [currentPage, setCurrentPage] = useState<1 | 2 | 3>(1);
    const [sessionData, setSessionData] = useState<{
        hasResume: boolean;
        hasScholarship: boolean;
        sessionId?: string;
        readyForOutput: boolean;
    }>({
        hasResume: false,
        hasScholarship: false,
        readyForOutput: false
    });

    return (
        <div className="w-[1265px] min-h-[900px] mx-auto relative bg-black">
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
                <motion.div
                    animate={{
                        x: [0, 100, -100, 0],
                        y: [0, -100, 100, 0],
                        rotate: [0, 180, 360],
                    }}
                    transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
                    className="absolute top-1/2 left-1/2 w-[500px] h-[500px] rounded-full"
                    style={{
                        background: 'radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%)',
                        filter: 'blur(50px)',
                    }}
                />
            </div>

            <AnimatePresence mode="wait">
                <motion.div
                    key={currentPage}
                    initial={{ opacity: 0, rotateY: 90 }}
                    animate={{ opacity: 1, rotateY: 0 }}
                    exit={{ opacity: 0, rotateY: -90 }}
                    transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                    className="min-h-[800px] w-full"
                    style={{ perspective: 1200 }}
                >
                    {currentPage === 1 && <InputPage onContinue={(data) => {
                        setSessionData({ ...data, readyForOutput: false });
                        setCurrentPage(2);
                    }} />}
                    {currentPage === 2 && <ChatPage 
                        sessionData={sessionData}
                        onContinue={() => {
                            setSessionData(prev => ({ ...prev, readyForOutput: true }));
                            setCurrentPage(3);
                        }} 
                        onBack={() => setCurrentPage(1)} 
                    />}
                    {currentPage === 3 && <OutputPage 
                        sessionData={sessionData}
                        onBack={() => setCurrentPage(2)} 
                    />}
                </motion.div>
            </AnimatePresence>
        </div>
    );
}