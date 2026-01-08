import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import { cn } from '../../lib/utils';

export const MarkdownViewer = ({ content, className }) => {
    return (
        <div className={cn("prose prose-slate max-w-none prose-headings:font-bold prose-headings:text-text-main prose-p:text-text-main prose-a:text-primary prose-a:no-underline hover:prose-a:underline prose-strong:text-text-main prose-code:text-primary prose-code:bg-primary/5 prose-code:rounded prose-code:px-1 prose-code:py-0.5 prose-pre:bg-sidebar prose-th:bg-surfaceHover prose-th:text-text-main prose-td:text-text-main", className)}>
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeRaw]}
                components={{
                    // Custom components if needed
                    img: ({ node, ...props }) => (
                        <img {...props} className="rounded-lg border border-border bg-surfaceHover" alt={props.alt || ''} />
                    ),
                    table: ({ node, ...props }) => (
                        <div className="overflow-x-auto my-4 border border-border rounded-lg">
                            <table {...props} className="w-full text-sm text-left my-0" />
                        </div>
                    )
                }}
            >
                {content}
            </ReactMarkdown>
        </div>
    );
};
