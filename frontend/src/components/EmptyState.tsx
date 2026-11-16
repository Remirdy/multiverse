import React from 'react';
import { Terminal, Atom, Calculator, Feather, Languages, Cpu } from 'lucide-react';
import { Logo } from './Logo';

interface EmptyStateProps {
  onSelectPrompt: (prompt: string) => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onSelectPrompt }) => {
  const suggestions = [
    {
      title: 'Coding & Systems Architecture',
      icon: Terminal,
      specialist: 'Poolside Laguna XS',
      prompt: 'Compare Python asyncio vs multiprocessing for a high-concurrency API server. Provide concrete code and benchmarks.',
    },
    {
      title: 'Formal Mathematics & Proofs',
      icon: Calculator,
      specialist: 'Nemotron 3.5 Lightning',
      prompt: 'Calculate the eigenvalues and eigenvectors of a 3x3 symmetric matrix and explain the geometric transformation.',
    },
    {
      title: 'Deep Scientific Deduction',
      icon: Atom,
      specialist: 'Nemotron Nano Omni',
      prompt: 'Provide a step-by-step hypothesis explaining why entropy increases monotonically in an isolated macroscopic thermodynamic system.',
    },
    {
      title: 'Multilingual Linguistics & Translation',
      icon: Languages,
      specialist: 'Riva Translate 4B',
      prompt: 'Translate the concept of "Schadenfreude" and "Weltschmerz" into Turkish, explaining the exact linguistic and cultural nuances.',
    },
    {
      title: 'Robotics Dynamics & Actuators',
      icon: Cpu,
      specialist: 'Nemotron Super VL 120B',
      prompt: 'Explain how to design an adaptive PID controller for a 6-DOF robotic manipulator arm facing varying payload inertia.',
    },
    {
      title: 'Creative Fiction & Worldbuilding',
      icon: Feather,
      specialist: 'MiniMax M3.1 Flash',
      prompt: 'Write an atmospheric scene opening depicting a quiet research station situated on the event horizon of a dormant Kerr black hole.',
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
          <p className="text-xs text-slate-400 max-w-lg mx-auto leading-relaxed">
            Every model in Multiverse is chosen strictly for its verified benchmark domain specialization.
            No single model is used for everything—select specialists tailored to your problem.
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
