import React, { useEffect, useState } from 'react';
import {
  Users,
  Play,
  Plus,
  Trash2,
  RotateCcw,
  GitFork,
  Download,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ShieldCheck,
  BookOpen,
  Workflow,
  PauseCircle,
  Ban,
} from 'lucide-react';
import { api } from '../../services/api';
import {
  ArtifactRef,
  CouncilMember,
  CouncilPreset,
  CouncilRole,
  CouncilSession,
  ModelInfo,
} from '../../types';
import { MarkdownRenderer } from '../../components/MarkdownRenderer';

interface CouncilWorkspaceProps {
  models: ModelInfo[];
  initialPrompt?: string;
  onSaveToNotebook?: (title: string, content: string, origin: string) => void;
  onSendToWorkflow?: (text: string) => void;
}

export const CouncilWorkspace: React.FC<CouncilWorkspaceProps> = ({
  models,
  initialPrompt = '',
  onSaveToNotebook,
  onSendToWorkflow,
}) => {
  const [roles, setRoles] = useState<CouncilRole[]>([]);
  const [presets, setPresets] = useState<CouncilPreset[]>([]);
  const [sessions, setSessions] = useState<CouncilSession[]>([]);
  const [activeSession, setActiveSession] = useState<CouncilSession | null>(null);

  const [selectedPresetId, setSelectedPresetId] = useState<string>('general_review');
  const [prompt, setPrompt] = useState<string>(initialPrompt);
  const [instructions, setInstructions] = useState<string>('');
  const [members, setMembers] = useState<CouncilMember[]>([
    { role_id: 'researcher', model_id: 'nvidia/nemotron-3-ultra-550b-a55b' },
    { role_id: 'critic', model_id: 'poolside/laguna-xs-2.1' },
    { role_id: 'fact_checker', model_id: 'nvidia/nemotron-3.5-lightning-30b-a3b' },
  ]);
  const [chairModelId, setChairModelId] = useState<string>('nvidia/nemotron-3-ultra-550b-a55b');
  const [reviewRounds, setReviewRounds] = useState<number>(1);
  const [enableReview, setEnableReview] = useState<boolean>(true);
  const [enableVerification, setEnableVerification] = useState<boolean>(true);
  const [pauseAfterProposals, setPauseAfterProposals] = useState<boolean>(false);

  const [estimate, setEstimate] = useState<any>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [exportedArtifact, setExportedArtifact] = useState<ArtifactRef | null>(null);
  const [historyFilter, setHistoryFilter] = useState<string>('');

  useEffect(() => {
    if (initialPrompt) setPrompt(initialPrompt);
  }, [initialPrompt]);

  useEffect(() => {
    loadInitial();
  }, []);

  useEffect(() => {
    api
      .estimateCouncil({ members, review_rounds: reviewRounds, enable_review: enableReview })
      .then(setEstimate)
      .catch(() => {});
  }, [members, reviewRounds, enableReview]);

  const loadInitial = async () => {
    try {
      const [r, p, s] = await Promise.all([
        api.getCouncilRoles(),
        api.getCouncilPresets(),
        api.getCouncilSessions(),
      ]);
      setRoles(r);
      setPresets(p);
      setSessions(s);
    } catch (err) {
      console.error('Failed loading council data:', err);
    }
  };

  const applyPreset = (presetId: string) => {
    setSelectedPresetId(presetId);
    const found = presets.find((p) => p.id === presetId);
    if (found) {
      setMembers(found.config.members.map((m) => ({ ...m })));
      setChairModelId(found.config.chair_model_id);
      setReviewRounds(found.config.review_rounds ?? 1);
      setEnableVerification(found.config.enable_verification ?? true);
    }
  };

  const handleAddMember = () => {
    const fallbackModel = models[0]?.id || 'poolside/laguna-xs-2.1';
    setMembers((prev) => [...prev, { role_id: 'reviewer', model_id: fallbackModel }]);
  };

  const handleRunCouncil = async () => {
    if (!prompt.trim()) {
      setErrorMsg('Please enter a question or problem for the Council.');
      return;
    }
    setErrorMsg(null);
    setExportedArtifact(null);
    setIsRunning(true);
    try {
      const session = await api.createCouncilSession({
        prompt,
        preset_id: selectedPresetId,
        members,
        chair_model_id: chairModelId,
        review_rounds: reviewRounds,
        enable_review: enableReview,
        enable_verification: enableVerification,
        instructions: instructions || undefined,
        pause_after_proposals: pauseAfterProposals,
      });
      setActiveSession(session);
      await loadInitial();
    } catch (err: any) {
      setErrorMsg(err.message || 'Council execution failed.');
    } finally {
      setIsRunning(false);
    }
  };

  const handleResume = async () => {
    if (!activeSession) return;
    setIsRunning(true);
    try {
      const updated = await api.resumeCouncilSession(activeSession.id);
      setActiveSession(updated);
      await loadInitial();
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setIsRunning(false);
    }
  };

  const handleCancelJob = async () => {
    if (!activeSession?.job_id) return;
    try {
      await api.cancelJob(activeSession.job_id);
      const updated = await api.getCouncilSessions();
      setSessions(updated);
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const handleRetryMember = async (memberIdx: number) => {
    if (!activeSession) return;
    setIsRunning(true);
    try {
      const updated = await api.retryCouncilMember(activeSession.id, memberIdx);
      setActiveSession(updated);
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setIsRunning(false);
    }
  };

  const handleFork = async () => {
    if (!activeSession) return;
    setIsRunning(true);
    try {
      const forked = await api.forkCouncilSession(activeSession.id);
      setActiveSession(forked);
      await loadInitial();
    } catch (err: any) {
      setErrorMsg(err.message);
    } finally {
      setIsRunning(false);
    }
  };

  const handleExport = async (fmt: string, includeFull: boolean) => {
    if (!activeSession) return;
    try {
      const art = await api.exportCouncilSession(activeSession.id, fmt, includeFull);
      setExportedArtifact(art);
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  const filteredSessions = sessions.filter((s) => {
    if (!historyFilter.trim()) return true;
    const q = historyFilter.toLowerCase();
    return s.title.toLowerCase().includes(q) || s.prompt.toLowerCase().includes(q);
  });

  return (
    <div className="flex-1 flex flex-col lg:flex-row overflow-hidden bg-space-950">
      {/* History Column */}
      <div className="w-full lg:w-72 border-b lg:border-b-0 lg:border-r border-slate-800 bg-space-900/60 flex flex-col max-h-56 lg:max-h-full">
        <div className="p-3 border-b border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
            <span className="flex items-center gap-1.5">
              <Users className="w-4 h-4 text-cyan-400" />
              Council Sessions
            </span>
            <button
              onClick={() => setActiveSession(null)}
              className="px-2 py-1 rounded bg-space-800 hover:bg-space-700 text-[11px] text-cyan-300"
            >
              + New
            </button>
          </div>
          <input
            type="text"
            value={historyFilter}
            onChange={(e) => setHistoryFilter(e.target.value)}
            placeholder="Filter sessions..."
            className="w-full px-2.5 py-1.5 rounded-lg bg-space-950 border border-slate-800 text-xs text-slate-200"
          />
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
          {filteredSessions.length === 0 ? (
            <p className="text-xs text-slate-500 p-3 text-center">No Council sessions yet.</p>
          ) : (
            filteredSessions.map((s) => (
              <div
                key={s.id}
                onClick={() => {
                  setActiveSession(s);
                  setPrompt(s.prompt);
                }}
                className={`p-2.5 rounded-xl cursor-pointer border text-xs transition-colors ${
                  activeSession?.id === s.id
                    ? 'bg-space-800 border-cyan-500/50 text-slate-100'
                    : 'bg-space-950/40 border-transparent hover:bg-space-850 text-slate-400'
                }`}
              >
                <div className="font-medium truncate">{s.title}</div>
                <div className="flex items-center justify-between text-[10px] text-slate-500 mt-1">
                  <span>{s.status}</span>
                  <span>{s.usage?.calls || 0} calls</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Council Workspace */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 custom-scrollbar">
        <div className="max-w-5xl mx-auto space-y-6">
          {/* Configuration Card */}
          <div className="rounded-2xl bg-space-900/90 border border-slate-800 p-5 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-base font-semibold text-slate-100">Multi-Model Council</h2>
                <p className="text-xs text-slate-400">
                  Independent parallel proposals, anonymized peer critique, deterministic verification, and Chair synthesis.
                </p>
              </div>
              <select
                value={selectedPresetId}
                onChange={(e) => applyPreset(e.target.value)}
                className="px-3 py-1.5 rounded-xl bg-space-950 border border-slate-700 text-xs text-slate-200"
              >
                {presets.map((p) => (
                  <option key={p.id} value={p.id}>
                    Preset: {p.name}
                  </option>
                ))}
              </select>
            </div>

            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={3}
              placeholder="Enter a technical, mathematical, coding, or research problem for the Council..."
              className="w-full p-3 rounded-xl bg-space-950 border border-slate-800 text-sm text-slate-100 focus:outline-none focus:border-cyan-500"
            />

            <input
              type="text"
              value={instructions}
              onChange={(e) => setInstructions(e.target.value)}
              placeholder="Optional instructions (language, rubric, constraints)..."
              className="w-full px-3 py-2 rounded-xl bg-space-950 border border-slate-800 text-xs text-slate-200"
            />

            {/* Role & Model Matrix */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-300">Council Members ({members.length})</span>
                <button
                  type="button"
                  onClick={handleAddMember}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-space-800 hover:bg-space-700 text-cyan-300"
                >
                  <Plus className="w-3.5 h-3.5" /> Add Member
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {members.map((m, idx) => (
                  <div key={idx} className="flex items-center gap-2 p-2 rounded-xl bg-space-950 border border-slate-800">
                    <select
                      value={m.role_id}
                      onChange={(e) =>
                        setMembers((prev) =>
                          prev.map((item, i) => (i === idx ? { ...item, role_id: e.target.value } : item))
                        )
                      }
                      className="px-2 py-1.5 rounded-lg bg-space-900 border border-slate-700 text-xs text-slate-200"
                    >
                      {roles.map((r) => (
                        <option key={r.id} value={r.id}>
                          {r.name}
                        </option>
                      ))}
                    </select>
                    <select
                      value={m.model_id}
                      onChange={(e) =>
                        setMembers((prev) =>
                          prev.map((item, i) => (i === idx ? { ...item, model_id: e.target.value } : item))
                        )
                      }
                      className="flex-1 min-w-0 px-2 py-1.5 rounded-lg bg-space-900 border border-slate-700 text-xs text-slate-200"
                    >
                      {models.map((mod) => (
                        <option key={mod.id} value={mod.id}>
                          {mod.name} {mod.is_local ? '(Local)' : ''}
                        </option>
                      ))}
                    </select>
                    {members.length > 1 && (
                      <button
                        type="button"
                        onClick={() => setMembers((prev) => prev.filter((_, i) => i !== idx))}
                        className="p-1.5 text-slate-500 hover:text-rose-400"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Chair & Options */}
            <div className="flex flex-wrap items-center gap-4 text-xs pt-2 border-t border-slate-800">
              <label className="flex items-center gap-2 text-slate-300">
                <span>Chair:</span>
                <select
                  value={chairModelId}
                  onChange={(e) => setChairModelId(e.target.value)}
                  className="px-2.5 py-1 rounded-lg bg-space-950 border border-slate-700 text-slate-200"
                >
                  {models.map((mod) => (
                    <option key={mod.id} value={mod.id}>
                      {mod.name}
                    </option>
                  ))}
                </select>
              </label>

              <label className="flex items-center gap-2 text-slate-300">
                <span>Revision Rounds:</span>
                <select
                  value={reviewRounds}
                  onChange={(e) => setReviewRounds(Number(e.target.value))}
                  className="px-2 py-1 rounded-lg bg-space-950 border border-slate-700 text-slate-200"
                >
                  <option value={0}>0</option>
                  <option value={1}>1</option>
                  <option value={2}>2</option>
                </select>
              </label>

              <label className="flex items-center gap-1.5 text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableReview}
                  onChange={(e) => setEnableReview(e.target.checked)}
                  className="accent-cyan-500"
                />
                <span>Peer Review</span>
              </label>

              <label className="flex items-center gap-1.5 text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={enableVerification}
                  onChange={(e) => setEnableVerification(e.target.checked)}
                  className="accent-cyan-500"
                />
                <span>Deterministic Checks</span>
              </label>

              <label className="flex items-center gap-1.5 text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={pauseAfterProposals}
                  onChange={(e) => setPauseAfterProposals(e.target.checked)}
                  className="accent-cyan-500"
                />
                <span>Pause After Proposals</span>
              </label>
            </div>

            {/* Estimate & Run Bar */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
              <div className="text-xs text-slate-400 space-y-1">
                {estimate && (
                  <div>
                    Estimated calls: <span className="font-mono text-cyan-300">{estimate.estimated_calls}</span> (
                    {estimate.unique_models} distinct model(s))
                  </div>
                )}
                {estimate?.warnings?.map((w: string, i: number) => (
                  <div key={i} className="flex items-center gap-1.5 text-amber-300">
                    <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                    <span>{w}</span>
                  </div>
                ))}
              </div>

              <div className="flex items-center gap-2">
                {isRunning && activeSession?.job_id && (
                  <button
                    type="button"
                    onClick={handleCancelJob}
                    className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-rose-950/60 border border-rose-700/60 text-xs font-semibold text-rose-200"
                  >
                    <Ban className="w-3.5 h-3.5" /> Cancel
                  </button>
                )}
                <button
                  type="button"
                  onClick={handleRunCouncil}
                  disabled={isRunning}
                  className="inline-flex items-center gap-2 px-5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-space-950 text-xs font-semibold transition-colors"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>{isRunning ? 'Running Council...' : 'Run Council'}</span>
                </button>
              </div>
            </div>

            {errorMsg && (
              <div className="p-3 rounded-xl bg-rose-950/40 border border-rose-800/60 text-xs text-rose-200">
                {errorMsg}
              </div>
            )}
          </div>

          {/* Active Session Results */}
          {activeSession && (
            <div className="space-y-5">
              {/* Status & Actions */}
              <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-2xl bg-space-900 border border-slate-800 text-xs">
                <div className="flex items-center gap-2.5">
                  <span className="px-2.5 py-1 rounded-full bg-space-800 border border-slate-700 font-mono text-cyan-300">
                    {activeSession.status}
                  </span>
                  <span className="text-slate-400">
                    Calls: {activeSession.usage?.calls || 0} • Tokens: {activeSession.usage?.tokens || 0}
                  </span>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  {activeSession.status === 'waiting_for_approval' && (
                    <button
                      onClick={handleResume}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500 text-space-950 font-semibold"
                    >
                      <PauseCircle className="w-3.5 h-3.5" /> Resume Synthesis
                    </button>
                  )}
                  <button
                    onClick={handleFork}
                    className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-space-800 hover:bg-space-700 text-slate-200"
                  >
                    <GitFork className="w-3.5 h-3.5" /> Fork
                  </button>
                  {['pdf', 'docx', 'md', 'json'].map((fmt) => (
                    <button
                      key={fmt}
                      onClick={() => handleExport(fmt, true)}
                      className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-space-800 hover:bg-space-700 text-slate-200 uppercase"
                    >
                      <Download className="w-3 h-3" /> {fmt}
                    </button>
                  ))}
                  {onSaveToNotebook && activeSession.synthesis?.final_answer && (
                    <button
                      onClick={() =>
                        onSaveToNotebook(
                          activeSession.title,
                          activeSession.synthesis?.final_answer || '',
                          'council'
                        )
                      }
                      className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-indigo-950/60 border border-indigo-700/60 text-indigo-200"
                    >
                      <BookOpen className="w-3.5 h-3.5" /> Save to Notebook
                    </button>
                  )}
                  {onSendToWorkflow && activeSession.synthesis?.final_answer && (
                    <button
                      onClick={() => onSendToWorkflow(activeSession.synthesis?.final_answer || '')}
                      className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-cyan-950/60 border border-cyan-700/60 text-cyan-200"
                    >
                      <Workflow className="w-3.5 h-3.5" /> Use in Workflow
                    </button>
                  )}
                </div>
              </div>

              {exportedArtifact && (
                <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-800/60 flex items-center justify-between text-xs text-emerald-200">
                  <span>Export ready: {exportedArtifact.filename}</span>
                  <a
                    href={exportedArtifact.download_url}
                    download={exportedArtifact.filename}
                    className="px-3 py-1 rounded-lg bg-emerald-500 text-space-950 font-semibold"
                  >
                    Download
                  </a>
                </div>
              )}

              {/* Chair Synthesis */}
              {activeSession.synthesis && (
                <div className="rounded-2xl bg-space-900 border border-cyan-500/40 p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-cyan-300 flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4" />
                      Chair Synthesis ({activeSession.synthesis.chair_model_id})
                    </h3>
                    <span className="text-[11px] font-mono text-slate-400">
                      {activeSession.synthesis.status}
                    </span>
                  </div>
                  <MarkdownRenderer content={activeSession.synthesis.final_answer || ''} />
                </div>
              )}

              {/* Disagreements & Deterministic Verification */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div className="rounded-2xl bg-space-900 border border-slate-800 p-4 space-y-2">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-amber-300">
                    Preserved Disagreements
                  </h4>
                  {activeSession.disagreements.length === 0 ? (
                    <p className="text-xs text-slate-500">No explicit dissent reported by reviewers.</p>
                  ) : (
                    <ul className="space-y-1.5 text-xs text-slate-300">
                      {activeSession.disagreements.map((d, i) => (
                        <li key={i} className="p-2 rounded-lg bg-space-950 border border-slate-800">
                          <span className="font-semibold text-amber-300 mr-1.5">[{d.source}]</span>
                          {d.point}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                <div className="rounded-2xl bg-space-900 border border-slate-800 p-4 space-y-2">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-emerald-300 flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4" /> Deterministic Verification
                  </h4>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {activeSession.verifications.map((v, i) => (
                      <li key={i} className="p-2 rounded-lg bg-space-950 border border-slate-800">
                        <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-0.5">
                          <span>{v.tool}</span>
                          <span>{v.status}</span>
                        </div>
                        <p>{v.summary}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Independent Proposals */}
              <div className="space-y-2">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Independent Member Proposals
                </h4>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {activeSession.proposals.map((p) => (
                    <div key={p.member_index} className="rounded-2xl bg-space-900 border border-slate-800 p-4 space-y-2">
                      <div className="flex items-center justify-between text-xs">
                        <div>
                          <span className="font-semibold text-slate-100">{p.label}: {p.role_name}</span>
                          <span className="block font-mono text-[10px] text-slate-500">{p.model_id}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-[11px] text-slate-400 flex items-center gap-1">
                            <Clock className="w-3 h-3" /> {p.response_time_ms ?? '-'}ms
                          </span>
                          {p.status !== 'success' && (
                            <button
                              onClick={() => handleRetryMember(p.member_index)}
                              className="inline-flex items-center gap-1 px-2 py-1 rounded bg-amber-950/60 border border-amber-700 text-amber-200 text-[11px]"
                            >
                              <RotateCcw className="w-3 h-3" /> Retry
                            </button>
                          )}
                        </div>
                      </div>
                      {p.status === 'success' ? (
                        <MarkdownRenderer content={p.response_text || ''} />
                      ) : (
                        <p className="text-xs text-rose-300">{p.error_message || `Status: ${p.status}`}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
