import React, { useState } from 'react';
import { User, Sparkles, FileText, Image as ImageIcon, Trophy, Loader2 } from 'lucide-react';
import { TurnDetail, ModelResult } from '../types';
import { ComparisonCard } from './ComparisonCard';
import { ArbiterCard } from './ArbiterCard';
import { api } from '../services/api';
import { useLanguage } from '../i18n/LanguageContext';

interface ComparisonGridProps {
  turns: TurnDetail[];
  onRetryModel: (turnId: string, modelId: string, prompt: string, systemPrompt?: string) => void;
  retryingModelKeys: Set<string>; // Set of `${turnId}-${modelId}`
}

export const ComparisonGrid: React.FC<ComparisonGridProps> = ({
  turns,
  onRetryModel,
  retryingModelKeys,
}) => {
  const { language, t } = useLanguage();
  const [syntheses, setSyntheses] = useState<Record<string, { arbiter_model: string; synthesis_text: string; latency_ms: number }>>({});
  const [synthesizingTurns, setSynthesizingTurns] = useState<Set<string>>(new Set());

  const handleSynthesize = async (turnId: string, prompt: string, responses: ModelResult[]) => {
    setSynthesizingTurns((prev) => new Set(prev).add(turnId));

    try {
      const payload = {
        prompt,
        responses: responses.map((r) => ({
          model_id: r.model_id,
          model_name: r.model_name,
          response_text: r.response_text || '',
        })),
        language,
      };
      const res = await api.synthesize(payload);
      if (res && res.synthesis_text) {
        setSyntheses((prev) => ({
          ...prev,
          [turnId]: res,
        }));
      }
    } catch (err: any) {
      alert(`Sentezleme sırasında hata oluştu: ${err.message}`);
    } finally {
      setSynthesizingTurns((prev) => {
        const next = new Set(prev);
        next.delete(turnId);
        return next;
      });
    }
  };

  const handleCloseSynthesis = (turnId: string) => {
    setSyntheses((prev) => {
      const next = { ...prev };
      delete next[turnId];
      return next;
    });
  };

  const getGridColsClass = (count: number) => {
    if (count === 1) return 'grid-cols-1 max-w-2xl mx-auto';
    if (count === 2) return 'grid-cols-1 lg:grid-cols-2';
    if (count === 3) return 'grid-cols-1 md:grid-cols-2 xl:grid-cols-3';
    if (count === 4) return 'grid-cols-1 md:grid-cols-2 xl:grid-cols-4';
    return 'grid-cols-1 md:grid-cols-2 xl:grid-cols-3';
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-4 sm:p-6 space-y-10">
      {turns.map((turn, index) => {
        const gridClass = getGridColsClass(turn.responses.length);

        return (
          <div key={turn.id || index} className="space-y-4 animate-fadeIn">
            {/* User Prompt Bubble */}
            <div className="flex items-start gap-3 max-w-3xl">
              <div className="w-8 h-8 rounded-xl bg-space-800 border border-slate-700/80 flex items-center justify-center text-slate-300 shrink-0 mt-0.5">
                <User className="w-4 h-4" />
              </div>
              <div className="flex-1 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-slate-300">You</span>
                  <span className="text-[10px] text-slate-500 font-mono">
                    {turn.created_at ? new Date(turn.created_at).toLocaleTimeString() : 'Just now'}
                  </span>
                </div>

                {/* Attachments Display in User Bubble */}
                {turn.attachments && turn.attachments.length > 0 && (
                  <div className="flex flex-wrap gap-2.5 pt-1">
                    {turn.attachments.map((att, attIdx) => (
                      <div
                        key={attIdx}
                        className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-space-900 border border-slate-700/80 text-xs shadow-sm max-w-sm"
                      >
                        {att.file_type === 'image' && att.data_url ? (
                          <div className="w-8 h-8 rounded-lg overflow-hidden bg-space-950 border border-slate-700 shrink-0">
                            <img src={att.data_url} alt={att.filename} className="w-full h-full object-cover" />
                          </div>
                        ) : att.file_type === 'image' ? (
                          <ImageIcon className="w-4 h-4 text-emerald-400 shrink-0" />
                        ) : (
                          <FileText className="w-4 h-4 text-cyan-400 shrink-0" />
                        )}
                        <div className="flex flex-col truncate">
                          <span className="truncate font-medium text-slate-200 text-xs" title={att.filename}>
                            {att.filename}
                          </span>
                          <span className="text-[10px] text-slate-400">
                            {formatBytes(att.size)} {att.page_count ? `• ${att.page_count} sayfa` : ''}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <div className="p-3.5 rounded-2xl rounded-tl-sm bg-space-850/80 border border-slate-800/80 text-sm text-slate-100 leading-relaxed shadow-sm">
                  {turn.prompt}
                  {turn.system_prompt && (
                    <div className="mt-2 pt-2 border-t border-slate-700/40 text-[11px] text-slate-400 italic">
                      Instructions: {turn.system_prompt}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Model Comparison Grid Header & Arbiter Mode */}
            <div className="pl-0 sm:pl-11 space-y-4">
              {/* Arbiter Action Bar */}
              {(() => {
                const successful = turn.responses.filter((r) => r.status === 'success' && r.response_text);
                const isLoadingModels = turn.responses.some((r) => r.status === 'loading');
                const isTurnSynthesizing = synthesizingTurns.has(turn.id);
                const currentSynthesis = syntheses[turn.id];

                return (
                  <>
                    <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-space-850/80 border border-slate-800 text-xs">
                      <div className="flex items-center gap-2 font-semibold text-slate-300">
                        <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                        <span>{t.perspectives} ({turn.responses.length})</span>
                      </div>

                      {successful.length >= 2 && !isLoadingModels && (
                        <button
                          type="button"
                          onClick={() => handleSynthesize(turn.id, turn.prompt, successful)}
                          disabled={isTurnSynthesizing}
                          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all shadow-md active:scale-95 ${
                            isTurnSynthesizing
                              ? 'bg-amber-950/80 text-amber-300 border border-amber-600/60 animate-pulse cursor-wait'
                              : 'bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-space-950 shadow-amber-950/40'
                          }`}
                          title="NVIDIA Nemotron Ultra 550B ile modellerin güçlü yönlerini sentezle"
                        >
                          {isTurnSynthesizing ? (
                            <>
                              <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              <span>{t.synthesizing}</span>
                            </>
                          ) : (
                            <>
                              <Trophy className="w-3.5 h-3.5 stroke-[2.5]" />
                              <span>{t.synthesizeBtn}</span>
                            </>
                          )}
                        </button>
                      )}
                    </div>

                    {/* Render Golden Synthesis Card if available */}
                    {currentSynthesis && (
                      <ArbiterCard
                        arbiterModel={currentSynthesis.arbiter_model}
                        synthesisText={currentSynthesis.synthesis_text}
                        latencyMs={currentSynthesis.latency_ms}
                        onClose={() => handleCloseSynthesis(turn.id)}
                      />
                    )}
                  </>
                );
              })()}

              <div className={`grid gap-4 ${gridClass}`}>
                {turn.responses.map((modelResult) => {
                  const retryKey = `${turn.id}-${modelResult.model_id}`;
                  const isRetrying = retryingModelKeys.has(retryKey);

                  return (
                    <ComparisonCard
                      key={modelResult.model_id}
                      result={modelResult}
                      isRetrying={isRetrying}
                      onRetry={() =>
                        onRetryModel(
                          turn.id,
                          modelResult.model_id,
                          turn.prompt,
                          turn.system_prompt || undefined
                        )
                      }
                    />
                  );
                })}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

function formatBytes(bytes: number): string {
  if (!bytes) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
