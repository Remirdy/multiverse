import React from 'react';
import { Check, X, Layers, Sparkles, Code2, Calculator, Atom, Languages, Cpu, Info } from 'lucide-react';
import { ModelInfo } from '../types';

interface ModelSelectorProps {
  isOpen: boolean;
  onClose: () => void;
  models: ModelInfo[];
  selectedModelIds: string[];
  onToggleModel: (modelId: string) => void;
  onSelectPreset: (modelIds: string[]) => void;
  maxModels?: number;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  isOpen,
  onClose,
  models,
  selectedModelIds,
  onToggleModel,
  onSelectPreset,
  maxModels = 6,
}) => {
  if (!isOpen) return null;

  // Domain-specialized preset definitions
  const presets = [
    {
      label: 'Specialist Trio',
      icon: Sparkles,
      ids: [
        'poolside/laguna-xs-2.1',
        'nvidia/nemotron-3.5-lightning-30b-a3b',
        'nvidia/nemotron-3-ultra-550b-a55b',
      ],
    },
    {
      label: 'Coding & Dev',
      icon: Code2,
      ids: [
        'poolside/laguna-xs-2.1',
        'nvidia/nemotron-3.5-lightning-30b-a3b',
      ],
    },
    {
      label: 'Math & Logic',
      icon: Calculator,
      ids: [
        'nvidia/nemotron-3.5-lightning-30b-a3b',
        'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning',
      ],
    },
    {
      label: 'Deep Science & 550B',
      icon: Atom,
      ids: [
        'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning',
        'nvidia/nemotron-3-ultra-550b-a55b',
      ],
    },
    {
      label: 'Robotics & Hardware',
      icon: Cpu,
      ids: [
        'nvidia/nemotron-3.5-super-vl-120b-a12b',
        'nvidia/nemotron-3.5-bolt-e4b',
      ],
    },
    {
      label: 'Translation & Literature',
      icon: Languages,
      ids: [
        'nvidia/riva-translate-4b-instruct-v2',
        'minimaxai/minimax-m3.1-flash',
      ],
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-4xl max-h-[85vh] flex flex-col rounded-2xl bg-space-900 border border-slate-800 shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-space-850/60">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-space-800 border border-slate-700/60 text-brand-cyan">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-100">Specialized AI Model Registry</h2>
              <p className="text-xs text-slate-400">
                Choose specialized models tailored by domain ({selectedModelIds.length}/{maxModels} selected)
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-space-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Quick Presets Bar */}
        <div className="flex items-center gap-2 px-6 py-3 border-b border-slate-800/80 bg-space-950/40 overflow-x-auto custom-scrollbar">
          <span className="text-xs font-medium text-slate-400 shrink-0 mr-1">Domains:</span>
          {presets.map((preset) => {
            const Icon = preset.icon;
            const isCurrent =
              preset.ids.length === selectedModelIds.length &&
              preset.ids.every((id) => selectedModelIds.includes(id));
            return (
              <button
                key={preset.label}
                onClick={() => onSelectPreset(preset.ids)}
                className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium transition-all shrink-0 ${
                  isCurrent
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 shadow-sm'
                    : 'bg-space-800 text-slate-300 hover:bg-space-700 hover:text-slate-100 border border-slate-700/60'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{preset.label}</span>
              </button>
            );
          })}
        </div>

        {/* Model Cards Grid */}
        <div className="flex-1 overflow-y-auto p-6 space-y-3 custom-scrollbar">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {models.map((model) => {
              const isSelected = selectedModelIds.includes(model.id);
              const isDisabled = !isSelected && selectedModelIds.length >= maxModels;

              return (
                <div
                  key={model.id}
                  onClick={() => {
                    if (!isDisabled) onToggleModel(model.id);
                  }}
                  className={`relative flex flex-col p-4 rounded-xl border transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-brand-indigo/15 border-cyan-500/70 shadow-md shadow-cyan-950/30'
                      : isDisabled
                      ? 'bg-space-950/40 border-slate-800/40 opacity-45 cursor-not-allowed'
                      : 'bg-space-850/70 border-slate-800 hover:border-slate-700 hover:bg-space-800/60'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-sm text-slate-100 truncate">
                          {model.name}
                        </span>
                        {model.is_default && (
                          <span className="text-[10px] bg-cyan-950/70 text-cyan-300 border border-cyan-800/60 px-1.5 py-0.2 rounded font-medium">
                            Specialist Pick
                          </span>
                        )}
                      </div>
                      <span className="inline-block text-[11px] font-mono text-slate-400 mb-2 truncate">
                        {model.id}
                      </span>
                    </div>

                    {/* Checkbox indicator */}
                    <div
                      className={`flex items-center justify-center w-5 h-5 rounded-md border shrink-0 transition-all ${
                        isSelected
                          ? 'bg-cyan-500 border-cyan-400 text-space-950 font-bold'
                          : 'border-slate-700 bg-space-800'
                      }`}
                    >
                      {isSelected && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                    </div>
                  </div>

                  <p className="text-xs text-slate-400 line-clamp-2 mb-3 leading-relaxed">
                    {model.description}
                  </p>

                  <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-800/80 mt-auto">
                    <span className="text-cyan-400/90 font-medium px-2 py-0.5 rounded bg-space-900 border border-slate-800">
                      {model.category}
                    </span>
                    <span className="font-mono text-slate-400">
                      {(model.context_length / 1000).toFixed(0)}k ctx
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-800 bg-space-850/80">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Info className="w-4 h-4 text-cyan-400 shrink-0" />
            <span>Each model is chosen strictly for its verified benchmark domain specialization.</span>
          </div>
          <button
            onClick={onClose}
            className="px-5 py-2 text-xs font-semibold rounded-lg bg-cyan-500 hover:bg-cyan-400 text-space-950 transition-colors shadow-sm"
          >
            Apply ({selectedModelIds.length} Models)
          </button>
        </div>
      </div>
    </div>
  );
};
