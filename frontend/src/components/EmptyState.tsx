import React from 'react';
import { Terminal, Atom, Calculator, Cpu, Sparkles, BookOpen } from 'lucide-react';
import { Logo } from './Logo';
import { useLanguage } from '../i18n/LanguageContext';

interface EmptyStateProps {
  onSelectPrompt: (prompt: string) => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onSelectPrompt }) => {
  const { language, t } = useLanguage();

  const suggestions = language === 'en' ? [
    {
      title: 'Software & Code Architecture',
      icon: Terminal,
      specialist: 'Poolside Laguna XS',
      equivalent: 'Claude Sonnet 5.5 Caliber',
      prompt: 'Compare Python asyncio vs Go goroutines. Present memory safety and throughput benchmarks for a high-concurrency message queue.',
    },
    {
      title: 'Math & Formal Logic',
      icon: Calculator,
      specialist: 'Nemotron 3.5 Lightning',
      equivalent: 'GPT-5 Reasoning Caliber',
      prompt: 'Calculate eigenvalues and eigenvectors of a 3x3 symmetric matrix and derive geometric evolution in quantum state vectors step-by-step.',
    },
    {
      title: 'Deep Frontier Synthesis',
      icon: BookOpen,
      specialist: 'Nemotron 3 Ultra 550B',
      equivalent: 'Claude Opus 4.6 Caliber',
      prompt: 'Explain the thermodynamic arrow of time and quantum entanglement in cosmology with comprehensive academic depth.',
    },
    {
      title: 'Sub-Second Speed & Summary',
      icon: Sparkles,
      specialist: 'Nemotron 3.5 Bolt',
      equivalent: 'Gemini 3.8 Flash Caliber',
      prompt: 'Summarize the 3 architectural differences between Neuromorphic chips and classical Von Neumann architecture in 200 milliseconds.',
    },
    {
      title: 'Circuit & Vision Engineering',
      icon: Cpu,
      specialist: 'Nemotron Super VL 120B',
      equivalent: '4-Argon Caliber (Vision)',
      prompt: 'Analyze the diode and transistor circuit schematics: calculate output voltage Vo, Zener breakdown point, and branch currents.',
    },
    {
      title: 'STEM Science & Hypotheses',
      icon: Atom,
      specialist: 'Nemotron Nano Omni',
      equivalent: '4-Hydrogen Caliber',
      prompt: 'Explain statistical entropy S = k ln(Omega) and quantum degeneracy in microcanonical ensembles with rigorous step derivations.',
    },
  ] : [
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
      title: 'Devre & Görsel Analiz',
      icon: Cpu,
      specialist: 'Nemotron Super VL 120B',
      equivalent: '4-Argon (Görsel Model)',
      prompt: 'Ekli şemadaki diyot ve transistör devrelerinde Vo çıkış gerilimini, Zener kırılma noktasını ve kol akımlarını hesapla.',
    },
    {
      title: 'Deneysel Bilim & Hipotez',
      icon: Atom,
      specialist: 'Nemotron Nano Omni',
      equivalent: '4-Hydrogen Muadili',
      prompt: 'Termodinamiğin ikinci yasasının izole makroskopik sistemlerde entropiyi neden tek yönlü artırdığını adım adım çıkarımla açıkla.',
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
            {t.heroTitle}
          </p>
          <p className="text-xs text-slate-400 max-w-xl mx-auto leading-relaxed">
            {t.heroSubtitle}
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
              className="flex flex-col justify-between p-3.5 rounded-xl bg-space-900 hover:bg-space-850 border border-slate-800 hover:border-slate-700/80 transition-all duration-200 group text-left shadow-sm hover:shadow-md"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-space-800 text-cyan-400 group-hover:text-cyan-300 group-hover:scale-105 transition-transform">
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="text-xs font-semibold text-slate-200 group-hover:text-white">
                      {item.title}
                    </span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed line-clamp-2">
                  {item.prompt}
                </p>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px]">
                <span className="font-mono text-cyan-400/90 font-medium">
                  {item.specialist}
                </span>
                <span className="text-slate-500 font-medium">
                  {item.equivalent}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
