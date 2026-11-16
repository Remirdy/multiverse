import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { CodeBlock } from './CodeBlock';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <div className="prose prose-invert prose-sm max-w-none text-slate-200 leading-relaxed space-y-2">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            const value = String(children).replace(/\n$/, '');
            if (!inline && (match || value.includes('\n'))) {
              return <CodeBlock language={match ? match[1] : undefined} value={value} />;
            }
            return (
              <code
                className="bg-space-850 text-cyan-300 font-mono text-[12px] px-1.5 py-0.5 rounded border border-slate-800"
                {...props}
              >
                {children}
              </code>
            );
          },
          p({ children }) {
            return <p className="mb-2.5 last:mb-0 text-slate-300 text-sm leading-relaxed">{children}</p>;
          },
          h1({ children }) {
            return <h1 className="text-lg font-semibold text-slate-100 mt-4 mb-2">{children}</h1>;
          },
          h2({ children }) {
            return <h2 className="text-base font-semibold text-slate-100 mt-3 mb-1.5">{children}</h2>;
          },
          h3({ children }) {
            return <h3 className="text-sm font-semibold text-slate-200 mt-2 mb-1">{children}</h3>;
          },
          ul({ children }) {
            return <ul className="list-disc list-outside pl-5 mb-2.5 space-y-1 text-slate-300 text-sm">{children}</ul>;
          },
          ol({ children }) {
            return <ol className="list-decimal list-outside pl-5 mb-2.5 space-y-1 text-slate-300 text-sm">{children}</ol>;
          },
          li({ children }) {
            return <li className="text-slate-300">{children}</li>;
          },
          blockquote({ children }) {
            return (
              <blockquote className="border-l-2 border-brand-indigo/60 pl-3 italic text-slate-400 my-2 text-sm bg-space-900/40 py-1 rounded-r">
                {children}
              </blockquote>
            );
          },
          table({ children }) {
            return (
              <div className="overflow-x-auto my-3 rounded border border-slate-700/60">
                <table className="min-w-full divide-y divide-slate-700/60 text-xs text-left">
                  {children}
                </table>
              </div>
            );
          },
          th({ children }) {
            return <th className="px-3 py-2 bg-space-850 font-semibold text-slate-200">{children}</th>;
          },
          td({ children }) {
            return <td className="px-3 py-1.5 border-t border-slate-800/80 text-slate-300">{children}</td>;
          },
          a({ href, children }) {
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-cyan-400 hover:text-cyan-300 underline underline-offset-2 transition-colors"
              >
                {children}
              </a>
            );
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};
