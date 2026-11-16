import React from 'react';
import { User, Sparkles } from 'lucide-react';
import { TurnDetail } from '../types';
import { ComparisonCard } from './ComparisonCard';

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
              <div className="flex-1 space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-slate-300">You</span>
                  <span className="text-[10px] text-slate-500 font-mono">
                    {turn.created_at ? new Date(turn.created_at).toLocaleTimeString() : 'Just now'}
                  </span>
                </div>
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

            {/* Model Comparison Grid */}
            <div className="pl-0 sm:pl-11 space-y-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                <span>Simultaneous Model Comparison ({turn.responses.length} Perspectives)</span>
              </div>

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
