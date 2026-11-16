import React from 'react';
import {
  Menu,
  Layers,
  ShieldCheck,
  ShieldAlert,
  Globe,
  Columns3,
  Users,
  Workflow,
  BookOpen,
} from 'lucide-react';
import { AppWorkspace, ModelInfo, ProviderHealth } from '../types';
import { Logo } from './Logo';
import { useLanguage } from '../i18n/LanguageContext';

interface HeaderProps {
  activeWorkspace: AppWorkspace;
  onSelectWorkspace: (ws: AppWorkspace) => void;
  onToggleSidebar: () => void;
  selectedModels: ModelInfo[];
  onOpenModelSelector: () => void;
  activeConversationTitle?: string;
  health: ProviderHealth | null;
  onOpenKeyModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeWorkspace,
  onSelectWorkspace,
  onToggleSidebar,
  selectedModels,
  onOpenModelSelector,
  activeConversationTitle,
  health,
  onOpenKeyModal,
}) => {
  const { toggleLanguage, t } = useLanguage();
  const isKeyConfigured = health?.api_key_set ?? false;

  const navItems: Array<{ id: AppWorkspace; label: string; icon: React.FC<{ className?: string }> }> = [
    { id: 'compare', label: t.navCompare, icon: Columns3 },
    { id: 'council', label: t.navCouncil, icon: Users },
    { id: 'workflows', label: t.navWorkflows, icon: Workflow },
    { id: 'study', label: t.navStudyLab, icon: BookOpen },
  ];

  return (
    <header className="h-14 border-b border-slate-800/80 bg-space-900/80 backdrop-blur-md px-3 sm:px-4 flex items-center justify-between gap-2 z-30 shrink-0">
      <div className="flex items-center gap-2.5 min-w-0">
        {activeWorkspace === 'compare' && (
          <button
            onClick={onToggleSidebar}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-space-800 transition-colors lg:hidden"
            title="Open sidebar"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}

        <div className="flex items-center gap-2 min-w-0">
          <div className="hidden sm:block">
            <Logo size={24} />
          </div>
          <span className="font-semibold text-sm text-slate-200 truncate hidden md:inline">
            {activeWorkspace === 'compare' ? activeConversationTitle || t.newComparison : 'MULTIVERSE'}
          </span>
        </div>

        {/* Workspace Switcher */}
        <nav aria-label="Primary Workspace" className="flex items-center gap-1 bg-space-950/70 p-1 rounded-xl border border-slate-800/80 ml-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = activeWorkspace === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectWorkspace(item.id)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                  active
                    ? 'bg-cyan-500 text-space-950 font-semibold shadow-sm'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-space-850'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
        <button
          onClick={toggleLanguage}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-space-850 hover:bg-space-800 border border-slate-700/60 text-xs font-semibold text-slate-300 hover:text-cyan-400 transition-all shadow-sm"
          title={t.changeLanguage}
        >
          <Globe className="w-3.5 h-3.5 text-cyan-400" />
          <span className="font-mono tracking-wider">{t.langLabel}</span>
        </button>

        {activeWorkspace === 'compare' && (
          <button
            onClick={onOpenModelSelector}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-space-850 hover:bg-space-800 border border-slate-700/60 text-xs font-medium text-slate-300 transition-all shadow-sm"
            title="Manage comparison models"
          >
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>{selectedModels.length} {t.modelsActive}</span>
          </button>
        )}

        <button
          onClick={onOpenKeyModal}
          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl border text-xs font-medium transition-all ${
            isKeyConfigured
              ? 'bg-emerald-950/40 text-emerald-300 border-emerald-800/50 hover:bg-emerald-900/40'
              : 'bg-amber-950/40 text-amber-300 border-amber-800/50 hover:bg-amber-900/40'
          }`}
          title={t.providersAndPolicy}
        >
          {isKeyConfigured ? (
            <>
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span className="hidden lg:inline">{t.nvidiaLive}</span>
            </>
          ) : (
            <>
              <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
              <span className="hidden lg:inline">{t.providersAndPolicy}</span>
            </>
          )}
        </button>
      </div>
    </header>
  );
};
