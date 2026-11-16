import React, { useEffect, useState } from 'react';
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  RotateCcw,
  Calculator,
  Cpu,
  Code2,
  GitBranch,
  Terminal,
} from 'lucide-react';
import { api } from '../../services/api';
import { MarkdownRenderer } from '../../components/MarkdownRenderer';

export const InteractiveLearningPanel: React.FC = () => {
  const [toolTab, setToolTab] = useState<'algorithms' | 'math' | 'electronics' | 'codelab' | 'latex'>('algorithms');

  // Algorithms state
  const [algName, setAlgName] = useState<string>('quick_sort');
  const [algInput, setAlgInput] = useState<string>('38, 27, 43, 3, 9, 82, 10');
  const [algTrace, setAlgTrace] = useState<any>(null);
  const [stepIdx, setStepIdx] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [pseudoCodeIn, setPseudoCodeIn] = useState<string>('def binary_search(arr, target):\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1');
  const [pseudoRes, setPseudoRes] = useState<any>(null);

  // Math & Numerical state
  const [mathMode, setMathMode] = useState<'plot' | 'symbolic' | 'numerical'>('plot');
  const [mathExpr, setMathExpr] = useState<string>('x^3 - 4*x');
  const [mathOp, setMathOp] = useState<string>('diff');
  const [numMethod, setNumMethod] = useState<string>('newton_raphson');
  const [plotData, setPlotData] = useState<any>(null);
  const [symResult, setSymResult] = useState<any>(null);
  const [numResult, setNumResult] = useState<any>(null);

  // Electronics state
  const [elecTopo, setElecTopo] = useState<string>('rc_transient');
  const [elecParams, setElecParams] = useState<{ vin: number; r1: number; r2: number; c: number }>({
    vin: 5,
    r1: 1000,
    r2: 2000,
    c: 0.0001,
  });
  const [elecRes, setElecRes] = useState<any>(null);

  // Code Lab & LaTeX
  const [codeSrc, setCodeSrc] = useState<string>('def factorial(n):\n    return 1 if n <= 1 else n * factorial(n - 1)\n\nprint("5! =", factorial(5))');
  const [codeRes, setCodeRes] = useState<any>(null);
  const [latexText, setLatexText] = useState<string>('$$\\int_0^\\pi \\sin(x)\\,dx = 2$$\n\n$$E = \\frac{1}{2}CV^2$$');

  useEffect(() => {
    runAlgorithm();
    runPlot();
    runElectronics();
  }, []);

  useEffect(() => {
    if (!isPlaying || !algTrace?.steps?.length) return;
    const timer = setInterval(() => {
      setStepIdx((prev) => {
        if (prev >= algTrace.steps.length - 1) {
          setIsPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, 550);
    return () => clearInterval(timer);
  }, [isPlaying, algTrace]);

  const runAlgorithm = async () => {
    setIsPlaying(false);
    setStepIdx(0);
    try {
      const arr = algInput
        .split(',')
        .map((s) => Number(s.trim()))
        .filter((n) => !Number.isNaN(n));
      const res = await api.runAlgorithmTool({
        mode: 'algorithm',
        algorithm: algName,
        array: arr.length ? arr : [38, 27, 43, 3, 9, 82, 10],
        target: arr[2] ?? 43,
      });
      setAlgTrace(res);
    } catch (err: any) {
      setAlgTrace({ error: err.message });
    }
  };

  const runPseudocode = async () => {
    const res = await api.runAlgorithmTool({ mode: 'pseudocode', code: pseudoCodeIn, language: 'python' });
    setPseudoRes(res);
  };

  const runPlot = async () => {
    try {
      const res = await api.runMathTool({ action: 'plot_1d', expression: mathExpr, x_min: -5, x_max: 5 });
      setPlotData(res);
    } catch (err: any) {
      setPlotData({ error: err.message });
    }
  };

  const runSymbolic = async () => {
    try {
      const res = await api.runMathTool({ action: 'symbolic', operation: mathOp, expression: mathExpr, variable: 'x' });
      setSymResult(res);
    } catch (err: any) {
      setSymResult({ error: err.message });
    }
  };

  const runNumerical = async () => {
    try {
      const res = await api.runMathTool({
        action: 'numerical',
        operation: numMethod,
        expression: mathExpr,
        a: -1,
        b: 3,
        x0: 1.5,
        x1: 2.5,
      });
      setNumResult(res);
    } catch (err: any) {
      setNumResult({ error: err.message });
    }
  };

  const runElectronics = async () => {
    try {
      const res = await api.runElectronicsTool({
        topology: elecTopo,
        params: {
          vin: elecParams.vin,
          voltage: elecParams.vin,
          r: elecParams.r1,
          r1: elecParams.r1,
          r2: elecParams.r2,
          r3: 300,
          c: elecParams.c,
          resistors: [elecParams.r1, elecParams.r2],
          connection: 'series',
        },
      });
      setElecRes(res);
    } catch (err: any) {
      setElecRes({ error: err.message });
    }
  };

  const runCode = async () => {
    const res = await api.runCodeLab({ code: codeSrc });
    setCodeRes(res);
  };

  const activeStep = algTrace?.steps?.[stepIdx] || null;
  const maxBar = useMemoValue(activeStep?.array || []);

  function useMemoValue(arr: number[]) {
    return Math.max(1, ...arr.map((n) => Math.abs(n)));
  }

  return (
    <div className="space-y-4">
      {/* Sub-tool Pills */}
      <div className="flex flex-wrap gap-2 text-xs">
        {[
          { id: 'algorithms', label: 'Algorithms & Pseudocode', icon: GitBranch },
          { id: 'math', label: 'Math Plotter & Numerical', icon: Calculator },
          { id: 'electronics', label: 'Electronics Circuits', icon: Cpu },
          { id: 'codelab', label: 'Python Sandbox', icon: Terminal },
          { id: 'latex', label: 'LaTeX Live Editor', icon: Code2 },
        ].map((t) => {
          const Icon = t.icon;
          return (
            <button
              key={t.id}
              onClick={() => setToolTab(t.id as any)}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border font-medium transition-colors ${
                toolTab === t.id
                  ? 'bg-cyan-500/20 border-cyan-500 text-cyan-300'
                  : 'bg-space-900 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{t.label}</span>
            </button>
          );
        })}
      </div>

      {/* Algorithms */}
      {toolTab === 'algorithms' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="rounded-2xl bg-space-900 border border-slate-800 p-4 space-y-3 text-xs">
            <div className="flex flex-wrap items-center gap-2">
              <select
                value={algName}
                onChange={(e) => setAlgName(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg bg-space-950 border border-slate-700 text-slate-200"
              >
                <option value="bubble_sort">Bubble Sort</option>
                <option value="selection_sort">Selection Sort</option>
                <option value="insertion_sort">Insertion Sort</option>
                <option value="merge_sort">Merge Sort</option>
                <option value="quick_sort">Quick Sort</option>
                <option value="linear_search">Linear Search</option>
                <option value="binary_search">Binary Search</option>
                <option value="bfs">Graph BFS</option>
                <option value="dfs">Graph DFS</option>
                <option value="dijkstra">Graph Dijkstra</option>
              </select>
              <input
                type="text"
                value={algInput}
                onChange={(e) => setAlgInput(e.target.value)}
                className="flex-1 px-2.5 py-1.5 rounded-lg bg-space-950 border border-slate-800 font-mono text-slate-200"
              />
              <button onClick={runAlgorithm} className="px-3 py-1.5 rounded-lg bg-cyan-500 text-space-950 font-semibold">
                Trace
              </button>
            </div>

            {algTrace?.steps && (
              <>
                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span>{algTrace.complexity}</span>
                  <span>
                    Step {stepIdx + 1}/{algTrace.steps.length} • Comparisons: {algTrace.comparisons ?? '-'} • Swaps:{' '}
                    {algTrace.swaps ?? '-'}
                  </span>
                </div>

                {activeStep?.array && (
                  <div className="h-44 flex items-end justify-center gap-2 p-3 rounded-xl bg-space-950 border border-slate-800">
                    {activeStep.array.map((val: number, i: number) => {
                      const isCmp = activeStep.comparing?.includes(i);
                      const isSwap = activeStep.swapped?.includes(i);
                      const isSorted = activeStep.sorted?.includes(i);
                      const barCls = isSwap
                        ? 'bg-amber-400'
                        : isCmp
                        ? 'bg-cyan-400'
                        : isSorted
                        ? 'bg-emerald-400'
                        : 'bg-slate-600';
                      return (
                        <div key={i} className="flex-1 flex flex-col items-center justify-end h-full">
                          <span className="text-[10px] font-mono text-slate-300 mb-1">{val}</span>
                          <div
                            className={`w-full rounded-t transition-all ${barCls}`}
                            style={{ height: `${Math.max(12, Math.round((Math.abs(val) / maxBar) * 110))}px` }}
                          />
                        </div>
                      );
                    })}
                  </div>
                )}

                {activeStep && !activeStep.array && (
                  <div className="p-3 rounded-xl bg-space-950 border border-slate-800 font-mono text-[11px] space-y-1">
                    <div>Current Node: {activeStep.current}</div>
                    <div>Visited: {JSON.stringify(activeStep.visited)}</div>
                    {activeStep.distances && <div>Distances: {JSON.stringify(activeStep.distances)}</div>}
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <button onClick={() => setStepIdx(0)} className="p-1.5 rounded bg-space-800 text-slate-300" aria-label="Reset">
                      <RotateCcw className="w-3.5 h-3.5" />
                    </button>
                    <button onClick={() => setStepIdx((s) => Math.max(0, s - 1))} className="p-1.5 rounded bg-space-800 text-slate-300" aria-label="Back">
                      <SkipBack className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => setIsPlaying((p) => !p)}
                      className="px-3 py-1 rounded bg-cyan-500 text-space-950 font-semibold inline-flex items-center gap-1"
                    >
                      {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
                      <span>{isPlaying ? 'Pause' : 'Play'}</span>
                    </button>
                    <button
                      onClick={() => setStepIdx((s) => Math.min(algTrace.steps.length - 1, s + 1))}
                      className="p-1.5 rounded bg-space-800 text-slate-300"
                      aria-label="Forward"
                    >
                      <SkipForward className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <span className="text-[11px] text-slate-400 truncate max-w-[220px]">
                    {activeStep?.description || ''}
                  </span>
                </div>
              </>
            )}
          </div>

          {/* Pseudocode Generator */}
          <div className="rounded-2xl bg-space-900 border border-slate-800 p-4 space-y-3 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-200">Python-to-Pseudocode & Complexity</span>
              <button onClick={runPseudocode} className="px-3 py-1.5 rounded-lg bg-space-800 hover:bg-space-700 text-cyan-300">
                Convert
              </button>
            </div>
            <textarea
              rows={7}
              value={pseudoCodeIn}
              onChange={(e) => setPseudoCodeIn(e.target.value)}
              className="w-full p-2.5 rounded-xl bg-space-950 border border-slate-800 font-mono text-[11px] text-slate-200"
            />
            {pseudoRes && (
              <div className="p-3 rounded-xl bg-space-950 border border-slate-800 space-y-1">
                <div className="text-[11px] text-emerald-300 font-semibold">{pseudoRes.complexity_hint}</div>
                <pre className="text-[11px] font-mono text-slate-300 whitespace-pre-wrap">{pseudoRes.pseudocode}</pre>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Math & Numerical */}
      {toolTab === 'math' && (
        <div className="rounded-2xl bg-space-900 border border-slate-800 p-4 space-y-3 text-xs">
          <div className="flex flex-wrap items-center gap-2">
            <button onClick={() => setMathMode('plot')} className={`px-3 py-1 rounded-lg ${mathMode === 'plot' ? 'bg-cyan-500 text-space-950 font-semibold' : 'bg-space-800 text-slate-300'}`}>1D Plotter</button>
            <button onClick={() => setMathMode('symbolic')} className={`px-3 py-1 rounded-lg ${mathMode === 'symbolic' ? 'bg-cyan-500 text-space-950 font-semibold' : 'bg-space-800 text-slate-300'}`}>Symbolic SymPy</button>
            <button onClick={() => setMathMode('numerical')} className={`px-3 py-1 rounded-lg ${mathMode === 'numerical' ? 'bg-cyan-500 text-space-950 font-semibold' : 'bg-space-800 text-slate-300'}`}>Numerical Methods</button>
            <input
              type="text"
              value={mathExpr}
              onChange={(e) => setMathExpr(e.target.value)}
              className="flex-1 min-w-[180px] px-2.5 py-1.5 rounded-lg bg-space-950 border border-slate-800 font-mono text-slate-100"
            />
            {mathMode === 'plot' && (
              <button onClick={runPlot} className="px-3 py-1.5 rounded-lg bg-cyan-500 text-space-950 font-semibold">Plot</button>
            )}
            {mathMode === 'symbolic' && (
              <>
                <select value={mathOp} onChange={(e) => setMathOp(e.target.value)} className="px-2 py-1.5 rounded-lg bg-space-950 border border-slate-700 text-slate-200">
                  <option value="simplify">Simplify</option>
                  <option value="solve">Solve (=0)</option>
                  <option value="diff">Derivative d/dx</option>
                  <option value="integrate">Integral</option>
                  <option value="series">Taylor Series</option>
                </select>
                <button onClick={runSymbolic} className="px-3 py-1.5 rounded-lg bg-cyan-500 text-space-950 font-semibold">Compute</button>
              </>
            )}
            {mathMode === 'numerical' && (
              <>
                <select value={numMethod} onChange={(e) => setNumMethod(e.target.value)} className="px-2 py-1.5 rounded-lg bg-space-950 border border-slate-700 text-slate-200">
                  <option value="bisection">Bisection</option>
                  <option value="newton_raphson">Newton-Raphson</option>
                  <option value="secant">Secant</option>
                  <option value="trapezoidal">Trapezoidal Integral</option>
                  <option value="simpson">Simpson Integral</option>
                </select>
                <button onClick={runNumerical} className="px-3 py-1.5 rounded-lg bg-cyan-500 text-space-950 font-semibold">Iterate</button>
              </>
            )}
          </div>

          {mathMode === 'plot' && plotData?.points && (
            <div className="space-y-2">
              <FunctionSvgPlot points={plotData.points} />
              {plotData.domain_restrictions?.length > 0 && (
                <div className="text-[11px] text-amber-300">Domain: {plotData.domain_restrictions.join(' | ')}</div>
              )}
            </div>
          )}
          {mathMode === 'symbolic' && symResult && (
            <div className="p-3 rounded-xl bg-space-950 border border-slate-800 space-y-1 font-mono">
              <div className="text-emerald-300">Result: {JSON.stringify(symResult.result)}</div>
              <div className="text-slate-400">LaTeX: {symResult.latex}</div>
            </div>
          )}
          {mathMode === 'numerical' && numResult && (
            <div className="p-3 rounded-xl bg-space-950 border border-slate-800 space-y-2">
              <div className="font-mono text-cyan-300">
                Result: {String(numResult.result)} • Converged: {String(numResult.converged)}
              </div>
              {numResult.warning && <div className="text-amber-300">{numResult.warning}</div>}
              <div className="max-h-40 overflow-y-auto">
                <table className="w-full text-left font-mono text-[11px]">
                  <thead>
                    <tr className="text-slate-400 border-b border-slate-800">
                      <th className="py-1">Iter</th>
                      <th>x</th>
                      <th>f(x)</th>
                      <th>Error</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(numResult.iterations || []).map((r: any, idx: number) => (
                      <tr key={idx} className="border-b border-slate-900">
                        <td className="py-1">{r.iteration ?? r.i}</td>
                        <td>{r.x}</td>
                        <td>{r.fx}</td>
                        <td>{r.error ?? '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Electronics */}
      {toolTab === 'electronics' && (
        <div className="rounded-2xl bg-space-900 border border-slate-800 p-4 space-y-3 text-xs">
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={elecTopo}
              onChange={(e) => setElecTopo(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg bg-space-950 border border-slate-700 text-slate-200"
            >
              <option value="ohms_law">Ohm's Law</option>
              <option value="series_parallel">Series / Parallel Resistors</option>
              <option value="voltage_divider">Voltage Divider</option>
              <option value="rc_transient">RC Step Transient</option>
              <option value="rc_ac_filter">RC Low-Pass AC Filter</option>
              <option value="kvl_kcl_loop">Two-Loop KVL / KCL Bridge</option>
            </select>
            <label className="flex items-center gap-1 text-slate-300">
              V: <input type="number" value={elecParams.vin} onChange={(e) => setElecParams({ ...elecParams, vin: Number(e.target.value) })} className="w-16 px-2 py-1 rounded bg-space-950 border border-slate-800" />
            </label>
            <label className="flex items-center gap-1 text-slate-300">
              R1(Ω): <input type="number" value={elecParams.r1} onChange={(e) => setElecParams({ ...elecParams, r1: Number(e.target.value) })} className="w-20 px-2 py-1 rounded bg-space-950 border border-slate-800" />
            </label>
            <label className="flex items-center gap-1 text-slate-300">
              R2(Ω): <input type="number" value={elecParams.r2} onChange={(e) => setElecParams({ ...elecParams, r2: Number(e.target.value) })} className="w-20 px-2 py-1 rounded bg-space-950 border border-slate-800" />
            </label>
            <button onClick={runElectronics} className="px-3 py-1.5 rounded-lg bg-cyan-500 text-space-950 font-semibold">
              Solve Circuit
            </button>
          </div>
          {elecRes && !elecRes.error && (
            <div className="p-3 rounded-xl bg-space-950 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-[11px] text-slate-400">
                <span>Engine: {elecRes.simulation_engine}</span>
                <span>ngspice binary: {elecRes.ngspice_available ? 'installed' : 'not installed (analytical solver active)'}</span>
              </div>
              <pre className="font-mono text-[11px] text-cyan-300">{JSON.stringify(elecRes.values, null, 2)}</pre>
              <ul className="list-disc pl-4 text-slate-300 space-y-0.5">
                {(elecRes.steps || []).map((s: string, i: number) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Code Lab */}
      {toolTab === 'codelab' && (
        <div className="rounded-2xl bg-space-900 border border-slate-800 p-4 space-y-3 text-xs">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-slate-200">Isolated Python Code Lab (No network / host access)</span>
            <button onClick={runCode} className="px-4 py-1.5 rounded-lg bg-cyan-500 text-space-950 font-semibold">
              Run in Sandbox
            </button>
          </div>
          <textarea
            rows={7}
            value={codeSrc}
            onChange={(e) => setCodeSrc(e.target.value)}
            className="w-full p-3 rounded-xl bg-space-950 border border-slate-800 font-mono text-slate-100"
          />
          {codeRes && (
            <div className="p-3 rounded-xl bg-space-950 border border-slate-800 font-mono text-[11px] space-y-1">
              <div className="text-cyan-300">Status: {codeRes.status} (exit {codeRes.exit_code})</div>
              {codeRes.stdout && <pre className="text-emerald-300 whitespace-pre-wrap">{codeRes.stdout}</pre>}
              {codeRes.stderr && <pre className="text-rose-300 whitespace-pre-wrap">{codeRes.stderr}</pre>}
            </div>
          )}
        </div>
      )}

      {/* LaTeX Editor */}
      {toolTab === 'latex' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="rounded-2xl bg-space-900 border border-slate-800 p-4 space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-200">LaTeX Source</span>
              <div className="flex gap-1">
                {['\\frac{a}{b}', '\\sum_{i=1}^n', '\\int_a^b'].map((sym) => (
                  <button
                    key={sym}
                    onClick={() => setLatexText((t) => `${t} $${sym}$`)}
                    className="px-2 py-0.5 rounded bg-space-800 text-cyan-300 font-mono text-[10px]"
                  >
                    {sym}
                  </button>
                ))}
              </div>
            </div>
            <textarea
              rows={8}
              value={latexText}
              onChange={(e) => setLatexText(e.target.value)}
              className="w-full p-3 rounded-xl bg-space-950 border border-slate-800 font-mono text-slate-100"
            />
          </div>
          <div className="rounded-2xl bg-space-900 border border-slate-800 p-4 space-y-2">
            <div className="text-xs font-semibold text-slate-200">KaTeX Live Preview</div>
            <MarkdownRenderer content={latexText} />
          </div>
        </div>
      )}
    </div>
  );
};

const FunctionSvgPlot: React.FC<{ points: Array<{ x: number; y: number | null; dy?: number | null }> }> = ({ points }) => {
  const validY = points.map((p) => p.y).filter((v): v is number => v !== null);
  const minX = points[0]?.x ?? -5;
  const maxX = points[points.length - 1]?.x ?? 5;
  const minY = validY.length ? Math.min(-1, ...validY) : -5;
  const maxY = validY.length ? Math.max(1, ...validY) : 5;
  const w = 640;
  const h = 210;

  const toSx = (x: number) => ((x - minX) / (maxX - minX || 1)) * (w - 40) + 20;
  const toSy = (y: number) => h - 20 - ((y - minY) / (maxY - minY || 1)) * (h - 40);

  let dPath = '';
  points.forEach((p) => {
    if (p.y === null) return;
    const cmd = dPath === '' || dPath.endsWith(' ') ? 'M' : 'L';
    dPath += `${cmd}${toSx(p.x).toFixed(1)},${toSy(p.y).toFixed(1)} `;
  });

  const zeroY = toSy(0);
  const zeroX = toSx(0);

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full h-52 rounded-xl bg-space-950 border border-slate-800">
      {zeroY >= 0 && zeroY <= h && <line x1="20" y1={zeroY} x2={w - 20} y2={zeroY} stroke="#334155" strokeWidth="1" />}
      {zeroX >= 0 && zeroX <= w && <line x1={zeroX} y1="15" x2={zeroX} y2={h - 15} stroke="#334155" strokeWidth="1" />}
      <path d={dPath} fill="none" stroke="#38BDF8" strokeWidth="2.5" />
    </svg>
  );
};
