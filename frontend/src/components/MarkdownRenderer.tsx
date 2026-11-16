import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import { CodeBlock } from './CodeBlock';
import { CinemaPlayer } from './CinemaPlayer';

interface MarkdownRendererProps {
  content: string;
}

/**
 * Preprocesses LaTeX equations and formatting produced by LLMs to ensure standard KaTeX parsing:
 * - Normalizes \[ ... \] to $$ ... $$ (display math)
 * - Normalizes \( ... \) to $ ... $ (inline math)
 * - Converts raw bracketed matrix environments [ U = \begin{pmatrix} ... \end{pmatrix} ] to $$ ... $$
 * - Wraps naked LaTeX environments in $$ ... $$
 * - Fixes naked symbols like \to, \Omega, \approx outside math tags
 * - Fixes unclosed single dollar signs ($) on individual lines
 * - Fixes single-backslash row breaks in matrices to \\
 */
function preprocessLaTeX(content: string): string {
  if (!content) return '';

  let text = content;

  // 1. Convert standard LaTeX display math \[ ... \] to $$ ... $$
  text = text.replace(/\\\[([\s\S]*?)\\\]/g, (_, math) => `\n\n$$\n${math.trim()}\n$$\n\n`);

  // 2. Convert standard LaTeX inline math \( ... \) to $ ... $
  text = text.replace(/\\\(([\s\S]*?)\\\)/g, (_, math) => `$${math.trim()}$`);

  // 3. Convert square-bracketed display math like [ U = \begin{pmatrix} ... \end{pmatrix} ]
  // or [ \lambda_1 = 3, \lambda_2 = 1 ] or [ x = \frac{a}{b} ] (excluding markdown links [text](url))
  text = text.replace(
    /(?:^|(?<=[^\w\\]))\[\s*([^[\]\n]*?(?:\\begin|\\frac|\\sqrt|\\pmatrix|\\matrix|\\bmatrix|\\vmatrix|\\quad|\\alpha|\\beta|\\gamma|\\lambda|\\theta|\\pi|\\sum|\\int|\\partial|\\cdot|\\times|\\pm|\\mp|\\in|\\subset|\\mathbf|\\mathbb|\\det|\\sin|\\cos|\\tan)[\s\S]*?)\s*\](?!\()/g,
    (_, math) => `\n\n$$\n${math.trim()}\n$$\n\n`
  );

  // 4. Wrap any naked \begin{matrix/pmatrix/cases...} not already enclosed in $$
  text = text.replace(
    /(?<!\$\$[\s\S]*?)(\\begin\{(?:pmatrix|matrix|bmatrix|vmatrix|Vmatrix|cases|aligned|align|gather)\}[\s\S]*?\\end\{(?:pmatrix|matrix|bmatrix|vmatrix|Vmatrix|cases|aligned|align|gather)\})/g,
    (match) => `\n\n$$\n${match.trim()}\n$$\n\n`
  );

  // 5. Fix single backslash row separators inside matrix blocks to double backslashes
  text = text.replace(
    /(\\begin\{(?:pmatrix|matrix|bmatrix|vmatrix|Vmatrix)\}[\s\S]*?\\end\{(?:pmatrix|matrix|bmatrix|vmatrix|Vmatrix)\})/g,
    (match) => match.replace(/\\\s+(?=\\frac|[-0-9a-zA-Z\\])/g, '\\\\ ')
  );

  // 6. Wrap raw electronics & math symbols outside $...$ in math tags
  // Fix arrows like \to or \rightarrow
  text = text.replace(/(?<!\$)\\(?:to|rightarrow)(?!\$)/g, ' $\\to$ ');
  // Fix Ohm symbols like 5k\Omega, \Omega, M\Omega
  text = text.replace(/([0-9.]+)?\s*(?:k|M|m)?\\Omega/g, (match) => ` $${match.trim()}$ `);
  // Fix micro symbols like \muA, \muF outside math
  text = text.replace(/(?<!\$)\\(?:mu|micro)\s*(A|F|V|s)?(?!\$)/g, (_, unit) => ` $\\mu${unit ? `\\text{${unit}}` : ''}$ `);

  // 7. Fix ?=I2 query tags from circuit labelings
  text = text.replace(/\?=(I[0-9a-zA-Z_]+|V[0-9a-zA-Z_]+)/g, '($1 = ?)');

  // 8. Fix unclosed dollar signs across lines or at the end of cut-off responses
  const lines = text.split('\n');
  const fixedLines = lines.map((line) => {
    const matches = line.match(/(?<!\\)\$/g);
    if (matches && matches.length % 2 !== 0) {
      return line.trimEnd() + '$';
    }
    return line;
  });
  text = fixedLines.join('\n');

  // If entire text has odd number of dollar signs, append closing dollar
  const globalDollarMatches = text.match(/(?<!\\)\$/g);
  if (globalDollarMatches && globalDollarMatches.length % 2 !== 0) {
    text = text.trimEnd() + '$';
  }

  return text;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  const normalizedContent = useMemo(() => preprocessLaTeX(content), [content]);

  return (
    <div className="prose prose-invert prose-sm max-w-none text-slate-200 leading-relaxed space-y-2.5">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, [remarkMath, { singleDollarTextMath: true }]]}
        rehypePlugins={[rehypeRaw, [rehypeKatex, { output: 'htmlAndMathml', throwOnError: false }]]}
        components={{
          video({ node, ...props }: any) {
            return (
              <CinemaPlayer
                src={props.src}
                title="NVIDIA Cosmos WFM • 9:16 ARRI Cinema Preview"
                aspectRatio="9:16"
                durationSeconds={15}
              />
            );
          },
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
            return <p className="mb-2 last:mb-0 text-slate-200 text-sm leading-relaxed">{children}</p>;
          },
          h1({ children }) {
            return <h1 className="text-lg font-bold text-slate-100 mt-4 mb-2 border-b border-slate-800 pb-1">{children}</h1>;
          },
          h2({ children }) {
            return <h2 className="text-base font-semibold text-cyan-300 mt-3.5 mb-1.5">{children}</h2>;
          },
          h3({ children }) {
            return <h3 className="text-sm font-semibold text-slate-100 mt-2.5 mb-1">{children}</h3>;
          },
          ul({ children }) {
            return <ul className="list-disc list-outside pl-5 mb-2.5 space-y-1.5 text-slate-200 text-sm">{children}</ul>;
          },
          ol({ children }) {
            return <ol className="list-decimal list-outside pl-5 mb-2.5 space-y-1.5 text-slate-200 text-sm">{children}</ol>;
          },
          li({ children }) {
            return <li className="text-slate-200 leading-relaxed pl-1">{children}</li>;
          },
          blockquote({ children }) {
            return (
              <blockquote className="border-l-3 border-cyan-500/80 pl-3.5 italic text-slate-300 my-2.5 text-sm bg-space-900/60 py-1.5 rounded-r">
                {children}
              </blockquote>
            );
          },
          table({ children }) {
            return (
              <div className="overflow-x-auto my-3 rounded-xl border border-slate-700/60 shadow-sm">
                <table className="min-w-full divide-y divide-slate-700/60 text-xs text-left">
                  {children}
                </table>
              </div>
            );
          },
          th({ children }) {
            return <th className="px-3.5 py-2.5 bg-space-850 font-semibold text-slate-200">{children}</th>;
          },
          td({ children }) {
            return <td className="px-3.5 py-2 border-t border-slate-800/80 text-slate-300">{children}</td>;
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
        {normalizedContent}
      </ReactMarkdown>
    </div>
  );
};
