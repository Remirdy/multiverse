import React from 'react';
import { Terminal, Atom, Calculator, Cpu, Sparkles, BookOpen } from 'lucide-react';
import { Logo } from './Logo';

interface EmptyStateProps {
  onSelectPrompt: (prompt: string) => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onSelectPrompt }) => {
  const suggestions = [
    {
      title: 'Agentic Software Engineering',
      icon: Terminal,
      specialist: 'Claude Sonnet 5.5',
      prompt: 'Compare Python asyncio vs Go goroutines for a high-throughput event processing pipeline with memory leak safety.',
    },
    {
      title: 'Frontier Mathematical Deduction',
      icon: Calculator,
      specialist: 'GPT-5',
      prompt: 'Derive the spectral theorem for compact self-adjoint operators and explain its implications in quantum state vectors.',
    },
    {
      title: 'Sub-Second Multimodal Reasoning',
      icon: Sparkles,
      specialist: 'Gemini 3.8 Flash',
      prompt: 'Provide a rapid executive synthesis of how neuromorphic computing architectures differ from Von Neumann systems.',
    },
    {
      title: 'Empirical Physics & Chemistry',
      icon: Atom,
      specialist: '4-Hydrogen',
      prompt: 'Formulate an empirical hypothesis evaluating entropy generation and microstate phase space in non-equilibrium thermodynamics.',
    },
    {
      title: 'Robotics Dynamics & Control',
      icon: Cpu,
      specialist: '4-Argon',
      prompt: 'Explain how to formulate the Lagrangian dynamics and non-linear inverse kinematics for an autonomous hexapod walking robot.',
    },
    {
      title: 'Deep Systems Philosophy',
      icon: BookOpen,
      specialist: 'Claude Opus 4.6',
      prompt: 'Explore the philosophical paradox of consciousness and intentionality in artificial substrates from an epistemological perspective.',
    },
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-5xl mx-auto space-y-6 animate-fadeIn">
      {/* Hero Badge */}
      <div className="space-y-3">
        <div className="flex justify-center mb-1">
          <Logo size={52} />
        </div>
        <div className="space-y-1.5">
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
            MULTIVERSE
          </h2>
          <p className="text-sm sm:text-base text-cyan-400 font-medium tracking-wide">
            One question. Multiple minds.
          </p>
          <p className="text-xs text-slate-400 max-w-xl mx-auto leading-relaxed">
            Query next-generation frontier intelligence simultaneously. Compare <strong>GPT-5</strong>, <strong>Claude Sonnet 5.5</strong>, <strong>Claude Opus 4.6</strong>, <strong>Gemini 3.8 Flash</strong>, <strong>4-Hydrogen</strong>, and <strong>4-Argon</strong> side-by-side.
          </p>
        </div>
      </div>

      {/* Example Specialist Prompt Grid */}
      <div className="w-full grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-1 text-left">
        {suggestions.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.title}
              onClick={() => onSelectPrompt(item.prompt)}
              className="group p-3.5 rounded-xl bg-space-900/80 hover:bg-space-850 border border-slate-800 hover:border-cyan-500/50 transition-all text-left space-y-2 shadow-sm hover:shadow-cyan-950/20"
            >
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-200 group-hover:text-cyan-300 transition-colors flex items-center gap-1.5 truncate">
                  <Icon className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                  <span className="truncate">{item.title}</span>
                </span>
              </div>
              <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                "{item.prompt}"
              </p>
              <div className="pt-1 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
                <span className="text-slate-500">Specialist:</span>
                <span className="text-cyan-400 font-mono font-medium">{item.specialist}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
