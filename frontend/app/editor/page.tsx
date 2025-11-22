"use client"
import TiptapEditor from '@/components/Editor';
import { useState } from 'react';

export default function page() {
  const [content, setContent] = useState('# Hello World\n\nThis is my content.');

  return (
    <div className="h-screen w-screen">
      <TiptapEditor
        initialMarkdown={content}
        onChange={(newMarkdown) => {
          setContent(newMarkdown);
          // or save to API, etc.
        }}
      />
    </div>
  );
}