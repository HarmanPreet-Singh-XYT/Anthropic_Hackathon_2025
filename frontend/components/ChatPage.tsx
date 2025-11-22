import { useState, useRef, useEffect } from 'react';
import { Send, FileText, ChevronDown } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
    role: 'assistant' | 'user';
    content: string;
}

interface Keyword {
    id: number;
    title: string;
    description: string;
}

interface ChatPageProps {
    sessionData: {
        hasResume: boolean;
        hasScholarship: boolean;
        sessionId?: string;
        readyForOutput: boolean;
    };
    onContinue: () => void;
    onBack: () => void;
}

export function ChatPage({ sessionData, onContinue, onBack }: ChatPageProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'assistant',
            content: "Hi! I've analyzed your resume and the scholarship requirements. I need a few more details to create the perfect application. What specific achievements or projects do you have relating to ...?"
        }
    ]);
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const [keywords, setKeywords] = useState<Keyword[]>([]);
    const [resumeText, setResumeText] = useState<string>('Loading resume...');
    const [isLoadingResume, setIsLoadingResume] = useState(true);

    const [keywordsExpanded, setKeywordsExpanded] = useState(true);
    const [resumeExpanded, setResumeExpanded] = useState(true);
    const [isLoading, setIsLoading] = useState(false);

    // Fetch resume from backend when component mounts
    useEffect(() => {
        const fetchResume = async () => {
            if (!sessionData.hasResume) {
                setResumeText('No resume uploaded');
                setIsLoadingResume(false);
                return;
            }

            try {
                const response = await fetch('http://localhost:8000/api/resume-stats');
                const data = await response.json();

                if (data.success && data.count > 0) {
                    setResumeText('Resume uploaded');
                } else {
                    setResumeText('Resume uploaded');
                }
            } catch (error) {
                console.error('Error fetching resume:', error);
                setResumeText('Unable to load');
            } finally {
                setIsLoadingResume(false);
            }
        };

        fetchResume();
    }, [sessionData.hasResume]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            // TODO: Backend integration coming soon
            // Simulating AI response for now
            await new Promise(resolve => setTimeout(resolve, 1000));

            const mockResponses = [
                "That's really interesting! Tell me more about your experiences relating to ...",
                "Great! What are your ...",
                "I'd love to hear about any leadership experiences you've had.",
                "Excellent! How about...",
            ];

            const assistantMessage: Message = {
                role: 'assistant',
                content: mockResponses[Math.floor(Math.random() * mockResponses.length)]
            };

            setMessages(prev => {
                const updatedMessages = [...prev, assistantMessage];

                // Auto-progress to output page after 4 messages (2 exchanges)
                if (updatedMessages.length >= 4) {
                    setTimeout(() => {
                        onContinue();
                    }, 2000);
                }

                return updatedMessages;
            });

            // Mock keyword extraction
            const mockKeywords: Keyword[] = [
                { id: 1, title: 'Leadership', description: 'Demonstrated leadership skills' },
                { id: 2, title: 'Academic Excellence', description: 'Strong academic performance' },
                { id: 3, title: 'Keyword 3', description: 'blablabla...' },
            ];

            if (messages.length < 3) {
                setKeywords(prev => {
                    const randomKeyword = mockKeywords[Math.floor(Math.random() * mockKeywords.length)];
                    if (!prev.some(k => k.title === randomKeyword.title)) {
                        return [...prev, randomKeyword];
                    }
                    return prev;
                });
            }

        } catch (error) {
            console.error('Chat error:', error);
            const fallbackMessage: Message = {
                role: 'assistant',
                content: "Thank you for sharing that! Could you tell me more about your experiences?"
            };
            setMessages(prev => [...prev, fallbackMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-[800px] w-full p-6 relative">
            <div className="max-w-[1150px] mx-auto min-h-full py-8">
                <div className="grid grid-cols-3 gap-5 min-h-[700px]">
                    {/* Chat Section */}
                    <div className="col-span-2 relative flex flex-col">
                        {/* Rotating gradient border */}
                        <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                            className="absolute -inset-[2px] rounded-3xl opacity-50"
                            style={{
                                background: 'linear-gradient(60deg, rgba(255,255,255,0.3), transparent, rgba(255,255,255,0.2), transparent)',
                            }}
                        />

                        <motion.div
                            initial={{ opacity: 0, x: -30 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.1 }}
                            whileHover={{ y: -3 }}
                            className="relative h-full bg-black/50 backdrop-blur-3xl border border-white/20 rounded-3xl p-6 flex flex-col overflow-hidden min-h-[700px]"
                            style={{ boxShadow: '0 0 60px rgba(255,255,255,0.1)' }}
                        >
                            {/* Animated grid overlay */}
                            <div
                                className="absolute inset-0 opacity-10 pointer-events-none"
                                style={{
                                    backgroundImage: `
                    linear-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(255, 255, 255, 0.1) 1px, transparent 1px)
                  `,
                                    backgroundSize: '25px 25px',
                                }}
                            />

                            <div className="relative z-10 mb-4 flex items-center gap-3 flex-shrink-0">
                                <motion.div
                                    animate={{
                                        scale: [1, 1.1, 1],
                                        rotate: [0, 5, -5, 0]
                                    }}
                                    transition={{ duration: 3, repeat: Infinity }}
                                >
                                    <div className="w-3 h-3 bg-white rounded-full shadow-lg shadow-white/50" />
                                </motion.div>
                                <h2 className="text-white text-xl tracking-tight" style={{ fontWeight: 200 }}>
                                    AI Assistant
                                </h2>
                            </div>

                            <div className="relative flex-1 overflow-y-auto space-y-4 mb-4 pr-2 min-h-0">
                                <AnimatePresence initial={false}>
                                    {messages.map((message, index) => (
                                        <motion.div
                                            key={index}
                                            initial={{ opacity: 0, y: 20, x: message.role === 'user' ? 20 : -20, scale: 0.95 }}
                                            animate={{ opacity: 1, y: 0, x: 0, scale: 1 }}
                                            transition={{
                                                type: "spring",
                                                stiffness: 300,
                                                damping: 25,
                                                delay: index * 0.05
                                            }}
                                            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                        >
                                            <motion.div
                                                whileHover={{ scale: 1.01, y: -1 }}
                                                className={`relative max-w-[85%] rounded-3xl p-5 ${message.role === 'user'
                                                    ? 'bg-white text-black'
                                                    : 'bg-white/5 text-white backdrop-blur-sm border border-white/20'
                                                    }`}
                                                style={{
                                                    borderRadius: message.role === 'user' ? '24px 24px 4px 24px' : '24px 24px 24px 4px',
                                                    boxShadow: message.role === 'user'
                                                        ? '0 8px 32px rgba(255,255,255,0.2)'
                                                        : '0 4px 20px rgba(0,0,0,0.3)'
                                                }}
                                            >
                                                {message.role === 'user' && (
                                                    <motion.div
                                                        className="absolute inset-0 rounded-3xl pointer-events-none"
                                                        animate={{
                                                            boxShadow: [
                                                                '0 0 20px rgba(255,255,255,0.2)',
                                                                '0 0 30px rgba(255,255,255,0.4)',
                                                                '0 0 20px rgba(255,255,255,0.2)',
                                                            ]
                                                        }}
                                                        transition={{ duration: 2, repeat: Infinity }}
                                                    />
                                                )}
                                                <span className="relative text-sm">{message.content}</span>
                                            </motion.div>
                                        </motion.div>
                                    ))}
                                </AnimatePresence>
                                <div ref={messagesEndRef} />
                            </div>

                            <div className="relative flex gap-3 flex-shrink-0">
                                <div className="flex-1 relative group">
                                    {/* Glowing border on focus */}
                                    <motion.div
                                        className="absolute -inset-[1px] rounded-full opacity-0 group-focus-within:opacity-100 transition-opacity"
                                        animate={{
                                            background: [
                                                'linear-gradient(90deg, rgba(255,255,255,0.3), rgba(255,255,255,0.1))',
                                                'linear-gradient(180deg, rgba(255,255,255,0.3), rgba(255,255,255,0.1))',
                                                'linear-gradient(270deg, rgba(255,255,255,0.3), rgba(255,255,255,0.1))',
                                            ]
                                        }}
                                        transition={{ duration: 2, repeat: Infinity }}
                                    />
                                    <Input
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                        placeholder="Type your message..."
                                        className="relative py-6 px-5 bg-white/5 border-white/20 text-white placeholder:text-gray-600 focus:border-white/30 focus:bg-white/10 rounded-full"
                                    />
                                </div>

                                <motion.div
                                    whileHover={{ scale: 1.1, rotate: 10 }}
                                    whileTap={{ scale: 0.9 }}
                                >
                                    <div className="relative">
                                        <motion.div
                                            animate={{
                                                boxShadow: [
                                                    '0 0 15px rgba(255,255,255,0.2)',
                                                    '0 0 25px rgba(255,255,255,0.4)',
                                                    '0 0 15px rgba(255,255,255,0.2)',
                                                ]
                                            }}
                                            transition={{ duration: 2, repeat: Infinity }}
                                            className="absolute inset-0 rounded-full blur-lg bg-white/20 pointer-events-none"
                                        />
                                        <Button
                                            onClick={handleSend}
                                            disabled={!input.trim() || isLoading}
                                            className="relative h-full px-7 bg-white text-black hover:bg-gray-100 rounded-full disabled:opacity-30"
                                        >
                                            {isLoading ? (
                                                <div className="animate-spin h-5 w-5 border-2 border-black border-t-transparent rounded-full" />
                                            ) : (
                                                <Send className="h-5 w-5" />
                                            )}
                                        </Button>
                                    </div>
                                </motion.div>
                            </div>
                        </motion.div>
                    </div>

                    {/* Context Section */}
                    <div className="space-y-5 flex flex-col min-h-0">
                        {/* Resume PDF Preview - Expandable */}
                        <motion.div
                            initial={{ opacity: 0, x: 30, rotateY: 20 }}
                            animate={{ opacity: 1, x: 0, rotateY: 0 }}
                            transition={{ delay: 0.2 }}
                            whileHover={{ scale: 1.03, rotateY: -5 }}
                            className="relative flex-1 flex flex-col min-h-0"
                            style={{ transformStyle: 'preserve-3d' }}
                        >
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
                                className="absolute -inset-[2px] rounded-3xl opacity-40"
                                style={{
                                    background: 'linear-gradient(120deg, rgba(255,255,255,0.25), transparent, rgba(255,255,255,0.25))',
                                }}
                            />

                            <div className="relative bg-black/50 backdrop-blur-3xl border border-white/20 rounded-3xl p-5 overflow-hidden flex flex-col min-h-0">
                                <motion.div
                                    className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-3xl pointer-events-none"
                                    animate={{
                                        scale: [1, 1.2, 1],
                                        opacity: [0.3, 0.5, 0.3]
                                    }}
                                    transition={{ duration: 3, repeat: Infinity }}
                                />

                                <motion.button
                                    whileHover={{ opacity: 0.8 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={() => setResumeExpanded(!resumeExpanded)}
                                    className="relative z-10 w-full flex items-center justify-between mb-3 flex-shrink-0"
                                >
                                    <div className="flex items-center gap-3">
                                        <motion.div
                                            animate={{ scale: [1, 1.3, 1] }}
                                            transition={{ duration: 2, repeat: Infinity }}
                                            className="w-2 h-2 bg-white rounded-full"
                                        />
                                        <h3 className="text-white tracking-widest text-xs uppercase">Resume</h3>
                                        <motion.span
                                            className="px-2 py-1 bg-white/20 text-white text-xs rounded-full backdrop-blur-sm"
                                        >
                                            PDF
                                        </motion.span>
                                    </div>
                                    <motion.div
                                        animate={{ rotate: resumeExpanded ? 0 : -180 }}
                                        transition={{ type: "spring", stiffness: 300 }}
                                    >
                                        <ChevronDown className="h-5 w-5 text-gray-400" />
                                    </motion.div>
                                </motion.button>

                                <AnimatePresence>
                                    {resumeExpanded && (
                                        <motion.div
                                            initial={{ opacity: 0, height: 0 }}
                                            animate={{ opacity: 1, height: "auto" }}
                                            exit={{ opacity: 0, height: 0 }}
                                            transition={{ duration: 0.3 }}
                                            className="relative z-10 flex-1 overflow-y-auto min-h-0"
                                        >
                                            <div className="bg-gradient-to-br from-white/8 to-white/3 border border-white/10 rounded-2xl p-6">
                                                {isLoadingResume ? (
                                                    <div className="flex items-center justify-center py-8">
                                                        <div className="animate-spin h-8 w-8 border-2 border-white border-t-transparent rounded-full" />
                                                    </div>
                                                ) : sessionData.hasResume ? (
                                                    <div className="bg-white/5 rounded-lg p-6 text-center">
                                                        <p className="text-gray-400">{resumeText}</p>
                                                    </div>
                                                ) : (
                                                    <div className="bg-white/5 rounded-lg p-6 text-center">
                                                        <p className="text-gray-400">No resume uploaded</p>
                                                    </div>
                                                )}
                                            </div>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        </motion.div>

                        {/* Keywords - Expandable Box */}
                        <motion.div
                            initial={{ opacity: 0, x: 30, rotateY: 20 }}
                            animate={{ opacity: 1, x: 0, rotateY: 0 }}
                            transition={{ delay: 0.3 }}
                            whileHover={{ scale: 1.03, rotateY: -5 }}
                            className="relative flex-1 flex flex-col min-h-0"
                            style={{ transformStyle: 'preserve-3d' }}
                        >
                            <motion.div
                                animate={{ rotate: -360 }}
                                transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                                className="absolute -inset-[2px] rounded-3xl opacity-40"
                                style={{
                                    background: 'linear-gradient(240deg, rgba(255,255,255,0.25), transparent, rgba(255,255,255,0.25))',
                                }}
                            />

                            <div className="relative bg-black/50 backdrop-blur-3xl border border-white/20 rounded-3xl p-5 overflow-hidden flex flex-col min-h-0">
                                <motion.div
                                    className="absolute bottom-0 left-0 w-32 h-32 bg-white/10 rounded-full blur-3xl pointer-events-none"
                                    animate={{
                                        scale: [1, 1.3, 1],
                                        opacity: [0.2, 0.4, 0.2]
                                    }}
                                    transition={{ duration: 4, repeat: Infinity }}
                                />

                                <motion.button
                                    whileHover={{ opacity: 0.8 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={() => setKeywordsExpanded(!keywordsExpanded)}
                                    className="relative z-10 w-full flex items-center justify-between mb-3 flex-shrink-0"
                                >
                                    <div className="flex items-center gap-3">
                                        <motion.div
                                            animate={{ scale: [1, 1.3, 1] }}
                                            transition={{ duration: 2, repeat: Infinity, delay: 0.3 }}
                                            className="w-2 h-2 bg-white rounded-full"
                                        />
                                        <h3 className="text-white tracking-widest text-xs uppercase">Requirements</h3>
                                        <motion.span
                                            key={keywords.length}
                                            initial={{ scale: 1.5, opacity: 0, y: -10 }}
                                            animate={{ scale: 1, opacity: 1, y: 0 }}
                                            className="px-2 py-1 bg-white/20 text-white text-xs rounded-full backdrop-blur-sm"
                                        >
                                            {keywords.length}
                                        </motion.span>
                                    </div>
                                    <motion.div
                                        animate={{ rotate: keywordsExpanded ? 0 : -180 }}
                                        transition={{ type: "spring", stiffness: 300 }}
                                    >
                                        <ChevronDown className="h-5 w-5 text-gray-400" />
                                    </motion.div>
                                </motion.button>

                                <AnimatePresence>
                                    {keywordsExpanded && (
                                        <motion.ul
                                            initial={{ opacity: 0, height: 0 }}
                                            animate={{ opacity: 1, height: "auto" }}
                                            exit={{ opacity: 0, height: 0 }}
                                            transition={{ duration: 0.3 }}
                                            className="relative z-10 space-y-3 overflow-y-auto flex-1 min-h-0"
                                        >
                                            <AnimatePresence mode="popLayout">
                                                {keywords.map((keyword, index) => (
                                                    <motion.li
                                                        key={keyword.id}
                                                        initial={{ opacity: 0, x: -20, scale: 0.9 }}
                                                        animate={{ opacity: 1, x: 0, scale: 1 }}
                                                        exit={{ opacity: 0, x: 20, scale: 0.9 }}
                                                        transition={{
                                                            delay: index * 0.08,
                                                            type: "spring",
                                                            stiffness: 300
                                                        }}
                                                        className="relative"
                                                    >
                                                        <motion.div
                                                            whileHover={{ x: 6, scale: 1.02 }}
                                                            className="relative bg-gradient-to-r from-white/8 to-white/5 rounded-2xl p-4 border border-white/10 overflow-hidden group"
                                                        >
                                                            {/* Shimmer on hover */}
                                                            <motion.div
                                                                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 group-hover:opacity-100 pointer-events-none"
                                                                animate={{
                                                                    x: ['-100%', '100%'],
                                                                }}
                                                                transition={{ duration: 1.5, repeat: Infinity }}
                                                            />

                                                            <p className="text-white text-sm mb-1 relative z-10">{keyword.title}</p>
                                                            <p className="text-gray-400 text-xs leading-relaxed relative z-10">{keyword.description}</p>
                                                        </motion.div>
                                                    </motion.li>
                                                ))}
                                            </AnimatePresence>
                                        </motion.ul>
                                    )}
                                </AnimatePresence>
                            </div>
                        </motion.div>
                    </div>
                </div>
            </div>
        </div>
    );
}