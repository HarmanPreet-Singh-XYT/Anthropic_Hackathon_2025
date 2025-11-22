"use client"
import React, { useEffect, useState, useCallback } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import Underline from '@tiptap/extension-underline';
import Link from '@tiptap/extension-link';
import Image from '@tiptap/extension-image';
import Youtube from '@tiptap/extension-youtube';
import CharacterCount from '@tiptap/extension-character-count';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { common, createLowlight } from 'lowlight';
import { 
  Bold, Italic, Underline as UnderlineIcon, Strikethrough, Code, 
  List, ListOrdered, Quote, Heading1, Heading2, 
  CheckSquare, Eye, Edit3, Terminal, Undo, Redo, 
  Image as ImageIcon, Youtube as YoutubeIcon, Minus, Copy, Check
} from 'lucide-react';

const lowlight = createLowlight(common);

interface MenuButtonProps {
  onClick: () => void;
  isActive?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  title: string;
}

const MenuButton: React.FC<MenuButtonProps> = ({ onClick, isActive = false, disabled = false, children, title }) => (
  <button
    onClick={onClick}
    disabled={disabled}
    title={title}
    className={`
      p-1.5 rounded-lg transition-all duration-200 ease-in-out flex items-center justify-center
      ${disabled ? 'opacity-30 cursor-not-allowed' : ''}
      ${isActive 
        ? 'bg-indigo-500/20 text-indigo-300 ring-1 ring-indigo-500/50' 
        : 'text-gray-400 hover:bg-white/10 hover:text-gray-200'
      }
    `}
  >
    {children}
  </button>
);

const Separator = () => <div className="w-px h-4 bg-gray-700 mx-1 self-center" />;

// HTML to Markdown converter
const htmlToMarkdown = (html: string): string => {
  let md = html;
  md = md.replace(/<h1[^>]*>(.*?)<\/h1>/gi, '# $1\n\n');
  md = md.replace(/<h2[^>]*>(.*?)<\/h2>/gi, '## $1\n\n');
  md = md.replace(/<h3[^>]*>(.*?)<\/h3>/gi, '### $1\n\n');
  md = md.replace(/<strong>(.*?)<\/strong>/gi, '**$1**');
  md = md.replace(/<b>(.*?)<\/b>/gi, '**$1**');
  md = md.replace(/<em>(.*?)<\/em>/gi, '*$1*');
  md = md.replace(/<i>(.*?)<\/i>/gi, '*$1*');
  md = md.replace(/<u>(.*?)<\/u>/gi, '__$1__');
  md = md.replace(/<s>(.*?)<\/s>/gi, '~~$1~~');
  md = md.replace(/<code[^>]*>(.*?)<\/code>/gi, '`$1`');
  md = md.replace(/<pre><code[^>]*>([\s\S]*?)<\/code><\/pre>/gi, '```\n$1\n```\n\n');
  md = md.replace(/<blockquote><p>(.*?)<\/p><\/blockquote>/gi, '> $1\n\n');
  md = md.replace(/<li data-type="taskItem" data-checked="true"[^>]*>.*?<p>(.*?)<\/p>.*?<\/li>/gi, '- [x] $1\n');
  md = md.replace(/<li data-type="taskItem" data-checked="false"[^>]*>.*?<p>(.*?)<\/p>.*?<\/li>/gi, '- [ ] $1\n');
  md = md.replace(/<li><p>(.*?)<\/p><\/li>/gi, '- $1\n');
  md = md.replace(/<ul[^>]*>/gi, '');
  md = md.replace(/<\/ul>/gi, '\n');
  md = md.replace(/<ol>/gi, '');
  md = md.replace(/<\/ol>/gi, '\n');
  md = md.replace(/<img[^>]*src="([^"]*)"[^>]*>/gi, '![Image]($1)\n\n');
  md = md.replace(/<div data-youtube-video[^>]*><iframe[^>]*src="([^"]*)"[^>]*><\/iframe><\/div>/gi, '[YouTube Video]($1)\n\n');
  md = md.replace(/<hr\s*\/?>/gi, '---\n\n');
  md = md.replace(/<p>(.*?)<\/p>/gi, '$1\n\n');
  md = md.replace(/<[^>]+>/g, '');
  md = md.replace(/&nbsp;/g, ' ');
  md = md.replace(/\n{3,}/g, '\n\n');
  return md.trim();
};

// Markdown to HTML converter
const markdownToHtml = (md: string): string => {
  let html = md;
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__(.+?)__/g, '<u>$1</u>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  html = html.replace(/~~(.+?)~~/g, '<s>$1</s>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  html = html.replace(/```\n?([\s\S]*?)\n?```/g, '<pre><code>$1</code></pre>');
  html = html.replace(/^> (.+)$/gm, '<blockquote><p>$1</p></blockquote>');
  html = html.replace(/^- \[x\] (.+)$/gm, '<ul data-type="taskList"><li data-type="taskItem" data-checked="true"><label><input type="checkbox" checked></label><div><p>$1</p></div></li></ul>');
  html = html.replace(/^- \[ \] (.+)$/gm, '<ul data-type="taskList"><li data-type="taskItem" data-checked="false"><label><input type="checkbox"></label><div><p>$1</p></div></li></ul>');
  html = html.replace(/^- (.+)$/gm, '<ul><li><p>$1</p></li></ul>');
  html = html.replace(/!\[.*?\]\((.+?)\)/g, '<img src="$1">');
  html = html.replace(/^---$/gm, '<hr>');
  html = html.replace(/^(?!<[hupob]|<li|<hr|<img|<pre|<code)(.+)$/gm, '<p>$1</p>');
  html = html.replace(/<\/ul>\s*<ul>/g, '');
  return html;
};

interface TiptapEditorProps {
  initialMarkdown?: string;
  onChange?: (markdown: string) => void;
  className?: string;
}

export default function TiptapEditor({ initialMarkdown = '', onChange, className = '' }: TiptapEditorProps) {
  const [showMarkdown, setShowMarkdown] = useState<boolean>(false);
  const [markdown, setMarkdown] = useState<string>(initialMarkdown);
  const [copied, setCopied] = useState(false);

  const handleUpdate = useCallback((newMarkdown: string) => {
    setMarkdown(newMarkdown);
    onChange?.(newMarkdown);
  }, [onChange]);

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        codeBlock: false,
        heading: { levels: [1, 2, 3] },
      }),
      Placeholder.configure({
        placeholder: ({ node }) => {
          if (node.type.name === 'heading') return `Heading ${node.attrs.level}`;
          return "Type '/' for commands or start writing...";
        },
      }),
      TaskList,
      TaskItem.configure({ nested: true }),
      Underline,
      Link.configure({ 
        openOnClick: false,
        HTMLAttributes: { class: 'text-indigo-400 hover:text-indigo-300 underline cursor-pointer' }
      }),
      Image.configure({
        inline: true,
        allowBase64: true,
        HTMLAttributes: { class: 'rounded-lg border border-gray-700 shadow-lg my-4 max-w-full' },
      }),
      Youtube.configure({
        controls: false,
        nocookie: true,
        HTMLAttributes: { class: 'w-full aspect-video rounded-lg border border-gray-700 shadow-lg my-4' },
      }),
      CharacterCount,
      CodeBlockLowlight.configure({ lowlight }),
    ],
    content: initialMarkdown ? markdownToHtml(initialMarkdown) : '',
    editorProps: {
      attributes: {
        class: 'prose prose-lg prose-invert max-w-none focus:outline-none h-full px-2',
      },
    },
    onUpdate: ({ editor }) => {
      const html = editor.getHTML();
      const newMd = htmlToMarkdown(html);
      handleUpdate(newMd);
    },
    immediatelyRender: false
  });

  useEffect(() => {
    if (editor && initialMarkdown !== markdown) {
      const currentMd = htmlToMarkdown(editor.getHTML());
      if (currentMd !== initialMarkdown) {
        editor.commands.setContent(markdownToHtml(initialMarkdown));
        setMarkdown(initialMarkdown);
      }
    }
  }, [initialMarkdown]);

  const addImage = () => {
    const url = window.prompt('Enter the URL of the image:');
    if (url && editor) editor.chain().focus().setImage({ src: url }).run();
  };

  const addYoutube = () => {
    const url = window.prompt('Enter YouTube URL:');
    if (url && editor) editor.commands.setYoutubeVideo({ src: url });
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!editor) return null;

  return (
    <div className={`h-full w-full bg-neutral-950 text-gray-100 font-sans selection:bg-indigo-500/30 flex flex-col ${className}`}>
      {/* Toolbar */}
      <div className="flex-shrink-0 p-2">
        <div className="bg-neutral-900/90 backdrop-blur-xl border border-neutral-800 rounded-xl shadow-2xl shadow-black/50 p-1.5 flex flex-wrap items-center gap-1">
          <div className="flex items-center gap-0.5 pr-1">
            <MenuButton onClick={() => editor.chain().focus().undo().run()} disabled={!editor.can().undo()} title="Undo">
              <Undo size={16} />
            </MenuButton>
            <MenuButton onClick={() => editor.chain().focus().redo().run()} disabled={!editor.can().redo()} title="Redo">
              <Redo size={16} />
            </MenuButton>
          </div>
          <Separator />
          <div className="flex items-center gap-0.5">
            <MenuButton onClick={() => editor.chain().focus().toggleBold().run()} isActive={editor.isActive('bold')} title="Bold">
              <Bold size={16} />
            </MenuButton>
            <MenuButton onClick={() => editor.chain().focus().toggleItalic().run()} isActive={editor.isActive('italic')} title="Italic">
              <Italic size={16} />
            </MenuButton>
            <MenuButton onClick={() => editor.chain().focus().toggleUnderline().run()} isActive={editor.isActive('underline')} title="Underline">
              <UnderlineIcon size={16} />
            </MenuButton>
            <MenuButton onClick={() => editor.chain().focus().toggleStrike().run()} isActive={editor.isActive('strike')} title="Strike">
              <Strikethrough size={16} />
            </MenuButton>
            <MenuButton onClick={() => editor.chain().focus().toggleCode().run()} isActive={editor.isActive('code')} title="Inline Code">
              <Code size={16} />
            </MenuButton>
          </div>
          <Separator />
          <div className="flex items-center gap-0.5">
            <MenuButton onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()} isActive={editor.isActive('heading', { level: 1 })} title="H1">
              <Heading1 size={16} />
            </MenuButton>
            <MenuButton onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()} isActive={editor.isActive('heading', { level: 2 })} title="H2">
              <Heading2 size={16} />
            </MenuButton>
          </div>
          <Separator />
          <div className="flex items-center gap-0.5">
            <MenuButton onClick={() => editor.chain().focus().toggleBulletList().run()} isActive={editor.isActive('bulletList')} title="Bullet List">
              <List size={16} />
            </MenuButton>
            <MenuButton onClick={() => editor.chain().focus().toggleOrderedList().run()} isActive={editor.isActive('orderedList')} title="Numbered List">
              <ListOrdered size={16} />
            </MenuButton>
            <MenuButton onClick={() => editor.chain().focus().toggleTaskList().run()} isActive={editor.isActive('taskList')} title="Task List">
              <CheckSquare size={16} />
            </MenuButton>
            <MenuButton onClick={() => editor.chain().focus().toggleBlockquote().run()} isActive={editor.isActive('blockquote')} title="Quote">
              <Quote size={16} />
            </MenuButton>
            <MenuButton onClick={() => editor.chain().focus().toggleCodeBlock().run()} isActive={editor.isActive('codeBlock')} title="Code Block">
              <Terminal size={16} />
            </MenuButton>
          </div>
          <Separator />
          <div className="flex items-center gap-0.5">
            <MenuButton onClick={addImage} title="Add Image">
              <ImageIcon size={16} />
            </MenuButton>
            <MenuButton onClick={addYoutube} title="Add YouTube">
              <YoutubeIcon size={16} />
            </MenuButton>
            <MenuButton onClick={() => editor.chain().focus().setHorizontalRule().run()} title="Divider">
              <Minus size={16} />
            </MenuButton>
          </div>
          <div className="flex-1" />
          <button
            onClick={() => setShowMarkdown(!showMarkdown)}
            className={`px-3 py-1.5 rounded-lg flex items-center gap-2 text-xs font-bold tracking-wide uppercase transition-all
              ${showMarkdown 
                ? 'bg-indigo-600 text-white ring-2 ring-indigo-500 ring-offset-2 ring-offset-neutral-900' 
                : 'bg-neutral-800 text-neutral-400 hover:bg-neutral-700'}`}
          >
            {showMarkdown ? <Edit3 size={14} /> : <Eye size={14} />}
            {showMarkdown ? 'Editor' : 'Source'}
          </button>
        </div>
      </div>

      {/* Editor Container */}
      <div className="flex-1 min-h-0 px-2 pb-2 flex flex-col">
        <div className="flex-1 min-h-0 bg-neutral-900 rounded-xl border border-neutral-800 shadow-xl overflow-hidden flex flex-col">
          {showMarkdown ? (
            <div className="h-full flex flex-col bg-[#0d0d0d]">
              <div className="flex-shrink-0 flex items-center justify-between px-6 py-3 border-b border-neutral-800 bg-neutral-900/50">
                <span className="text-xs font-mono text-neutral-500">MARKDOWN PREVIEW</span>
                <button 
                  onClick={handleCopy}
                  className="flex items-center gap-2 text-xs font-medium text-neutral-400 hover:text-white transition-colors"
                >
                  {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
                  {copied ? 'Copied!' : 'Copy MD'}
                </button>
              </div>
              <div className="flex-1 min-h-0 p-8 overflow-auto">
                <pre className="font-mono text-sm text-gray-300 whitespace-pre-wrap leading-relaxed">{markdown}</pre>
              </div>
            </div>
          ) : (
            <div className="flex-1 min-h-0 p-8 md:p-12 overflow-auto">
              <EditorContent editor={editor} className="h-full" />
            </div>
          )}
        </div>
        <div className="flex-shrink-0 flex justify-end gap-4 mt-2 px-2 text-xs font-mono text-neutral-600">
          <span>{editor.storage.characterCount.words()} words</span>
          <span>{editor.storage.characterCount.characters()} chars</span>
        </div>
      </div>

      <style>{`
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #171717; }
        ::-webkit-scrollbar-thumb { background: #404040; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #525252; }
        .ProseMirror { min-height: 100%; outline: none; }
        .ProseMirror p.is-editor-empty:first-child::before {
          color: #525252; content: attr(data-placeholder); float: left; height: 0; pointer-events: none;
        }
        ul[data-type="taskList"] { list-style: none; padding: 0; }
        ul[data-type="taskList"] li { display: flex; gap: 0.5rem; margin-bottom: 0.5rem; }
        ul[data-type="taskList"] li > label { margin-top: 0.25em; flex-shrink: 0; }
        ul[data-type="taskList"] li > label input { 
          appearance: none; background-color: #262626; width: 1.2em; height: 1.2em; 
          border: 1px solid #525252; border-radius: 4px; cursor: pointer; display: grid; place-content: center;
        }
        ul[data-type="taskList"] li > label input::before {
          content: ""; width: 0.65em; height: 0.65em; transform: scale(0);
          background-color: #818cf8; clip-path: polygon(14% 44%, 0 65%, 50% 100%, 100% 16%, 80% 0%, 43% 62%);
          transition: 120ms transform ease-in-out;
        }
        ul[data-type="taskList"] li > label input:checked::before { transform: scale(1); }
        ul[data-type="taskList"] li[data-checked="true"] > div > p { text-decoration: line-through; color: #525252; }
        pre { background: #0a0a0a !important; border: 1px solid #262626; border-radius: 0.5rem; padding: 1rem; }
        code { color: inherit; background: none; }
        p > code, li > code { 
          background: #262626; color: #e2e8f0; padding: 0.2rem 0.4rem; 
          border-radius: 0.25rem; font-size: 0.85em; border: 1px solid #404040;
        }
        blockquote {
          border-left: 3px solid #6366f1; background: linear-gradient(to right, #1e1e2e, transparent);
          padding: 0.5rem 1rem; color: #9ca3af;
        }
        img { transition: all 0.2s; }
        img.ProseMirror-selectednode { outline: 3px solid #6366f1; }
      `}</style>
    </div>
  );
}