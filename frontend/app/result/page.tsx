"use client"
import React, { useState, useEffect, useCallback } from 'react';
import { Sparkles, FileDown, Copy, Check, Loader2, RefreshCw } from 'lucide-react';

function cn(...inputs) {
  return inputs.filter(Boolean).join(' ');
}

const GrainTexture = () => (
  <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden opacity-[0.03]">
    <svg className="h-full w-full">
      <filter id="noise">
        <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="3" stitchTiles="stitch" />
      </filter>
      <rect width="100%" height="100%" filter="url(#noise)" />
    </svg>
  </div>
);

const SpotlightCard = ({ title, children, className = "", status }) => {
  const [mouse, setMouse] = useState({ x: 0, y: 0 });
  const [hovered, setHovered] = useState(false);

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setMouse({ x: e.clientX - rect.left, y: e.clientY - rect.top });
  };

  return (
    <div
      className={cn("group relative border border-white/10 bg-neutral-900/50 overflow-hidden rounded-2xl transition-all duration-500", className)}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {hovered && (
        <div
          className="pointer-events-none absolute -inset-px rounded-2xl transition duration-300"
          style={{
            background: `radial-gradient(650px circle at ${mouse.x}px ${mouse.y}px, rgba(255,255,255,0.08), transparent 40%)`
          }}
        />
      )}
      
      <div className="relative h-full flex flex-col p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="relative flex h-2 w-2 items-center justify-center">
              <div className={cn(
                "absolute h-full w-full rounded-full",
                status === 'loading' ? "animate-ping bg-amber-400 opacity-40" :
                status === 'success' ? "bg-emerald-400 opacity-40" :
                "animate-ping bg-white opacity-20"
              )} />
              <div className={cn(
                "h-1.5 w-1.5 rounded-full",
                status === 'loading' ? "bg-amber-400" :
                status === 'success' ? "bg-emerald-400" : "bg-white"
              )} />
            </div>
            <span className="text-[10px] font-bold tracking-[0.15em] text-neutral-400 uppercase">
              {title}
            </span>
          </div>
          {status === 'loading' && (
            <Loader2 className="w-3 h-3 text-neutral-500 animate-spin" />
          )}
        </div>
        <div className="flex-1 relative z-10 min-h-0">{children}</div>
      </div>
    </div>
  );
};

const EssayArea = ({ text, isLoading }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    if (text) {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (isLoading && !text) {
    return (
      <div className="h-full bg-black/40 rounded-xl border border-white/5 flex items-center justify-center">
        <div className="flex flex-col items-center gap-2">
          <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
          <span className="text-xs text-neutral-500">Fetching essay...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="relative h-full bg-black/40 rounded-xl border border-white/5 overflow-hidden flex flex-col">
      <div className="absolute top-0 left-0 w-full h-16 bg-gradient-to-b from-white/5 to-transparent pointer-events-none z-10" />
      
      {text && (
        <button
          onClick={handleCopy}
          className="absolute top-2 right-2 z-20 p-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-all group"
        >
          {copied ? (
            <Check className="w-3.5 h-3.5 text-emerald-400" />
          ) : (
            <Copy className="w-3.5 h-3.5 text-neutral-400 group-hover:text-white transition-colors" />
          )}
        </button>
      )}
      
      <div className="p-4 flex-1 overflow-auto">
        {text ? (
          <p className="text-sm text-neutral-300 leading-relaxed whitespace-pre-wrap">{text}</p>
        ) : (
          <div className="text-sm text-neutral-500">
            Your essay will appear here...
            <span className="inline-block w-[2px] h-4 ml-1 align-middle bg-indigo-500/50 animate-pulse" />
          </div>
        )}
      </div>
    </div>
  );
};

const PDFPreview = ({ pdfData, isLoading }) => {
  if (isLoading && !pdfData) {
    return (
      <div className="h-full bg-black/40 rounded-xl border border-white/5 flex items-center justify-center">
        <div className="flex flex-col items-center gap-2">
          <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
          <span className="text-xs text-neutral-500">Loading resume...</span>
        </div>
      </div>
    );
  }

  if (!pdfData) {
    return (
      <div className="h-full bg-black/40 rounded-xl border border-white/5 p-4">
        <div className="text-sm text-neutral-500 font-mono">
          Your resume will appear here...
          <span className="inline-block w-[2px] h-4 ml-1 align-middle bg-indigo-500/50 animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className="h-full bg-white rounded-xl overflow-hidden shadow-2xl flex flex-col">
      <div className="flex-1 overflow-auto p-5">
        <div className="space-y-4">
          <div className="border-b-2 border-gray-800 pb-3">
            <h2 className="text-lg font-bold text-gray-900">{pdfData.name || 'John Doe'}</h2>
            <p className="text-sm text-gray-600">{pdfData.title || 'Software Engineer'}</p>
            <p className="text-xs text-gray-500 mt-1">{pdfData.email || 'john@example.com'} • {pdfData.phone || '(555) 123-4567'}</p>
          </div>
          
          {pdfData.sections?.map((section, i) => (
            <div key={i}>
              <h3 className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-1.5">{section.title}</h3>
              <p className="text-xs text-gray-600 leading-relaxed">{section.content}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

const ApplicationUI = () => {
  const [essayText, setEssayText] = useState('');
  const [pdfData, setPdfData] = useState(null);
  const [isPolling, setIsPolling] = useState(true);
  const [status, setStatus] = useState({ essay: 'idle', resume: 'idle' });

  const mockApiResponse = useCallback(() => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          essay: `Throughout my academic journey, I have consistently demonstrated a passion for innovation and problem-solving. My experience spans across multiple disciplines, from software engineering to data science, where I've contributed to projects that have made meaningful impacts.

During my internship at a leading tech company, I led a team of three to develop an AI-powered recommendation system that improved user engagement by 40%. This experience taught me the importance of collaboration and iterative development.

Beyond technical skills, I believe in the power of continuous learning. I regularly participate in hackathons and open-source projects, staying current with emerging technologies while giving back to the community.

I am excited about the opportunity to bring my unique perspective and skills to your program, where I hope to further develop my abilities while contributing to groundbreaking research.`,
          resume: {
            name: 'Alex Johnson',
            title: 'Full Stack Developer',
            email: 'alex.johnson@email.com',
            phone: '(555) 987-6543',
            sections: [
              { title: 'Experience', content: 'Senior Developer at TechCorp (2022-Present) - Led development of microservices architecture serving 1M+ users. Software Engineer at StartupXYZ (2020-2022) - Built React applications and REST APIs.' },
              { title: 'Education', content: 'M.S. Computer Science, Stanford University (2020). B.S. Computer Science, UC Berkeley (2018). GPA: 3.9/4.0' },
              { title: 'Skills', content: 'React, TypeScript, Node.js, Python, AWS, Docker, Kubernetes, PostgreSQL, MongoDB, GraphQL' }
            ]
          }
        });
      }, 2000);
    });
  }, []);

  useEffect(() => {
    if (!isPolling) return;

    const pollApi = async () => {
      setStatus({ essay: 'loading', resume: 'loading' });
      
      try {
        const data = await mockApiResponse();
        
        if (data.essay) {
          setEssayText(data.essay);
          setStatus(s => ({ ...s, essay: 'success' }));
        }
        if (data.resume) {
          setPdfData(data.resume);
          setStatus(s => ({ ...s, resume: 'success' }));
        }
        
        setIsPolling(false);
      } catch (err) {
        console.error('Polling error:', err);
        setTimeout(pollApi, 3000);
      }
    };

    pollApi();
  }, [isPolling, mockApiResponse]);

  const handleExportPDF = () => {
    if (!pdfData) return;
    
    const content = `${pdfData.name}\n${pdfData.title}\n${pdfData.email} | ${pdfData.phone}\n\n` +
      pdfData.sections?.map(s => `${s.title.toUpperCase()}\n${s.content}`).join('\n\n');
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'resume.pdf';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleRefresh = () => {
    setEssayText('');
    setPdfData(null);
    setStatus({ essay: 'idle', resume: 'idle' });
    setIsPolling(true);
  };

  return (
    <div className="h-screen bg-[#030303] text-white flex flex-col overflow-hidden font-sans">
      <GrainTexture />

      {/* Background Glows */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-indigo-500/10 blur-[120px] rounded-full pointer-events-none z-0" />
      <div className="fixed bottom-0 left-0 w-[400px] h-[400px] bg-rose-500/5 blur-[120px] rounded-full pointer-events-none z-0" />

      {/* Header - Compact */}
      <div className="relative z-10 flex items-center justify-center gap-3 py-4 shrink-0">
        <div className="relative group cursor-default">
          <div className="absolute inset-0 bg-white/20 blur-xl rounded-full opacity-50 group-hover:opacity-80 transition-opacity" />
          <Sparkles className="w-6 h-6 text-white relative z-10 drop-shadow-[0_0_10px_rgba(255,255,255,0.5)]" strokeWidth={1.5} />
        </div>
        <h1 className="text-xl font-medium tracking-tight bg-clip-text text-transparent bg-gradient-to-b from-white via-white to-white/40">
          Your Application
        </h1>
      </div>

      {/* Main Content - Takes remaining space */}
      <div className="flex-1 min-h-0 px-4 pb-4 relative z-10">
        <div className="h-full grid grid-cols-1 lg:grid-cols-2 gap-4">
          <SpotlightCard title="Essay" status={status.essay} className="h-full">
            <EssayArea text={essayText} isLoading={status.essay === 'loading'} />
          </SpotlightCard>
          
          <SpotlightCard title="Resume" status={status.resume} className="h-full">
            <PDFPreview pdfData={pdfData} isLoading={status.resume === 'loading'} />
          </SpotlightCard>
        </div>
      </div>

      {/* Action Bar - Fixed at bottom */}
      <div className="relative z-20 px-4 pb-4 shrink-0">
        <div className="group relative w-full h-14 rounded-xl border border-white/10 bg-[#080808] flex items-center justify-center gap-3 overflow-hidden">
          <div className="absolute bottom-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent" />
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-16 bg-white/5 blur-2xl rounded-full group-hover:bg-white/10 transition-colors duration-500" />

          <button
            onClick={handleRefresh}
            className="relative p-2 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 transition-all"
          >
            <RefreshCw className={cn("w-3.5 h-3.5 text-neutral-400", isPolling && "animate-spin")} />
          </button>

          <button
            onClick={handleExportPDF}
            disabled={!pdfData}
            className={cn(
              "relative overflow-hidden bg-white text-black px-5 py-2 rounded-full font-semibold text-sm flex items-center gap-2 transition-all duration-200 shadow-[0_0_30px_-10px_rgba(255,255,255,0.3)]",
              pdfData ? "hover:scale-[1.02] active:scale-[0.98]" : "opacity-50 cursor-not-allowed"
            )}
          >
            <FileDown className="w-3.5 h-3.5" strokeWidth={2.5} />
            <span>Export PDF</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ApplicationUI;