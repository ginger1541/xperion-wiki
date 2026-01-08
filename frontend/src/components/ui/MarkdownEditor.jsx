import React from 'react';
import { MarkdownViewer } from './MarkdownViewer';
import { cn } from '../../lib/utils';

export const MarkdownEditor = ({ content, onChange, className }) => {
    return (
        <div className={cn("grid grid-cols-1 md:grid-cols-2 gap-6 h-full", className)}>
            {/* Editor Pane */}
            <div className="flex flex-col h-full border border-border rounded-lg bg-surface overflow-hidden shadow-sm focus-within:ring-2 focus-within:ring-primary/20 transition-all">
                <div className="bg-sidebar px-4 py-2 border-b border-border text-xs font-semibold text-text-muted flex justify-between">
                    <span>MARKDOWN</span>
                    <span>Editor Mode</span>
                </div>
                <textarea
                    value={content}
                    onChange={(e) => onChange(e.target.value)}
                    className="flex-1 w-full p-4 resize-none outline-none font-mono text-sm leading-relaxed bg-transparent text-text-main"
                    placeholder="# 제목을 입력하세요..."
                    spellCheck="false"
                />
            </div>

            {/* Preview Pane */}
            <div className="flex flex-col h-full border border-border rounded-lg bg-surface overflow-hidden shadow-sm hidden md:flex">
                <div className="bg-sidebar px-4 py-2 border-b border-border text-xs font-semibold text-text-muted flex justify-between">
                    <span>PREVIEW</span>
                    <span>Live Render</span>
                </div>
                <div className="flex-1 overflow-y-auto p-8 bg-white">
                    <MarkdownViewer content={content} />
                </div>
            </div>
        </div>
    );
};
