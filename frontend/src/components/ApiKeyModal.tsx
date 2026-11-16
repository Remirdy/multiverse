import React from 'react';
import { X, KeyRound, ExternalLink, ShieldCheck, ShieldAlert, Cpu } from 'lucide-react';
import { ProviderHealth } from '../types';

interface ApiKeyModalProps {
  isOpen: boolean;
  onClose: () => void;
  health: ProviderHealth | null;
  onRefreshHealth: () => void;
}

export const ApiKeyModal: React.FC<ApiKeyModalProps> = ({
  isOpen,
  onClose,
  health,
  onRefreshHealth,
}) => {
  if (!isOpen) return null;

  const isConfigured = health?.api_key_set ?? false;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-lg rounded-2xl bg-space-900 border border-slate-800 shadow-2xl overflow-hidden p-6 space-y-5">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-space-800 border border-slate-700/60 flex items-center justify-center text-cyan-400">
              <KeyRound className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-100">NVIDIA Build API Status</h3>
              <p className="text-xs text-slate-400">Official NVIDIA NIM endpoint integration</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-space-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Status Box */}
        <div className={`p-4 rounded-xl border flex items-start gap-3 ${
          isConfigured
            ? 'bg-emerald-950/30 border-emerald-800/60 text-emerald-200'
            : 'bg-amber-950/30 border-amber-800/60 text-amber-200'
        }`}>
          {isConfigured ? (
            <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          )}
          <div className="space-y-1 text-xs">
            <h4 className="font-semibold text-sm">
              {isConfigured ? 'NVIDIA API Key Active' : 'API Key Pending in backend/.env'}
            </h4>
            <p className="text-slate-300 leading-relaxed">
              {isConfigured
                ? 'Your backend has a valid NVIDIA API Key configured. Prompts are dispatched directly to live NVIDIA NIM models.'
                : 'To query live models, create a backend/.env file and set your NVIDIA_API_KEY from build.nvidia.com.'}
            </p>
          </div>
        </div>

        {/* Configuration instructions */}
        <div className="space-y-2 text-xs text-slate-300 bg-space-950/70 p-4 rounded-xl border border-slate-800 font-mono">
          <div className="flex items-center justify-between text-slate-400 font-sans font-medium text-[11px] mb-1">
            <span>Configuration Path</span>
            <span>backend/.env</span>
          </div>
          <div className="p-2 rounded bg-space-900 border border-slate-800/80 text-cyan-300 select-all overflow-x-auto">
            NVIDIA_API_KEY=nvapi-your-key-here<br />
            NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
          </div>
        </div>

        <div className="space-y-2 text-xs text-slate-400">
          <p className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-slate-500" />
            <span>Endpoint: <code className="text-slate-300 font-mono">https://integrate.api.nvidia.com/v1</code></span>
          </p>
          <a
            href="https://build.nvidia.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-cyan-400 hover:text-cyan-300 font-medium"
          >
            <span>Get your NVIDIA NIM API Key at build.nvidia.com</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>

        <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
          <button
            onClick={onRefreshHealth}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-space-800 hover:bg-space-700 text-slate-200 border border-slate-700/60 transition-colors"
          >
            Check Status
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-cyan-500 hover:bg-cyan-400 text-space-950 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
