import React, { useEffect, useState } from 'react';
import {
  X,
  KeyRound,
  ExternalLink,
  ShieldCheck,
  ShieldAlert,
  Cpu,
  Server,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Lock,
} from 'lucide-react';
import { ExecutionPolicy, ProviderConfigItem, ProviderHealth } from '../types';
import { api } from '../services/api';

interface ApiKeyModalProps {
  isOpen: boolean;
  onClose: () => void;
  health: ProviderHealth | null;
  onRefreshHealth: () => void;
  onModelsUpdated?: () => void;
}

export const ApiKeyModal: React.FC<ApiKeyModalProps> = ({
  isOpen,
  onClose,
  health,
  onRefreshHealth,
  onModelsUpdated,
}) => {
  const [providers, setProviders] = useState<ProviderConfigItem[]>([]);
  const [policy, setPolicy] = useState<ExecutionPolicy>({
    local_only: false,
    free_only: true,
    max_calls_per_run: 24,
    max_parallel: 6,
  });
  const [urlEdits, setUrlEdits] = useState<Record<string, string>>({});
  const [testingId, setTestingId] = useState<string | null>(null);
  const [testMessages, setTestMessages] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!isOpen) return;
    loadProvidersAndPolicy();
  }, [isOpen]);

  const loadProvidersAndPolicy = async () => {
    try {
      const [provList, pol] = await Promise.all([api.getProviders(), api.getExecutionPolicy()]);
      setProviders(provList);
      setPolicy(pol);
      const map: Record<string, string> = {};
      provList.forEach((p) => {
        map[p.provider_id] = p.base_url;
      });
      setUrlEdits(map);
    } catch (err) {
      console.error('Failed loading providers/policy:', err);
    }
  };

  if (!isOpen) return null;

  const isConfigured = health?.api_key_set ?? false;
  const localProviders = providers.filter((p) => p.is_local);

  const handleTestAndSaveProvider = async (p: ProviderConfigItem) => {
    setTestingId(p.provider_id);
    try {
      const configured = await api.configureProvider({
        provider_id: p.provider_id,
        name: p.name,
        base_url: urlEdits[p.provider_id] || p.base_url,
        is_local: p.is_local,
        is_enabled: true,
      });
      setTestMessages((prev) => ({
        ...prev,
        [p.provider_id]:
          configured.status === 'connected'
            ? `Connected (${configured.discovered_models.length} model(s) discovered)`
            : configured.error || `Status: ${configured.status}`,
      }));
      await loadProvidersAndPolicy();
      onModelsUpdated?.();
    } catch (err: any) {
      setTestMessages((prev) => ({ ...prev, [p.provider_id]: err.message || 'Connection failed' }));
    } finally {
      setTestingId(null);
    }
  };

  const handlePolicyChange = async (patch: Partial<ExecutionPolicy>) => {
    try {
      const updated = await api.updateExecutionPolicy(patch);
      setPolicy(updated);
    } catch (err) {
      console.error('Failed updating policy:', err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-2xl max-h-[88vh] flex flex-col rounded-2xl bg-space-900 border border-slate-800 shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-space-800 border border-slate-700/60 flex items-center justify-center text-cyan-400">
              <KeyRound className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-slate-100">Providers, Local Models & Run Policy</h3>
              <p className="text-xs text-slate-400">NVIDIA NIM cloud endpoint, local OpenAI-compatible servers, and safety budgets</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-space-800 transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-5 custom-scrollbar">
          {/* NVIDIA Status */}
          <div
            className={`p-4 rounded-xl border flex items-start gap-3 ${
              isConfigured
                ? 'bg-emerald-950/30 border-emerald-800/60 text-emerald-200'
                : 'bg-amber-950/30 border-amber-800/60 text-amber-200'
            }`}
          >
            {isConfigured ? (
              <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            ) : (
              <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            )}
            <div className="space-y-1 text-xs flex-1">
              <h4 className="font-semibold text-sm">
                {isConfigured ? 'NVIDIA NIM API Key Active' : 'NVIDIA_API_KEY Not Configured in backend/.env'}
              </h4>
              <p className="text-slate-300 leading-relaxed">
                {isConfigured
                  ? 'API key is loaded server-side and never exposed in browser bundles.'
                  : 'Set NVIDIA_API_KEY in backend/.env or configure a local model server below.'}
              </p>
              <a
                href="https://build.nvidia.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-cyan-400 hover:text-cyan-300 font-medium pt-1"
              >
                <span>build.nvidia.com</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          {/* Execution Policy */}
          <div className="p-4 rounded-xl bg-space-950/70 border border-slate-800 space-y-3">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
              <Lock className="w-4 h-4 text-cyan-400" />
              <span>Execution & Budget Policy</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <label className="flex items-center justify-between p-2.5 rounded-lg bg-space-900 border border-slate-800 cursor-pointer">
                <span className="text-slate-300">Local-Only Mode (block external calls)</span>
                <input
                  type="checkbox"
                  checked={policy.local_only}
                  onChange={(e) => handlePolicyChange({ local_only: e.target.checked })}
                  className="accent-cyan-500 w-4 h-4"
                />
              </label>
              <label className="flex items-center justify-between p-2.5 rounded-lg bg-space-900 border border-slate-800 cursor-pointer">
                <span className="text-slate-300">Strict Free/Local Policy</span>
                <input
                  type="checkbox"
                  checked={policy.free_only}
                  onChange={(e) => handlePolicyChange({ free_only: e.target.checked })}
                  className="accent-cyan-500 w-4 h-4"
                />
              </label>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-300 pt-1">
              <span>Max Model Calls Per Run:</span>
              <input
                type="number"
                min={1}
                max={100}
                value={policy.max_calls_per_run}
                onChange={(e) => handlePolicyChange({ max_calls_per_run: Number(e.target.value) || 24 })}
                className="w-24 px-2.5 py-1 rounded-lg bg-space-900 border border-slate-700 text-slate-100 font-mono text-right"
              />
            </div>
          </div>

          {/* Local Providers */}
          <div className="space-y-2.5">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
              <Server className="w-4 h-4 text-cyan-400" />
              <span>Local OpenAI-Compatible Inference Servers</span>
            </div>
            {localProviders.map((prov) => {
              const msg = testMessages[prov.provider_id];
              const isConnected = prov.discovered_models.length > 0 || msg?.startsWith('Connected');
              return (
                <div
                  key={prov.provider_id}
                  className="p-3.5 rounded-xl bg-space-950/70 border border-slate-800 space-y-2 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200 flex items-center gap-2">
                      <Cpu className="w-3.5 h-3.5 text-slate-400" />
                      {prov.name}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium ${
                        isConnected
                          ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/60'
                          : 'bg-space-800 text-slate-400 border border-slate-700'
                      }`}
                    >
                      {isConnected ? <CheckCircle2 className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                      {prov.discovered_models.length} model(s)
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={urlEdits[prov.provider_id] ?? prov.base_url}
                      onChange={(e) => setUrlEdits((prev) => ({ ...prev, [prov.provider_id]: e.target.value }))}
                      className="flex-1 px-2.5 py-1.5 rounded-lg bg-space-900 border border-slate-700/80 text-slate-200 font-mono text-[11px]"
                    />
                    <button
                      type="button"
                      onClick={() => handleTestAndSaveProvider(prov)}
                      disabled={testingId === prov.provider_id}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-space-800 hover:bg-space-700 border border-slate-700 text-slate-200 font-medium transition-colors"
                    >
                      <RefreshCw className={`w-3 h-3 ${testingId === prov.provider_id ? 'animate-spin' : ''}`} />
                      <span>Test & Discover</span>
                    </button>
                  </div>
                  {msg && <p className="text-[11px] text-slate-400">{msg}</p>}
                </div>
              );
            })}
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 px-6 py-4 border-t border-slate-800">
          <button
            onClick={() => {
              onRefreshHealth();
              loadProvidersAndPolicy();
            }}
            className="px-4 py-2 text-xs font-semibold rounded-lg bg-space-800 hover:bg-space-700 text-slate-200 border border-slate-700/60 transition-colors"
          >
            Refresh Status
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
