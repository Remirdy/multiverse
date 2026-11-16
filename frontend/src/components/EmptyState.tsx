import React from 'react';
import { Terminal, Atom, Calculator, Cpu, Sparkles, BookOpen } from 'lucide-react';
import { Logo } from './Logo';

interface EmptyStateProps {
  onSelectPrompt: (prompt: string) => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onSelectPrompt }) => {
  const suggestions = [
    {
      title: 'Yazılım & Kod Mimarisi',
      icon: Terminal,
      specialist: 'Poolside Laguna XS',
      equivalent: 'Claude Sonnet 5.5 Muadili',
      prompt: 'Python asyncio vs Go goroutines karşılaştırması yap. Yüksek eşzamanlı bir veri kuyruğunda bellek güvenliği ve throughput kıyaslaması sun.',
    },
    {
      title: 'Matematik & Formel Mantık',
      icon: Calculator,
      specialist: 'Nemotron 3.5 Lightning',
      equivalent: 'GPT-5 Reasoning Muadili',
      prompt: '3x3 simetrik bir matrisin özdeğer ve özvektörlerini hesaplayıp kuantum durum vektörlerindeki geometrik dönüşümünü adım adım ispatla.',
    },
    {
      title: 'Derin Akademik & Felsefe',
      icon: BookOpen,
      specialist: 'Nemotron 3 Ultra 550B',
      equivalent: 'Claude Opus 4.6 Muadili',
      prompt: 'Kozmolojide termodinamik zaman oku ile kuantum dolanıklığı arasındaki ilişkiyi kapsamlı ve felsefi bir derinlikle açıkla.',
    },
    {
      title: 'Ultra Hızlı Özet & Analiz',
      icon: Sparkles,
      specialist: 'Nemotron 3.5 Bolt',
      equivalent: 'Gemini 3.8 Flash Muadili',
      prompt: 'Nöromorfik çip mimarilerinin klasik Von Neumann mimarisine göre 3 temel donanımsal farkını 200 milisaniyede özetle.',
    },
    {
      title: 'Deneysel Bilim & Hipotez',
      icon: Atom,
      specialist: 'Nemotron Nano Omni',
      equivalent: '4-Hydrogen Muadili',
      prompt: 'Termodinamiğin ikinci yasasının izole makroskopik sistemlerde entropiyi neden tek yönlü artırdığını adım adım çıkarımla açıkla.',
    },
    {
      title: 'Robotik & Sistem Mühendisliği',
      icon: Cpu,
      specialist: 'Nemotron Super VL 120B',
      equivalent: '4-Argon Muadili',
      prompt: '6 serbestlik dereceli (DOF) bir robotik kol için değişen yüklere karşı adaptif PID kontrol ve ters kinematik formülasyonunu yaz.',
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
            NVIDIA NIM API altyapısıyla çalışan, <strong>Claude Sonnet</strong>, <strong>GPT-5</strong>, <strong>Claude Opus</strong>, <strong>Gemini Flash</strong>, <strong>4-Hydrogen</strong> ve <strong>4-Argon</strong> kalibresindeki resmi uzman modelleri eşzamanlı sorgulayın.
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
              <div className="pt-1.5 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
                <span className="text-cyan-400 font-mono font-medium truncate">{item.specialist}</span>
                <span className="text-slate-500 font-sans shrink-0">{item.equivalent}</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
