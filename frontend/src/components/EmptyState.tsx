import React from 'react';
import { Terminal, Atom, Calculator, Feather } from 'lucide-react';
import { Logo } from './Logo';

interface EmptyStateProps {
  onSelectPrompt: (prompt: string) => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onSelectPrompt }) => {
  const suggestions = [
    {
      title: 'Programming & Concurrency',
      icon: Terminal,
      category: 'Programming',
      prompt: 'Compare Python asyncio vs multithreading vs multiprocessing. Provide concrete code benchmarks and advice on when to choose each.',
    },
    {
      title: 'Mathematical Reasoning',
      icon: Calculator,
      category: 'Mathematics',
      prompt: 'Derive the eigenvalue equation and explain its geometric interpretation in linear transformations step by step.',
    },
    {
      title: 'Scientific Frontiers',
      icon: Atom,
      category: 'Science',
      prompt: 'Explain the difference between quantum entanglement and classical correlation using an accessible thought experiment.',
    },
    {
      title: 'Creative Worldbuilding',
      icon: Feather,
      category: 'Creative',
      prompt: 'Write an atmospheric scene opening depicting the discovery of an ancient Dyson swarm drifting silently around a dying red dwarf.',
    },
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-4xl mx-auto space-y-8 animate-fadeIn">
      {/* Hero Badge */}
      <div className="space-y-4">
        <div className="flex justify-center mb-2">
          <Logo size={56} />
        </div>
        <div className="space-y-2">
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
            MULTIVERSE
          </h2>
          <p className="text-sm sm:text-base text-cyan-400 font-medium tracking-wide">
            One question. Multiple minds.
          </p>
          <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            Send your prompt concurrently to frontier models powered by NVIDIA NIM.
            Analyze divergent perspectives, compare latency, and evaluate reasoning side-by-side.
          </p>
        </div>
      </div>

      {/* Example Prompt Grid */}
      <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-left">
        {suggestions.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.title}
              onClick={() => onSelectPrompt(item.prompt)}
              className="group p-4 rounded-xl bg-space-900/80 hover:bg-space-850 border border-slate-800 hover:border-cyan-500/50 transition-all text-left space-y-2 shadow-sm hover:shadow-cyan-950/20"
            >
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-200 group-hover:text-cyan-300 transition-colors flex items-center gap-1.5">
                  <Icon className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{item.title}</span>
                </span>
                <span className="text-[10px] text-slate-500 uppercase tracking-wider font-medium">
                  {item.category}
                </span>
              </div>
              <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                "{item.prompt}"
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
};
