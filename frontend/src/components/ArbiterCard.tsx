import React, { useState } from 'react';
import { Trophy, Copy, Check, Sparkles, X, ChevronDown, ChevronUp, Clock } from 'lucide-react';
import { MarkdownRenderer } from './MarkdownRenderer';
import { useLanguage } from '../i18n/LanguageContext';

interface ArbiterCardProps {
  synthesisText: string;
  arbiterModel: string;
  latencyMs: number;
  onClose: () => void;
}

export const ArbiterCard: React.FC<ArbiterCardProps> = ({
  synthesisText,
  arbiterModel,
  latencyMs,
  onClose,
}) => {
  const { t } = useLanguage();
  const [copied, setCopied] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(synthesisText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full mb-6 rounded-2xl bg-gradient-to-b from-amber-950/40 via-space-900 to-space-950 border border-amber-500/40 shadow-2xl shadow-amber-950/30 overflow-hidden animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3.5 bg-gradient-to-r from-amber-950/60 to-orange-950/40 border-b border-amber-500/30">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-8 h-8 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 text-space-950 shadow-md shadow-amber-900/50">
            <Trophy className="w-4 h-4 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-amber-200 tracking-wide">
                {t.arbiterTitle}
              </h3>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-400/20 text-amber-300 border border-amber-400/40">
                <Sparkles className="w-2.5 h-2.5" />
                550B MoE Flagship
              </span>
            </div>
            <p className="text-[11px] text-amber-300/70">
              {arbiterModel.replace('nvidia/', '')} • {t.arbiterSubtitle}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Latency Badge */}
          <div className="hidden sm:flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-950/50 border border-amber-500/30 text-[11px] text-amber-300">
            <Clock className="w-3 h-3 text-amber-400" />
            <span>{(latencyMs / 1000).toFixed(1)}s</span>
          </div>

          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-950/50 hover:bg-amber-900/50 border border-amber-500/30 text-amber-300 text-xs transition-colors"
            title="Sentez Çözümünü Kopyala"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-300 font-medium">{t.copied}</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>{t.copy}</span>
              </>
            )}
          </button>

          {/* Toggle Collapse */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 rounded-lg text-amber-400 hover:text-amber-200 hover:bg-amber-900/40 transition-colors"
            title={isCollapsed ? 'Genişlet' : 'Daralt'}
          >
            {isCollapsed ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </button>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-space-800 transition-colors"
            title={t.closeArbiter}
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Body Content */}
      {!isCollapsed && (
        <div className="p-5 md:p-6 text-sm text-slate-200 leading-relaxed overflow-x-auto custom-scrollbar">
          <div className="prose prose-invert max-w-none prose-table:border prose-table:border-amber-900/40 prose-th:bg-amber-950/30 prose-th:text-amber-200 prose-td:border-amber-900/30">
            <MarkdownRenderer content={synthesisText} />
          </div>
        </div>
      )}
    </div>
  );
};
