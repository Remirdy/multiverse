import React from 'react';
import { Check, X, Layers, Sparkles, Code2, Atom, Cpu, Languages, Zap, Info } from 'lucide-react';
import { ModelInfo } from '../types';
import { useLanguage } from '../i18n/LanguageContext';

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
  const { language, t } = useLanguage();
  if (!isOpen) return null;

  // Presets mapping directly to real NVIDIA NIM model IDs
  const presets = language === 'en' ? [
    {
      label: 'Balanced Trio (Sonnet + GPT-5 + Opus)',
      icon: Sparkles,
      ids: [
        'poolside/laguna-xs-2.1',
        'nvidia/nemotron-3.5-lightning-30b-a3b',
        'nvidia/nemotron-3-ultra-550b-a55b',
      ],
    },
    {
      label: 'Coding & Architecture (Sonnet Tier)',
      icon: Code2,
      ids: [
        'poolside/laguna-xs-2.1',
        'nvidia/nemotron-3.5-lightning-30b-a3b',
      ],
    },
    {
      label: 'Circuit & Vision (4-Argon)',
      icon: Cpu,
      ids: [
        'nvidia/nemotron-3.5-super-vl-120b-a12b',
        'nvidia/nemotron-3.5-lightning-30b-a3b',
      ],
    },
    {
      label: 'Sub-Second Speed (Gemini Flash)',
      icon: Zap,
      ids: [
        'nvidia/nemotron-3.5-bolt-e4b',
        'poolside/laguna-xs-2.1',
      ],
    },
    {
      label: 'STEM Science & Physics (4-Hydrogen)',
      icon: Atom,
      ids: [
        'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning',
        'nvidia/nemotron-3-ultra-550b-a55b',
      ],
    },
    {
      label: 'Neural Translation (Riva)',
      icon: Languages,
      ids: [
        'nvidia/riva-translate-4b-instruct-v2',
        'nvidia/nemotron-3.5-bolt-e4b',
      ],
    },
  ] : [
    {
      label: 'Dengeli Üçlü (Sonnet + GPT-5 + Opus)',
      icon: Sparkles,
      ids: [
        'poolside/laguna-xs-2.1',
        'nvidia/nemotron-3.5-lightning-30b-a3b',
        'nvidia/nemotron-3-ultra-550b-a55b',
      ],
    },
    {
      label: 'Kodlama (Sonnet Muadili)',
      icon: Code2,
      ids: [
        'poolside/laguna-xs-2.1',
        'nvidia/nemotron-3.5-lightning-30b-a3b',
      ],
    },
    {
      label: 'Devre & Görsel (4-Argon)',
      icon: Cpu,
      ids: [
        'nvidia/nemotron-3.5-super-vl-120b-a12b',
        'nvidia/nemotron-3.5-lightning-30b-a3b',
      ],
    },
    {
      label: 'Hızlı & Flash (Gemini Flash)',
      icon: Zap,
      ids: [
        'nvidia/nemotron-3.5-bolt-e4b',
        'poolside/laguna-xs-2.1',
      ],
    },
    {
      label: 'Derin Bilim & STEM (4-Hydrogen)',
      icon: Atom,
      ids: [
        'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning',
        'nvidia/nemotron-3-ultra-550b-a55b',
      ],
    },
    {
      label: 'Çeviri & Dilbilim (Riva)',
      icon: Languages,
      ids: [
        'nvidia/riva-translate-4b-instruct-v2',
        'nvidia/nemotron-3.5-bolt-e4b',
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
              <h2 className="text-base font-semibold text-slate-100">{t.modalTitle}</h2>
              <p className="text-xs text-slate-400">
                {t.modalSubtitle} ({selectedModelIds.length}/{maxModels} {t.activeCount.toLowerCase()})
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
          <span className="text-xs font-medium text-slate-400 shrink-0 mr-1">{language === 'en' ? 'Presets:' : 'Ön Ayarlar:'}</span>
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
                <Icon className="w-3.5 h-3.5 text-cyan-400" />
                <span>{preset.label}</span>
              </button>
            );
          })}
        </div>

        {/* Models Grid */}
        <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {models.map((model) => {
              const isSelected = selectedModelIds.includes(model.id);
              const isVision = model.id.includes('vl') || model.tags.includes('vision');

              return (
                <div
                  key={model.id}
                  onClick={() => onToggleModel(model.id)}
                  className={`flex flex-col justify-between p-4 rounded-xl cursor-pointer border transition-all ${
                    isSelected
                      ? 'bg-space-850 border-cyan-500/80 shadow-md shadow-cyan-950/20 ring-1 ring-cyan-500/40'
                      : 'bg-space-950/60 border-slate-800 hover:border-slate-700/80 hover:bg-space-850/50'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-slate-100">
                          {model.name}
                        </span>
                        {isVision && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-800/60 font-medium">
                            Vision / Devre
                          </span>
                        )}
                      </div>
                      <span className="font-mono text-[10px] text-slate-500 block truncate">
                        {model.id}
                      </span>
                    </div>

                    <div
                      className={`w-5 h-5 rounded-md flex items-center justify-center border transition-all shrink-0 mt-0.5 ${
                        isSelected
                          ? 'bg-cyan-500 border-cyan-400 text-space-950'
                          : 'border-slate-700 bg-space-800 text-transparent'
                      }`}
                    >
                      <Check className="w-3.5 h-3.5 stroke-[3]" />
                    </div>
                  </div>

                  <p className="text-xs text-slate-400 leading-relaxed mb-3 line-clamp-2">
                    {model.description}
                  </p>

                  <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800/80 mt-auto">
                    <span className="text-cyan-400 font-medium px-2 py-0.5 rounded bg-space-900 border border-slate-800">
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
            <span>NVIDIA NIM API microservices.</span>
          </div>
          <button
            onClick={onClose}
            className="px-5 py-2 text-xs font-semibold rounded-lg bg-cyan-500 hover:bg-cyan-400 text-space-950 transition-colors shadow-sm"
          >
            {t.doneBtn} ({selectedModelIds.length} {t.modelsLabel})
          </button>
        </div>
      </div>
    </div>
  );
};
