import React from 'react';
import { Menu, Layers, ShieldCheck, ShieldAlert } from 'lucide-react';
import { ModelInfo, ProviderHealth } from '../types';
import { Logo } from './Logo';

interface HeaderProps {
  onToggleSidebar: () => void;
  selectedModels: ModelInfo[];
  onOpenModelSelector: () => void;
  activeConversationTitle?: string;
  health: ProviderHealth | null;
  onOpenKeyModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  onToggleSidebar,
  selectedModels,
  onOpenModelSelector,
  activeConversationTitle,
  health,
  onOpenKeyModal,
}) => {
  const isKeyConfigured = health?.api_key_set ?? false;

  return (
    <header className="h-14 border-b border-slate-800/80 bg-space-900/80 backdrop-blur-md px-4 flex items-center justify-between z-30 shrink-0">
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={onToggleSidebar}
          className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-space-800 transition-colors lg:hidden"
          title="Open sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 min-w-0">
          <div className="hidden sm:block">
            <Logo size={24} />
          </div>
          <span className="font-semibold text-sm text-slate-200 truncate">
            {activeConversationTitle || 'New Comparison'}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2.5">
        {/* Model Selection Pill */}
        <button
          onClick={onOpenModelSelector}
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-space-850 hover:bg-space-800 border border-slate-700/60 text-xs font-medium text-slate-300 transition-all shadow-sm"
          title="Manage comparison models"
        >
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          <span>{selectedModels.length} Models Active</span>
        </button>

        {/* NVIDIA API Health / Key status button */}
        <button
          onClick={onOpenKeyModal}
          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl border text-xs font-medium transition-all ${
            isKeyConfigured
              ? 'bg-emerald-950/40 text-emerald-300 border-emerald-800/50 hover:bg-emerald-900/40'
              : 'bg-amber-950/40 text-amber-300 border-amber-800/50 hover:bg-amber-900/40'
          }`}
          title="NVIDIA NIM API Key Status"
        >
          {isKeyConfigured ? (
            <>
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span className="hidden md:inline">NVIDIA Live</span>
            </>
          ) : (
            <>
              <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
              <span className="hidden md:inline">API Key Needed</span>
            </>
          )}
        </button>
      </div>
    </header>
  );
};
