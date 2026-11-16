import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Workflow as WorkflowIcon,
  Play,
  Save,
  Plus,
  Trash2,
  Download,
  Upload,
  CheckCircle2,
  AlertTriangle,
  ListTree,
  LayoutGrid,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Undo2,
  Redo2,
  Wand2,
  ShieldAlert,
  RefreshCw,
} from 'lucide-react';
import { api } from '../../services/api';
import {
  ModelInfo,
  WorkflowDefinition,
  WorkflowGraphEdge,
  WorkflowGraphNode,
  WorkflowNodeCatalogItem,
  WorkflowRun,
} from '../../types';

interface WorkflowsWorkspaceProps {
  models: ModelInfo[];
  initialInputText?: string;
}

const STATUS_STYLE: Record<string, string> = {
  succeeded: 'border-emerald-500/80 bg-emerald-950/30',
  running: 'border-cyan-400 bg-cyan-950/30',
  waiting_for_approval: 'border-amber-400 bg-amber-950/40',
  failed: 'border-rose-500/80 bg-rose-950/30',
  rejected: 'border-rose-500/60 bg-rose-950/20',
  skipped: 'border-slate-700 bg-space-900/50 opacity-60',
};

export const WorkflowsWorkspace: React.FC<WorkflowsWorkspaceProps> = ({
  models,
  initialInputText = '',
}) => {
  const [catalog, setCatalog] = useState<WorkflowNodeCatalogItem[]>([]);
  const [templates, setTemplates] = useState<WorkflowDefinition[]>([]);
  const [workflows, setWorkflows] = useState<WorkflowDefinition[]>([]);
  const [activeWorkflow, setActiveWorkflow] = useState<WorkflowDefinition | null>(null);

  const [name, setName] = useState<string>('Custom Workflow');
  const [description, setDescription] = useState<string>('');
  const [nodes, setNodes] = useState<WorkflowGraphNode[]>([]);
  const [edges, setEdges] = useState<WorkflowGraphEdge[]>([]);
  const [undoStack, setUndoStack] = useState<Array<{ nodes: WorkflowGraphNode[]; edges: WorkflowGraphEdge[] }>>([]);
  const [redoStack, setRedoStack] = useState<Array<{ nodes: WorkflowGraphNode[]; edges: WorkflowGraphEdge[] }>>([]);

  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [paletteQuery, setPaletteQuery] = useState<string>('');
  const [viewMode, setViewMode] = useState<'canvas' | 'accessible_list'>('canvas');
  const [zoom, setZoom] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 20, y: 20 });

  const [runInputText, setRunInputText] = useState<string>(initialInputText);
  const [runInputExpression, setRunInputExpression] = useState<string>('x^2 - 5x + 6 = 0');
  const [activeRun, setActiveRun] = useState<WorkflowRun | null>(null);
  const [validation, setValidation] = useState<{
    valid: boolean;
    errors: string[];
    warnings: string[];
    estimated_calls: number;
  } | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const [edgeSource, setEdgeSource] = useState<string>('');
  const [edgeHandle, setEdgeHandle] = useState<string>('');
  const [edgeTarget, setEdgeTarget] = useState<string>('');

  const draggingRef = useRef<{ nodeId: string; startX: number; startY: number; origX: number; origY: number } | null>(null);
  const importFileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (initialInputText) setRunInputText(initialInputText);
  }, [initialInputText]);

  useEffect(() => {
    loadAll();
  }, []);

  useEffect(() => {
    if (nodes.length === 0) {
      setValidation(null);
      return;
    }
    api
      .validateWorkflowGraph({ nodes, edges })
      .then(setValidation)
      .catch(() => {});
  }, [nodes, edges]);

  const loadAll = async () => {
    try {
      const [cat, tpls, wfs] = await Promise.all([
        api.getWorkflowNodeCatalog(),
        api.getWorkflowTemplates(),
        api.getWorkflows(),
      ]);
      setCatalog(cat);
      setTemplates(tpls);
      setWorkflows(wfs);
      if (!activeWorkflow && tpls.length > 0) {
        loadDefinition(tpls[0], false);
      }
    } catch (err) {
      console.error('Failed loading workflow metadata:', err);
    }
  };

  const pushHistory = (nextNodes: WorkflowGraphNode[], nextEdges: WorkflowGraphEdge[]) => {
    setUndoStack((prev) => [...prev.slice(-19), { nodes, edges }]);
    setRedoStack([]);
    setNodes(nextNodes);
    setEdges(nextEdges);
  };

  const handleUndo = () => {
    if (undoStack.length === 0) return;
    const prev = undoStack[undoStack.length - 1];
    setRedoStack((r) => [...r, { nodes, edges }]);
    setUndoStack((u) => u.slice(0, -1));
    setNodes(prev.nodes);
    setEdges(prev.edges);
  };

  const handleRedo = () => {
    if (redoStack.length === 0) return;
    const nxt = redoStack[redoStack.length - 1];
    setUndoStack((u) => [...u, { nodes, edges }]);
    setRedoStack((r) => r.slice(0, -1));
    setNodes(nxt.nodes);
    setEdges(nxt.edges);
  };

  const loadDefinition = (wf: WorkflowDefinition, isSaved: boolean = true) => {
    setActiveWorkflow(isSaved ? wf : null);
    setName(isSaved ? wf.name : `${wf.name} (Draft)`);
    setDescription(wf.description || '');
    setNodes(JSON.parse(JSON.stringify(wf.graph.nodes || [])));
    setEdges(JSON.parse(JSON.stringify(wf.graph.edges || [])));
    setSelectedNodeId(wf.graph.nodes?.[0]?.id || null);
    setActiveRun(null);
    setUndoStack([]);
    setRedoStack([]);
  };

  const handleAddNode = (item: WorkflowNodeCatalogItem) => {
    if (!item.available) return;
    const newId = `n_${Date.now().toString(36).slice(-4)}`;
    const newNode: WorkflowGraphNode = {
      id: newId,
      type: item.type,
      label: item.label,
      position: { x: 80 + (nodes.length % 4) * 240, y: 70 + Math.floor(nodes.length / 4) * 140 },
      config: { ...(item.default_config || {}) },
    };
    pushHistory([...nodes, newNode], edges);
    setSelectedNodeId(newId);
  };

  const handleDeleteNode = (nodeId: string) => {
    pushHistory(
      nodes.filter((n) => n.id !== nodeId),
      edges.filter((e) => e.source !== nodeId && e.target !== nodeId)
    );
    if (selectedNodeId === nodeId) setSelectedNodeId(null);
  };

  const handleAutoLayout = () => {
    const laidOut = nodes.map((n, idx) => ({
      ...n,
      position: { x: 40 + (idx % 4) * 250, y: 60 + Math.floor(idx / 4) * 150 },
    }));
    pushHistory(laidOut, edges);
  };

  const handleAddEdge = () => {
    if (!edgeSource || !edgeTarget || edgeSource === edgeTarget) return;
    const exists = edges.some(
      (e) => e.source === edgeSource && e.target === edgeTarget && (e.sourceHandle || '') === edgeHandle
    );
    if (exists) return;
    const newEdge: WorkflowGraphEdge = {
      id: `e_${Date.now().toString(36).slice(-4)}`,
      source: edgeSource,
      target: edgeTarget,
      sourceHandle: edgeHandle || undefined,
    };
    pushHistory(nodes, [...edges, newEdge]);
  };

  const handleSave = async (): Promise<WorkflowDefinition | null> => {
    try {
      let saved: WorkflowDefinition;
      if (activeWorkflow && !activeWorkflow.is_template) {
        saved = await api.updateWorkflow(activeWorkflow.id, {
          name,
          description,
          graph: { nodes, edges },
        });
      } else {
        saved = await api.createWorkflow({
          name,
          description,
          graph: { nodes, edges },
        });
      }
      setActiveWorkflow(saved);
      setStatusMessage(`Saved workflow v${saved.version}.`);
      await loadAll();
      return saved;
    } catch (err: any) {
      setStatusMessage(`Save failed: ${err.message}`);
      return null;
    }
  };

  const handleRun = async () => {
    setIsRunning(true);
    setStatusMessage(null);
    try {
      const wf = await handleSave();
      if (!wf) return;
      const run = await api.runWorkflow(wf.id, {
        text: runInputText || 'Analyze and summarize key steps.',
        question: runInputText || 'Analyze and summarize key steps.',
        expression: runInputExpression,
      });
      setActiveRun(run);
    } catch (err: any) {
      setStatusMessage(`Execution error: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const handleApprove = async (nodeId: string, approved: boolean) => {
    if (!activeRun) return;
    setIsRunning(true);
    try {
      const updated = await api.approveWorkflowRun(activeRun.id, nodeId, approved);
      setActiveRun(updated);
    } catch (err: any) {
      setStatusMessage(err.message);
    } finally {
      setIsRunning(false);
    }
  };

  const handleRetryNode = async (nodeId: string) => {
    if (!activeRun) return;
    setIsRunning(true);
    try {
      const updated = await api.retryWorkflowNode(activeRun.id, nodeId);
      setActiveRun(updated);
    } catch (err: any) {
      setStatusMessage(err.message);
    } finally {
      setIsRunning(false);
    }
  };

  const handleExportJson = async () => {
    if (!activeWorkflow) {
      const blob = new Blob([JSON.stringify({ name, description, graph: { nodes, edges } }, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${name.toLowerCase().replace(/\s+/g, '_')}.json`;
      a.click();
      URL.revokeObjectURL(url);
      return;
    }
    const data = await api.exportWorkflowJson(activeWorkflow.id);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activeWorkflow.name.toLowerCase().replace(/\s+/g, '_')}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImportJson = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const raw = JSON.parse(await file.text());
      const res = await api.importWorkflow(raw, true);
      if (res.saved_workflow) {
        loadDefinition(res.saved_workflow, true);
      }
      if (res.import_warnings?.length) {
        setStatusMessage(`Imported with safety notices: ${res.import_warnings.join(' | ')}`);
      } else {
        setStatusMessage('Workflow imported cleanly.');
      }
      await loadAll();
    } catch (err: any) {
      setStatusMessage(`Import failed: ${err.message}`);
    } finally {
      e.target.value = '';
    }
  };

  const selectedNode = useMemo(() => nodes.find((n) => n.id === selectedNodeId) || null, [nodes, selectedNodeId]);

  const filteredCatalog = useMemo(() => {
    const q = paletteQuery.trim().toLowerCase();
    if (!q) return catalog;
    return catalog.filter(
      (c) =>
        c.label.toLowerCase().includes(q) ||
        c.type.toLowerCase().includes(q) ||
        c.category.toLowerCase().includes(q)
    );
  }, [catalog, paletteQuery]);

  const handleNodePointerDown = (e: React.PointerEvent, node: WorkflowGraphNode) => {
    e.stopPropagation();
    setSelectedNodeId(node.id);
    draggingRef.current = {
      nodeId: node.id,
      startX: e.clientX,
      startY: e.clientY,
      origX: node.position.x,
      origY: node.position.y,
    };
  };

  const handleCanvasPointerMove = (e: React.PointerEvent) => {
    if (!draggingRef.current) return;
    const { nodeId, startX, startY, origX, origY } = draggingRef.current;
    const dx = (e.clientX - startX) / zoom;
    const dy = (e.clientY - startY) / zoom;
    setNodes((prev) =>
      prev.map((n) =>
        n.id === nodeId ? { ...n, position: { x: Math.max(10, Math.round(origX + dx)), y: Math.max(10, Math.round(origY + dy)) } } : n
      )
    );
  };

  const handleCanvasPointerUp = () => {
    draggingRef.current = null;
  };

  return (
    <div className="flex-1 flex flex-col lg:flex-row overflow-hidden bg-space-950">
      {/* Left Palette & Templates */}
      <div className="w-full lg:w-72 border-b lg:border-b-0 lg:border-r border-slate-800 bg-space-900/70 flex flex-col max-h-64 lg:max-h-full overflow-hidden">
        <div className="p-3 border-b border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
            <span className="flex items-center gap-1.5">
              <WorkflowIcon className="w-4 h-4 text-cyan-400" />
              Node Palette & Templates
            </span>
          </div>
          <input
            type="text"
            value={paletteQuery}
            onChange={(e) => setPaletteQuery(e.target.value)}
            placeholder="Search nodes..."
            className="w-full px-2.5 py-1.5 rounded-lg bg-space-950 border border-slate-800 text-xs text-slate-200"
          />
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-4 custom-scrollbar text-xs">
          {/* Templates */}
          <div className="space-y-1.5">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Templates</div>
            {templates.map((tpl) => (
              <button
                key={tpl.id}
                onClick={() => loadDefinition(tpl, false)}
                className="w-full text-left p-2 rounded-lg bg-space-950/70 hover:bg-space-800 border border-slate-800 transition-colors"
              >
                <div className="font-medium text-slate-200">{tpl.name}</div>
                <div className="text-[10px] text-slate-500 line-clamp-1">{tpl.description}</div>
              </button>
            ))}
          </div>

          {/* Saved Workflows */}
          {workflows.length > 0 && (
            <div className="space-y-1.5">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Saved Workflows</div>
              {workflows.map((wf) => (
                <button
                  key={wf.id}
                  onClick={() => loadDefinition(wf, true)}
                  className={`w-full text-left p-2 rounded-lg border transition-colors ${
                    activeWorkflow?.id === wf.id
                      ? 'bg-space-800 border-cyan-500/60 text-cyan-200'
                      : 'bg-space-950/70 hover:bg-space-800 border-slate-800 text-slate-300'
                  }`}
                >
                  <div className="font-medium truncate">{wf.name} (v{wf.version})</div>
                </button>
              ))}
            </div>
          )}

          {/* Node Catalog */}
          <div className="space-y-1.5">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Add Node</div>
            {filteredCatalog.map((item) => (
              <button
                key={item.type}
                type="button"
                disabled={!item.available}
                onClick={() => handleAddNode(item)}
                title={item.unavailable_reason || item.description}
                className={`w-full text-left p-2 rounded-lg border flex items-center justify-between transition-colors ${
                  item.available
                    ? 'bg-space-950 hover:bg-space-800 border-slate-800 text-slate-200'
                    : 'bg-space-950/40 border-slate-800/50 text-slate-500 cursor-not-allowed'
                }`}
              >
                <div>
                  <div className="font-medium">{item.label}</div>
                  <div className="text-[10px] text-slate-500">{item.category}</div>
                </div>
                {item.available ? (
                  <Plus className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                ) : (
                  <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">Disabled</span>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Center Canvas / List + Run Output */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Toolbar */}
        <div className="p-3 border-b border-slate-800 bg-space-900/50 flex flex-wrap items-center justify-between gap-2 text-xs">
          <div className="flex items-center gap-2 min-w-0">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg bg-space-950 border border-slate-800 font-semibold text-slate-100 w-48"
            />
            <button onClick={handleUndo} disabled={undoStack.length === 0} className="p-1.5 rounded-lg bg-space-800 disabled:opacity-40 text-slate-300" title="Undo">
              <Undo2 className="w-3.5 h-3.5" />
            </button>
            <button onClick={handleRedo} disabled={redoStack.length === 0} className="p-1.5 rounded-lg bg-space-800 disabled:opacity-40 text-slate-300" title="Redo">
              <Redo2 className="w-3.5 h-3.5" />
            </button>
            <button onClick={handleAutoLayout} className="p-1.5 rounded-lg bg-space-800 text-slate-300" title="Auto Layout">
              <Wand2 className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setViewMode((m) => (m === 'canvas' ? 'accessible_list' : 'canvas'))}
              className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-space-800 text-slate-200"
            >
              {viewMode === 'canvas' ? <ListTree className="w-3.5 h-3.5" /> : <LayoutGrid className="w-3.5 h-3.5" />}
              <span>{viewMode === 'canvas' ? 'List View' : 'Canvas'}</span>
            </button>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <input ref={importFileRef} type="file" accept=".json" onChange={handleImportJson} className="hidden" />
            <button
              onClick={() => importFileRef.current?.click()}
              className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-space-800 hover:bg-space-700 text-slate-200"
            >
              <Upload className="w-3.5 h-3.5" /> Import
            </button>
            <button
              onClick={handleExportJson}
              className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-space-800 hover:bg-space-700 text-slate-200"
            >
              <Download className="w-3.5 h-3.5" /> Export JSON
            </button>
            <button
              onClick={handleSave}
              className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-space-800 hover:bg-space-700 border border-slate-700 text-slate-100 font-medium"
            >
              <Save className="w-3.5 h-3.5 text-cyan-400" /> Save
            </button>
            <button
              onClick={handleRun}
              disabled={isRunning || (validation ? !validation.valid : false)}
              className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-space-950 font-semibold"
            >
              <Play className="w-3.5 h-3.5" /> {isRunning ? 'Running...' : 'Run Workflow'}
            </button>
          </div>
        </div>

        {/* Validation & Run Inputs */}
        <div className="px-4 py-2 border-b border-slate-800 bg-space-950 flex flex-wrap items-center justify-between gap-2 text-xs">
          <div className="flex flex-wrap items-center gap-2 flex-1">
            <input
              type="text"
              value={runInputText}
              onChange={(e) => setRunInputText(e.target.value)}
              placeholder="Workflow input text / question..."
              className="flex-1 min-w-[200px] px-2.5 py-1 rounded-lg bg-space-900 border border-slate-800 text-slate-200"
            />
            <input
              type="text"
              value={runInputExpression}
              onChange={(e) => setRunInputExpression(e.target.value)}
              placeholder="Optional math expression"
              className="w-48 px-2.5 py-1 rounded-lg bg-space-900 border border-slate-800 text-slate-200 font-mono"
            />
          </div>
          {validation && (
            <div className="flex items-center gap-2">
              {validation.valid ? (
                <span className="inline-flex items-center gap-1 text-emerald-300">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Valid Graph • ~{validation.estimated_calls} call(s)
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 text-rose-300">
                  <AlertTriangle className="w-3.5 h-3.5" /> {validation.errors[0]}
                </span>
              )}
            </div>
          )}
        </div>

        {statusMessage && (
          <div className="px-4 py-1.5 bg-space-900 border-b border-slate-800 text-xs text-cyan-300">{statusMessage}</div>
        )}

        {/* Canvas or Accessible List */}
        {viewMode === 'canvas' ? (
          <div
            className="relative flex-1 overflow-auto bg-[radial-gradient(#1f2c45_1px,transparent_1px)] [background-size:20px_20px]"
            onPointerMove={handleCanvasPointerMove}
            onPointerUp={handleCanvasPointerUp}
          >
            {/* Zoom Controls */}
            <div className="sticky top-3 left-3 z-20 inline-flex items-center gap-1 p-1 rounded-lg bg-space-900/90 border border-slate-800 m-3">
              <button onClick={() => setZoom((z) => Math.max(0.6, z - 0.1))} className="p-1 text-slate-300 hover:text-white">
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
              <span className="text-[11px] font-mono text-slate-400 px-1">{Math.round(zoom * 100)}%</span>
              <button onClick={() => setZoom((z) => Math.min(1.5, z + 0.1))} className="p-1 text-slate-300 hover:text-white">
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
              <button onClick={() => { setZoom(1); setPan({ x: 20, y: 20 }); }} className="p-1 text-slate-300 hover:text-white">
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            </div>

            <div
              className="relative min-w-[1280px] min-h-[540px]"
              style={{ transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`, transformOrigin: 'top left' }}
            >
              {/* SVG Edges */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none">
                <defs>
                  <marker id="mv-arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
                    <path d="M0,0 L0,6 L8,3 z" fill="#38BDF8" />
                  </marker>
                </defs>
                {edges.map((edge) => {
                  const src = nodes.find((n) => n.id === edge.source);
                  const tgt = nodes.find((n) => n.id === edge.target);
                  if (!src || !tgt) return null;
                  const x1 = src.position.x + 190;
                  const y1 = src.position.y + 42;
                  const x2 = tgt.position.x;
                  const y2 = tgt.position.y + 42;
                  const mx = (x1 + x2) / 2;
                  const pathD = `M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`;
                  return (
                    <g key={edge.id}>
                      <path d={pathD} stroke="#38BDF8" strokeWidth="2" fill="none" strokeOpacity="0.65" markerEnd="url(#mv-arrow)" />
                      {edge.sourceHandle && (
                        <text x={mx} y={(y1 + y2) / 2 - 6} fill="#94A3B8" fontSize="10" textAnchor="middle">
                          {edge.sourceHandle}
                        </text>
                      )}
                    </g>
                  );
                })}
              </svg>

              {/* Nodes */}
              {nodes.map((node) => {
                const state = activeRun?.node_states?.[node.id];
                const styleCls = state ? STATUS_STYLE[state.status] || 'border-slate-700 bg-space-900' : 'border-slate-700/80 bg-space-900';
                const isSel = selectedNodeId === node.id;
                return (
                  <div
                    key={node.id}
                    onPointerDown={(e) => handleNodePointerDown(e, node)}
                    style={{ left: node.position.x, top: node.position.y }}
                    className={`absolute w-[190px] rounded-xl border p-3 shadow-lg cursor-grab active:cursor-grabbing select-none transition-shadow ${styleCls} ${
                      isSel ? 'ring-2 ring-cyan-400' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1 mb-1">
                      <span className="text-[10px] font-mono uppercase text-cyan-400">{node.type}</span>
                      <span className="text-[10px] font-mono text-slate-500">{node.id}</span>
                    </div>
                    <div className="text-xs font-semibold text-slate-100 truncate">{node.label || node.type}</div>
                    {state && (
                      <div className="mt-1.5 flex items-center justify-between text-[10px]">
                        <span className="font-mono text-slate-300">{state.status}</span>
                        {state.status === 'failed' && activeRun && (
                          <button
                            onClick={(ev) => { ev.stopPropagation(); handleRetryNode(node.id); }}
                            className="text-amber-300 hover:underline flex items-center gap-0.5"
                          >
                            <RefreshCw className="w-2.5 h-2.5" /> Retry
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          /* Accessible Keyboard List Mode */
          <div className="flex-1 overflow-y-auto p-4 space-y-2 custom-scrollbar">
            {nodes.map((node, idx) => (
              <div
                key={node.id}
                onClick={() => setSelectedNodeId(node.id)}
                tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && setSelectedNodeId(node.id)}
                className={`p-3 rounded-xl border flex items-center justify-between cursor-pointer ${
                  selectedNodeId === node.id ? 'bg-space-850 border-cyan-500' : 'bg-space-900 border-slate-800'
                }`}
              >
                <div>
                  <div className="text-xs font-semibold text-slate-100">
                    {idx + 1}. {node.label || node.type} ({node.type})
                  </div>
                  <div className="text-[11px] font-mono text-slate-500">
                    ID: {node.id} • Edges out:{' '}
                    {edges.filter((e) => e.source === node.id).map((e) => `${e.sourceHandle || 'next'}->${e.target}`).join(', ') || 'none'}
                  </div>
                </div>
                <span className="text-[11px] font-mono text-cyan-300">{activeRun?.node_states?.[node.id]?.status || 'ready'}</span>
              </div>
            ))}
          </div>
        )}

        {/* Active Run Results & Approval Bar */}
        {activeRun && (
          <div className="h-56 border-t border-slate-800 bg-space-900/90 p-3 overflow-y-auto custom-scrollbar space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-200">
                Run Status: <span className="font-mono text-cyan-300">{activeRun.status}</span> (Calls: {activeRun.usage?.calls || 0})
              </span>
            </div>

            {Object.entries(activeRun.node_states).map(([nid, st]) => (
              <div key={nid} className="p-2.5 rounded-lg bg-space-950 border border-slate-800 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-slate-200 font-semibold">
                    {nid} — {st.status}
                  </span>
                  {st.status === 'waiting_for_approval' && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleApprove(nid, true)}
                        className="px-2.5 py-1 rounded bg-emerald-500 text-space-950 font-semibold"
                      >
                        Approve & Continue
                      </button>
                      <button
                        onClick={() => handleApprove(nid, false)}
                        className="px-2.5 py-1 rounded bg-rose-500 text-white font-semibold"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </div>
                <div className="text-[11px] text-slate-400">{st.logs?.join(' | ')}</div>
                {activeRun.outputs?.[nid]?.download_url && (
                  <a
                    href={activeRun.outputs[nid].download_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-cyan-400 hover:underline font-medium"
                  >
                    <Download className="w-3 h-3" /> Download Generated Artifact
                  </a>
                )}
                {activeRun.outputs?.[nid]?.output && !activeRun.outputs?.[nid]?.download_url && (
                  <pre className="text-[11px] text-slate-300 whitespace-pre-wrap max-h-24 overflow-y-auto bg-space-900 p-2 rounded">
                    {String(activeRun.outputs[nid].output).slice(0, 1200)}
                  </pre>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Right Inspector */}
      <div className="w-full lg:w-72 border-t lg:border-t-0 lg:border-l border-slate-800 bg-space-900/70 p-3 overflow-y-auto custom-scrollbar space-y-4 text-xs">
        <div className="font-semibold text-slate-200 border-b border-slate-800 pb-2">Node Inspector & Edges</div>

        {selectedNode ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-mono text-cyan-300">{selectedNode.id} ({selectedNode.type})</span>
              <button onClick={() => handleDeleteNode(selectedNode.id)} className="text-rose-400 hover:text-rose-300">
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Label</label>
              <input
                type="text"
                value={selectedNode.label || ''}
                onChange={(e) =>
                  setNodes((prev) =>
                    prev.map((n) => (n.id === selectedNode.id ? { ...n, label: e.target.value } : n))
                  )
                }
                className="w-full px-2.5 py-1.5 rounded-lg bg-space-950 border border-slate-800 text-slate-200"
              />
            </div>

            {selectedNode.type === 'model' && (
              <div>
                <label className="text-[11px] text-slate-400 block mb-1">Model</label>
                <select
                  value={selectedNode.config.model_id || ''}
                  onChange={(e) =>
                    setNodes((prev) =>
                      prev.map((n) =>
                        n.id === selectedNode.id ? { ...n, config: { ...n.config, model_id: e.target.value } } : n
                      )
                    )
                  }
                  className="w-full px-2 py-1.5 rounded-lg bg-space-950 border border-slate-800 text-slate-200"
                >
                  {models.map((m) => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))}
                </select>
              </div>
            )}

            {(selectedNode.type === 'code' || selectedNode.type === 'webhook') && selectedNode.config.approved_by_owner === false && (
              <div className="p-2.5 rounded-lg bg-amber-950/50 border border-amber-700/60 space-y-2 text-amber-200">
                <div className="flex items-center gap-1.5 font-semibold">
                  <ShieldAlert className="w-3.5 h-3.5" /> Imported Node Disabled
                </div>
                <button
                  onClick={() =>
                    setNodes((prev) =>
                      prev.map((n) =>
                        n.id === selectedNode.id ? { ...n, config: { ...n.config, approved_by_owner: true } } : n
                      )
                    )
                  }
                  className="w-full py-1 rounded bg-amber-500 text-space-950 font-semibold"
                >
                  Approve Node Execution
                </button>
              </div>
            )}

            <div>
              <label className="text-[11px] text-slate-400 block mb-1">Config JSON</label>
              <textarea
                rows={6}
                value={JSON.stringify(selectedNode.config, null, 2)}
                onChange={(e) => {
                  try {
                    const parsed = JSON.parse(e.target.value);
                    setNodes((prev) =>
                      prev.map((n) => (n.id === selectedNode.id ? { ...n, config: parsed } : n))
                    );
                  } catch {
                    // Wait until valid JSON
                  }
                }}
                className="w-full p-2 rounded-lg bg-space-950 border border-slate-800 font-mono text-[11px] text-slate-200"
              />
            </div>
          </div>
        ) : (
          <p className="text-slate-500">Select a node on the canvas to configure it.</p>
        )}

        {/* Edge Builder */}
        <div className="pt-3 border-t border-slate-800 space-y-2">
          <div className="font-semibold text-slate-300">Connect Nodes</div>
          <select value={edgeSource} onChange={(e) => setEdgeSource(e.target.value)} className="w-full px-2 py-1 rounded bg-space-950 border border-slate-800 text-slate-200">
            <option value="">Source node...</option>
            {nodes.map((n) => <option key={n.id} value={n.id}>{n.id} ({n.label || n.type})</option>)}
          </select>
          <select value={edgeHandle} onChange={(e) => setEdgeHandle(e.target.value)} className="w-full px-2 py-1 rounded bg-space-950 border border-slate-800 text-slate-200">
            <option value="">Branch: default</option>
            <option value="true">true</option>
            <option value="false">false</option>
            <option value="approved">approved</option>
            <option value="rejected">rejected</option>
          </select>
          <select value={edgeTarget} onChange={(e) => setEdgeTarget(e.target.value)} className="w-full px-2 py-1 rounded bg-space-950 border border-slate-800 text-slate-200">
            <option value="">Target node...</option>
            {nodes.map((n) => <option key={n.id} value={n.id}>{n.id} ({n.label || n.type})</option>)}
          </select>
          <button onClick={handleAddEdge} className="w-full py-1.5 rounded-lg bg-space-800 hover:bg-space-700 text-cyan-300 font-medium">
            + Add Edge
          </button>

          <div className="space-y-1 max-h-32 overflow-y-auto pt-1">
            {edges.map((e) => (
              <div key={e.id} className="flex items-center justify-between text-[11px] font-mono text-slate-400 bg-space-950 px-2 py-1 rounded">
                <span>{e.source} {e.sourceHandle ? `[${e.sourceHandle}]` : ''} → {e.target}</span>
                <button onClick={() => pushHistory(nodes, edges.filter((x) => x.id !== e.id))} className="text-rose-400">×</button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
