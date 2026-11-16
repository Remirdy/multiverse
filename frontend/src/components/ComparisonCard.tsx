import React, { useState } from 'react';
import { Copy, Check, RotateCw, AlertTriangle, Clock, Sparkles } from 'lucide-react';
import { ModelResult } from '../types';
import { MarkdownRenderer } from './MarkdownRenderer';

interface ComparisonCardProps {
  result: ModelResult;
  onRetry?: (modelId: string) => void;
  isRetrying?: boolean;
}

export const ComparisonCard: React.FC<ComparisonCardProps> = ({
  result,
  onRetry,
  isRetrying = false,
}) => {
  const [copied, setCopied] = useState(false);

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

  return (
    <div className={`flex flex-col rounded-xl border transition-all duration-200 bg-space-900/90 shadow-lg ${
      isError || isTimeout
        ? 'border-rose-900/40 hover:border-rose-700/60 shadow-rose-950/20'
        : 'border-slate-800 hover:border-slate-700/80 shadow-black/30'
    } h-full min-h-[320px] max-h-[680px] overflow-hidden`}>
      {/* Card Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-space-850/80 border-b border-slate-800/80 backdrop-blur-sm">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-space-800 border border-slate-700/60 text-brand-cyan shrink-0">
            <Sparkles className="w-3.5 h-3.5" />
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
            <div className="flex items-center gap-1 text-[11px] font-mono text-slate-400 bg-space-800/90 px-2 py-0.5 rounded border border-slate-700/40">
              <Clock className="w-3 h-3 text-slate-500" />
              <span>{Math.round(result.response_time_ms).toLocaleString()} ms</span>
            </div>
          )}

          {/* Status Badge */}
          {isLoading ? (
            <span className="inline-flex items-center gap-1.5 text-[11px] text-brand-cyan bg-cyan-950/60 border border-cyan-800/50 px-2 py-0.5 rounded-full font-medium">
              <RotateCw className="w-3 h-3 animate-spin" />
              Thinking
            </span>
          ) : isError || isTimeout ? (
            <span className="inline-flex items-center gap-1 text-[11px] text-rose-400 bg-rose-950/60 border border-rose-800/50 px-2 py-0.5 rounded-full font-medium">
              <AlertTriangle className="w-3 h-3" />
              {isTimeout ? 'Timeout' : 'Failed'}
            </span>
          ) : (
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-200 transition-colors bg-space-800/80 hover:bg-space-700/80 px-2 py-1 rounded border border-slate-700/50"
              title="Copy answer"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400 font-medium">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy</span>
                </>
              )}
            </button>
          )}

          {/* Retry Button if failed or timeout */}
          {(isError || isTimeout) && onRetry && (
            <button
              onClick={() => onRetry(result.model_id)}
              disabled={isLoading}
              className="flex items-center gap-1 text-[11px] font-medium text-rose-300 hover:text-rose-100 bg-rose-950/80 hover:bg-rose-900 border border-rose-800/60 px-2.5 py-1 rounded transition-colors"
              title="Retry this model"
            >
              <RotateCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} />
              <span>Retry</span>
            </button>
          )}
        </div>
      </div>

      {/* Card Body */}
      <div className="flex-1 p-4 overflow-y-auto custom-scrollbar">
        {isLoading ? (
          <div className="space-y-3.5 animate-pulse pt-2">
            <div className="h-4 bg-slate-800/70 rounded w-5/6"></div>
            <div className="h-4 bg-slate-800/60 rounded w-full"></div>
            <div className="h-4 bg-slate-800/60 rounded w-4/6"></div>
            <div className="h-24 bg-space-850/60 rounded-lg w-full border border-slate-800/60"></div>
            <div className="h-4 bg-slate-800/50 rounded w-3/4"></div>
          </div>
        ) : isError || isTimeout ? (
          <div className="flex flex-col items-center justify-center text-center p-6 space-y-3 my-auto h-full">
            <div className="w-10 h-10 rounded-full bg-rose-950/70 border border-rose-800/60 flex items-center justify-center text-rose-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div className="space-y-1">
              <h4 className="text-sm font-semibold text-rose-200">
                {isTimeout ? 'Model Response Timed Out' : 'Model Execution Failed'}
              </h4>
              <p className="text-xs text-slate-400 max-w-sm leading-relaxed">
                {result.error_message || 'An unknown error occurred while communicating with the NVIDIA NIM API.'}
              </p>
            </div>
            {onRetry && (
              <button
                onClick={() => onRetry(result.model_id)}
                className="mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-200 bg-space-800 hover:bg-space-700 border border-slate-700/60 rounded-lg transition-colors"
              >
                <RotateCw className="w-3.5 h-3.5" />
                Retry {result.model_name}
              </button>
            )}
          </div>
        ) : (
          <MarkdownRenderer content={result.response_text || ''} />
        )}
      </div>
    </div>
  );
};
