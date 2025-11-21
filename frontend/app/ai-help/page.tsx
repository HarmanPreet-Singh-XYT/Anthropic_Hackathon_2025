"use client"

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, FileText, ChevronDown, ChevronUp, Sparkles, Bot, User } from 'lucide-react';

// --- Types ---
type Message = {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
};

type Requirement = {
    id: string;
    title: string;
    description: string;
    status: 'met' | 'partial' | 'missing';
};

// --- Mock Data ---
const INITIAL_MESSAGES: Message[] = [
    {
        id: '1',
        role: 'assistant',
        content: "Hi! I've analyzed your resume and the scholarship requirements. I need a few more details to create the perfect application. What specific achievements or projects do you have relating to leadership in community service?",
        timestamp: new Date(Date.now() - 60000),
    }
];

const MOCK_REQUIREMENTS: Requirement[] = [
    {
        id: '1',
        title: 'Academic Excellence',
        description: 'Must maintain a minimum GPA of 3.5 or higher. Transcript verification required.',
        status: 'met',
    },
    {
        id: '2',
        title: 'Leadership',
        description: 'Demonstrated leadership roles in school or community organizations for at least 1 year.',
        status: 'partial',
    },
    {
        id: '3',
        title: 'Community Impact',
        description: 'Evidence of significant contribution to local community improvement projects.',
        status: 'missing',
    }
];

export default function AIHelpPage() {
    const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
    const [inputValue, setInputValue] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [expandedReq, setExpandedReq] = useState<string | null>('1');

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);

    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        const newUserMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: inputValue,
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, newUserMsg]);
        setInputValue('');
        setIsTyping(true);

        // Simulate AI response
        setTimeout(() => {
            const newAiMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: "That's a great example! I can definitely weave that into the essay to highlight your initiative. Could you elaborate on the specific outcome of that project?",
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, newAiMsg]);
            setIsTyping(false);
        }, 2000);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <div className="min-h-screen bg-[#050505] text-white font-sans selection:bg-white/20 relative flex flex-col pt-32 pb-10 px-4 md:px-6">

            {/* Background Effects */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                <div className="absolute top-[-20%] left-[-10%] w-[800px] h-[800px] bg-purple-500/5 rounded-full blur-[150px]" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] bg-blue-500/5 rounded-full blur-[150px]" />
                {/* Stars */}
                {[...Array(15)].map((_, i) => (
                    <div
                        key={i}
                        className="absolute rounded-full bg-white opacity-20 animate-pulse"
                        style={{
                            top: `${Math.random() * 100}%`,
                            left: `${Math.random() * 100}%`,
                            width: `${Math.random() * 2 + 1}px`,
                            height: `${Math.random() * 2 + 1}px`,
                            animationDuration: `${Math.random() * 4 + 2}s`,
                        }}
                    />
                ))}
            </div>

            <div className="relative z-10 w-full max-w-7xl mx-auto h-[80vh] flex flex-col">
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full">

                    {/* LEFT COLUMN: CHAT INTERFACE */}
                    <div className="lg:col-span-8 flex flex-col h-full">

                        {/* Chat Container */}
                        <div className="flex-1 bg-[#111111]/60 backdrop-blur-xl border border-white/10 rounded-[32px] flex flex-col overflow-hidden shadow-2xl relative">

                            {/* Header */}
                            <div className="h-20 border-b border-white/5 flex items-center px-8 justify-between bg-white/5">
                                <div className="flex items-center gap-3">
                                    <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
                                    <h2 className="text-xl font-medium tracking-tight">AI Assistant</h2>
                                </div>
                                <div className="flex items-center gap-2 text-xs font-mono text-zinc-500 bg-black/20 px-3 py-1 rounded-full border border-white/5">
                                    <Sparkles className="w-3 h-3 text-purple-400" />
                                    <span>MODEL: CLAUDE 3.5 SONNET</span>
                                </div>
                            </div>

                            {/* Messages Area */}
                            <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                                {messages.map((msg) => (
                                    <motion.div
                                        key={msg.id}
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                    >
                                        <div className={`flex max-w-[80%] gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>

                                            {/* Avatar */}
                                            <div className={`
                        w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0
                        ${msg.role === 'assistant' ? 'bg-white/10 text-white' : 'bg-zinc-800 text-zinc-400'}
                      `}>
                                                {msg.role === 'assistant' ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
                                            </div>

                                            {/* Bubble */}
                                            <div className={`
                        p-5 rounded-2xl text-sm leading-relaxed shadow-lg
                        ${msg.role === 'assistant'
                                                    ? 'bg-[#1A1A1A] border border-white/5 text-zinc-200 rounded-tl-none'
                                                    : 'bg-white text-black rounded-tr-none font-medium'}
                      `}>
                                                {msg.content}
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}

                                {isTyping && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="flex w-full justify-start"
                                    >
                                        <div className="flex max-w-[80%] gap-4">
                                            <div className="w-10 h-10 rounded-full bg-white/10 text-white flex items-center justify-center flex-shrink-0">
                                                <Bot className="w-5 h-5" />
                                            </div>
                                            <div className="bg-[#1A1A1A] border border-white/5 p-5 rounded-2xl rounded-tl-none flex gap-1 items-center h-[60px]">
                                                <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                                                <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                                                <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                                            </div>
                                        </div>
                                    </motion.div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>

                            {/* Input Area */}
                            <div className="p-6 bg-gradient-to-t from-black/40 to-transparent">
                                <div className="relative group">
                                    <textarea
                                        value={inputValue}
                                        onChange={(e) => setInputValue(e.target.value)}
                                        onKeyDown={handleKeyDown}
                                        placeholder="Type your message..."
                                        className="w-full bg-[#0A0A0A] border border-white/10 rounded-2xl pl-6 pr-14 py-4 text-zinc-300 placeholder:text-zinc-600 focus:outline-none focus:border-white/20 focus:bg-[#0F0F0F] transition-all resize-none h-[60px] min-h-[60px] max-h-[120px]"
                                    />
                                    <button
                                        onClick={handleSendMessage}
                                        disabled={!inputValue.trim()}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-white/10 hover:bg-white text-white hover:text-black rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                    >
                                        <Send className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                        </div>
                    </div>

                    {/* RIGHT COLUMN: CONTEXT SIDEBAR */}
                    <div className="lg:col-span-4 flex flex-col gap-6 h-full overflow-y-auto pb-6 scrollbar-hide">

                        {/* Resume Card */}
                        <div className="bg-[#111111]/60 backdrop-blur-xl border border-white/10 rounded-[32px] p-6 flex flex-col gap-4 relative overflow-hidden group">
                            <div className="flex items-center gap-2 text-xs font-bold tracking-widest text-zinc-400 uppercase mb-2">
                                <div className="w-2 h-2 rounded-full bg-white" />
                                Resume
                            </div>

                            <div className="aspect-[4/3] bg-black/40 rounded-xl border border-white/5 flex items-center justify-center relative overflow-hidden group-hover:border-white/20 transition-colors cursor-pointer">
                                <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                                <div className="text-center z-10">
                                    <FileText className="w-12 h-12 text-zinc-600 mx-auto mb-2 group-hover:text-white transition-colors" />
                                    <p className="text-zinc-500 text-sm group-hover:text-zinc-300">resume.pdf</p>
                                </div>
                            </div>
                        </div>

                        {/* Requirements / Keywords */}
                        <div className="bg-[#111111]/60 backdrop-blur-xl border border-white/10 rounded-[32px] p-6 flex-1 flex flex-col relative overflow-hidden">
                            <div className="flex items-center justify-between mb-6">
                                <div className="flex items-center gap-2 text-xs font-bold tracking-widest text-zinc-400 uppercase">
                                    <div className="w-2 h-2 rounded-full bg-white" />
                                    Key Words / Requirements
                                </div>
                                <ChevronDown className="w-4 h-4 text-zinc-600" />
                            </div>

                            <div className="space-y-3 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-white/10">
                                {MOCK_REQUIREMENTS.map((req) => (
                                    <motion.div
                                        key={req.id}
                                        layout
                                        onClick={() => setExpandedReq(expandedReq === req.id ? null : req.id)}
                                        className={`
                       p-4 rounded-2xl border transition-all cursor-pointer
                       ${expandedReq === req.id
                                                ? 'bg-white/10 border-white/20'
                                                : 'bg-white/5 border-transparent hover:bg-white/10'}
                     `}
                                    >
                                        <div className="flex items-start justify-between">
                                            <h4 className="font-medium text-sm text-zinc-200">{req.title}</h4>
                                            <div className={`w-2 h-2 rounded-full mt-1.5 ${req.status === 'met' ? 'bg-green-500' :
                                                req.status === 'partial' ? 'bg-yellow-500' : 'bg-red-500'
                                                }`} />
                                        </div>

                                        <AnimatePresence>
                                            {expandedReq === req.id && (
                                                <motion.div
                                                    initial={{ height: 0, opacity: 0, marginTop: 0 }}
                                                    animate={{ height: 'auto', opacity: 1, marginTop: 8 }}
                                                    exit={{ height: 0, opacity: 0, marginTop: 0 }}
                                                    className="overflow-hidden"
                                                >
                                                    <p className="text-xs text-zinc-400 leading-relaxed">
                                                        {req.description}
                                                    </p>
                                                </motion.div>
                                            )}
                                        </AnimatePresence>
                                    </motion.div>
                                ))}
                            </div>
                        </div>

                    </div>

                </div>
            </div>
        </div>
    );
}
