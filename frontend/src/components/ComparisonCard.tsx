import React, { useState } from 'react';
import { Copy, Check, RotateCw, AlertTriangle, Clock, Sparkles, Brain, ChevronDown, ChevronUp } from 'lucide-react';
import { ModelResult } from '../types';
import { MarkdownRenderer } from './MarkdownRenderer';
import { useLanguage } from '../i18n/LanguageContext';

interface ComparisonCardProps {
  result: ModelResult;
  onRetry?: (modelId: string) => void;
  isRetrying?: boolean;
}

/**
 * Parses internal reasoning traces / scratchpads from final solution to keep presentation clean
 */
function parseReasoningAndContent(text: string): { thinking: string | null; solution: string } {
  if (!text) return { thinking: null, solution: '' };

  // 1. Explicit <think>...</think> tags
  const thinkTag = text.match(/<think>([\s\S]*?)<\/think>([\s\S]*)/i);
  if (thinkTag) {
    return {
      thinking: thinkTag[1].trim(),
      solution: thinkTag[2].trim() || text,
    };
  }

  // 2. "Here's a thinking process:" or "Thinking Process:" block
  const thinkHeader = text.match(
    /^(?:Here(?:'|’)s a thinking process:?|Thinking Process:?|Draft:?)([\s\S]*?)(?=\n#{1,3}\s+(?:Final|Solution|Result|Answer|Sonuç|Çözüm|Nihai Sonuç)|\n\*\*(?:Final Answer|Sonuç|Çözüm|Nihai Sonuç):?\*\*|$)/i
  );
  if (thinkHeader && text.length > thinkHeader[0].length + 40) {
    const remaining = text.slice(thinkHeader[0].length).trim();
    if (remaining) {
      return {
        thinking: thinkHeader[1].trim(),
        solution: remaining,
      };
    }
  }

  return { thinking: null, solution: text };
}

export const ComparisonCard: React.FC<ComparisonCardProps> = ({
  result,
  onRetry,
  isRetrying = false,
}) => {
  const { t } = useLanguage();
  const [copied, setCopied] = useState(false);
  const [showReasoning, setShowReasoning] = useState(false);

  const handleCopy = async () => {
    if (!result.response_text) return;
    try {
      await navigator.clipboard.writeText(result.response_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy response: ', err);
    }
  };

  const isError = result.status === 'error';
  const isTimeout = result.status === 'timeout';
  const isLoading = result.status === 'loading' || isRetrying;

  const { thinking, solution } = parseReasoningAndContent(result.response_text || '');

  return (
    <div
      className={`flex flex-col rounded-2xl border transition-all duration-200 bg-space-900/90 shadow-xl ${
        isError || isTimeout
          ? 'border-rose-900/40 hover:border-rose-700/60 shadow-rose-950/20'
          : 'border-slate-800 hover:border-slate-700/80 shadow-black/40'
      } h-full min-h-[320px] max-h-[700px] overflow-hidden`}
    >
      {/* Card Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-space-850/90 border-b border-slate-800/80 backdrop-blur-sm shrink-0">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-space-800 border border-slate-700/60 text-brand-cyan shrink-0">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-slate-100 truncate tracking-tight">
                {result.model_name}
              </h3>
              <span className="text-[10px] font-medium tracking-wide uppercase px-1.5 py-0.5 rounded bg-space-800 text-slate-400 border border-slate-700/40 shrink-0">
                {result.provider}
              </span>
            </div>
          </div>
        </div>

        {/* Card Header Actions / Status */}
        <div className="flex items-center gap-2 shrink-0">
          {/* Response Time Badge */}
          {result.response_time_ms != null && !isLoading && (
            <div className="flex items-center gap-1 text-[11px] font-mono text-slate-400 bg-space-800/90 px-2 py-0.5 rounded-md border border-slate-700/40">
              <Clock className="w-3 h-3 text-cyan-400/70" />
              <span>{Math.round(result.response_time_ms).toLocaleString()} ms</span>
            </div>
          )}

          {/* Status Badge */}
          {isLoading ? (
            <span className="inline-flex items-center gap-1.5 text-[11px] text-cyan-300 bg-cyan-950/60 border border-cyan-800/50 px-2.5 py-0.5 rounded-full font-medium">
              <RotateCw className="w-3 h-3 animate-spin text-cyan-400" />
              <span>{t.retrying}</span>
            </span>
          ) : isError || isTimeout ? (
            <span className="inline-flex items-center gap-1 text-[11px] text-rose-400 bg-rose-950/60 border border-rose-800/50 px-2 py-0.5 rounded-full font-medium">
              <AlertTriangle className="w-3 h-3" />
              {isTimeout ? t.timeoutTitle : t.errorTitle}
            </span>
          ) : (
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-200 transition-colors bg-space-800/80 hover:bg-space-700/80 px-2.5 py-1 rounded-lg border border-slate-700/50"
              title={t.copy}
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400 font-medium">{t.copied}</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>{t.copy}</span>
                </>
              )}
            </button>
          )}

          {/* Retry Button if failed or timeout */}
          {(isError || isTimeout) && onRetry && (
            <button
              onClick={() => onRetry(result.model_id)}
              disabled={isLoading}
              className="flex items-center gap-1 text-[11px] font-medium text-rose-300 hover:text-rose-100 bg-rose-950/80 hover:bg-rose-900 border border-rose-800/60 px-2.5 py-1 rounded-lg transition-colors"
              title={t.retry}
            >
              <RotateCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} />
              <span>{t.retry}</span>
            </button>
          )}
        </div>
      </div>

      {/* Card Body */}
      <div className="flex-1 p-4 sm:p-5 overflow-y-auto custom-scrollbar">
        {isLoading ? (
          <div className="space-y-3.5 animate-pulse pt-2">
            <div className="h-4 bg-slate-800/70 rounded w-5/6"></div>
            <div className="h-4 bg-slate-800/60 rounded w-full"></div>
            <div className="h-4 bg-slate-800/60 rounded w-4/6"></div>
            <div className="h-28 bg-space-850/60 rounded-xl w-full border border-slate-800/60"></div>
            <div className="h-4 bg-slate-800/50 rounded w-3/4"></div>
          </div>
        ) : isError || isTimeout ? (
          <div className="flex flex-col items-center justify-center text-center p-6 space-y-3 my-auto h-full">
            <div className="w-10 h-10 rounded-full bg-rose-950/70 border border-rose-800/60 flex items-center justify-center text-rose-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <h4 className="text-sm font-semibold text-rose-200">
                {isTimeout ? t.timeoutTitle : t.errorTitle}
              </h4>
              <p className="text-xs text-slate-400 max-w-sm leading-relaxed">
                {result.error_message || 'NVIDIA NIM API bağlantısında beklenmeyen bir hata oluştu.'}
              </p>
            </div>
            {onRetry && (
              <button
                onClick={() => onRetry(result.model_id)}
                className="mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-200 bg-space-800 hover:bg-space-700 border border-slate-700/60 rounded-lg transition-colors"
              >
                <RotateCw className="w-3.5 h-3.5" />
                {t.retry}
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            {/* Collapsible Reasoning & Thought Trace (Accordion) */}
            {thinking && (
              <div className="rounded-xl border border-cyan-800/40 bg-space-950/70 overflow-hidden text-xs shadow-inner">
                <button
                  type="button"
                  onClick={() => setShowReasoning(!showReasoning)}
                  className="w-full flex items-center justify-between px-3.5 py-2.5 bg-space-850/60 hover:bg-space-850 text-cyan-300 font-medium transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <Brain className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{t.reasoningProcess}</span>
                  </div>
                  <div className="flex items-center gap-1 text-[11px] text-slate-400">
                    <span>{showReasoning ? t.hideReasoning : t.showReasoning}</span>
                    {showReasoning ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </div>
                </button>
                {showReasoning && (
                  <div className="p-3.5 text-slate-300 bg-space-950/50 max-h-72 overflow-y-auto custom-scrollbar border-t border-slate-800/60">
                    <MarkdownRenderer content={thinking} />
                  </div>
                )}
              </div>
            )}

            {/* Main Final Solution Content */}
            <MarkdownRenderer content={solution} />
          </div>
        )}
      </div>
    </div>
  );
};
