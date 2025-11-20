"use client"
import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Upload, Link2 } from 'lucide-react';
import { useTheme } from '@/context/ThemeContext';
import ThemeToggle from '@/components/ThemeToggle';


export default function ScholarshipAssistant() {
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState<string>('');
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const { darkMode } = useTheme();

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

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
    if (droppedFile) {
      setFile(droppedFile);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleContinue = () => {
    if (file || url) {
      alert('Processing your application...');
    }
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-gray-50 to-gray-100 dark:from-black dark:to-black flex items-center justify-center p-4 transition-colors">
      <ThemeToggle/>

      <div className="w-full max-w-2xl">
        <div className="text-center mb-8 space-y-2">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
            Scholarship Application Assistant
          </h1>
          <p className="text-base text-gray-600 dark:text-gray-300">
            Upload your resume and provide scholarship details to get started
          </p>
        </div>

        <Card className="shadow-xl dark:bg-black dark:border-gray-700">
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="resume" className="text-base font-medium dark:text-gray-200">
                Resume Upload
              </Label>
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer hover:border-gray-400 dark:hover:border-gray-500 ${
                  isDragging 
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-950' 
                    : 'border-gray-300 bg-gray-50 dark:border-gray-700 dark:bg-gray-900'
                }`}
                onClick={() => document.getElementById('file-input')?.click()}
              >
                <input
                  id="file-input"
                  type="file"
                  className="hidden"
                  accept=".pdf,.doc,.docx,.tex"
                  onChange={handleFileSelect}
                />
                <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400 dark:text-gray-500" />
                <p className="text-gray-600 dark:text-gray-300 mb-1">
                  {file ? (
                    <span className="font-medium text-gray-900 dark:text-white">{file.name}</span>
                  ) : (
                    'Drag and drop your resume here, or click to browse'
                  )}
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Supports PDF, DOC, LaTeX
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="scholarship-url" className="text-base font-medium dark:text-gray-200">
                Scholarship URL
              </Label>
              <div className="relative">
                <Link2 className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
                <Input
                  id="scholarship-url"
                  type="url"
                  placeholder="https://example.com/scholarship"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="pl-10 h-12 dark:bg-black dark:border-gray-800 dark:text-white dark:placeholder-gray-400"
                />
              </div>
            </div>

            <Button
              onClick={handleContinue}
              disabled={!file && !url}
              className="w-full h-12 text-base font-medium dark:bg-gray-400 dark:hover:bg-gray-200"
            >
              Continue
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}