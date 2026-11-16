import React, { useEffect, useState } from 'react';
import {
  BookOpen,
  FileUp,
  CheckCircle2,
  GraduationCap,
  Layers,
  Calendar,
  BarChart3,
  Presentation,
  Sparkles,
  Download,
  Trash2,
  Users,
  Languages,
  Mic,
  Plus,
} from 'lucide-react';
import { api } from '../../services/api';
import {
  ArtifactRef,
  FlashcardDeck,
  ModelInfo,
  StudyAssignment,
  StudyExam,
  StudyNotebook,
  StudyPlan,
} from '../../types';
import { MarkdownRenderer } from '../../components/MarkdownRenderer';
import { InteractiveLearningPanel } from './InteractiveLearningPanel';

interface StudyLabWorkspaceProps {
  models: ModelInfo[];
  onOpenInCouncil?: (question: string) => void;
  onSendToWorkflow?: (text: string) => void;
}

export const StudyLabWorkspace: React.FC<StudyLabWorkspaceProps> = ({
  models,
  onOpenInCouncil,
  onSendToWorkflow,
}) => {
  const [section, setSection] = useState<'solve' | 'practice' | 'materials' | 'progress'>('solve');
  const [solveTab, setSolveTab] = useState<'assignment' | 'verifier' | 'tutor' | 'interactive'>('assignment');

  const [selectedModelId, setSelectedModelId] = useState<string>(models[0]?.id || 'nvidia/nemotron-3.5-lightning-30b-a3b');

  // Shared documents & assignments
  const [documents, setDocuments] = useState<ArtifactRef[]>([]);
  const [assignments, setAssignments] = useState<StudyAssignment[]>([]);
  const [activeAssignment, setActiveAssignment] = useState<StudyAssignment | null>(null);
  const [assignTitle, setAssignTitle] = useState<string>('Homework Set 1');
  const [assignQuestionText, setAssignQuestionText] = useState<string>('Solve x^2 - 5x + 6 = 0 step by step.');
  const [assignMode, setAssignMode] = useState<string>('step_by_step');
  const [assignLang, setAssignLang] = useState<string>('en');
  const [exportedUrl, setExportedUrl] = useState<string | null>(null);

  // Verifier
  const [verQuestion, setVerQuestion] = useState<string>('Expand (x + 1)^2');
  const [verStudent, setVerStudent] = useState<string>('x^2 + 2*x + 1');
  const [verExpected, setVerExpected] = useState<string>('x^2 + 2*x + 1');
  const [verResult, setVerResult] = useState<any>(null);

  // Tutor & Language Tutor
  const [tutorPrompt, setTutorPrompt] = useState<string>('Explain eigenvalues intuitively.');
  const [tutorLevel, setTutorLevel] = useState<string>('intermediate');
  const [tutorMode, setTutorMode] = useState<string>('tutor');
  const [tutorReply, setTutorReply] = useState<string>('');
  const [langText, setLangText] = useState<string>('I goes to school yesterday.');
  const [langReply, setLangReply] = useState<string>('');

  // Practice: Flashcards & Exam
  const [decks, setDecks] = useState<FlashcardDeck[]>([]);
  const [activeDeck, setActiveDeck] = useState<FlashcardDeck | null>(null);
  const [cardIdx, setCardIdx] = useState<number>(0);
  const [showCardBack, setShowCardBack] = useState<boolean>(false);
  const [newDeckTitle, setNewDeckTitle] = useState<string>('Calculus Core');
  const [newCardFront, setNewCardFront] = useState<string>('Derivative of sin(x)');
  const [newCardBack, setNewCardBack] = useState<string>('cos(x)');

  const [exams, setExams] = useState<StudyExam[]>([]);
  const [activeExam, setActiveExam] = useState<StudyExam | null>(null);
  const [examAnswers, setExamAnswers] = useState<Record<string, string>>({});
  const [examAttemptResult, setExamAttemptResult] = useState<any>(null);

  // Materials: Notebooks, PDF Chat, Lecture, PPTX
  const [notebooks, setNotebooks] = useState<StudyNotebook[]>([]);
  const [activeNotebook, setActiveNotebook] = useState<StudyNotebook | null>(null);
  const [newNbTitle, setNewNbTitle] = useState<string>('EE201 Circuits & Math');
  const [pdfChatQ, setPdfChatQ] = useState<string>('Summarize the key equations and cite page numbers.');
  const [pdfChatRes, setPdfChatRes] = useState<any>(null);
  const [lectureStatus, setLectureStatus] = useState<any>(null);
  const [lectureTranscript, setLectureTranscript] = useState<string>('[00:01:15] Today we cover KVL and RC transient time constants tau = R*C.');
  const [lectureNotes, setLectureNotes] = useState<string>('');
  const [pptxTitle, setPptxTitle] = useState<string>('Linear Algebra Review');
  const [pptxResult, setPptxResult] = useState<ArtifactRef | null>(null);

  // Progress: Analytics & Planner
  const [analytics, setAnalytics] = useState<any>(null);
  const [plans, setPlans] = useState<StudyPlan[]>([]);
  const [planTitle, setPlanTitle] = useState<string>('Midterm Preparation Plan');
  const [planDate, setPlanDate] = useState<string>(
    new Date(Date.now() + 7 * 86400 * 1000).toISOString().slice(0, 10)
  );
  const [planHours, setPlanHours] = useState<number>(2);

  const [busy, setBusy] = useState<boolean>(false);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    if (models.length && !models.some((m) => m.id === selectedModelId)) {
      setSelectedModelId(models[0].id);
    }
  }, [models]);

  useEffect(() => {
    refreshAll();
  }, []);

  const refreshAll = async () => {
    try {
      const [docs, assigns, dks, exs, nbs, an, pls, lec] = await Promise.all([
        api.getStudyDocuments(),
        api.getAssignments(),
        api.getDecks(),
        api.getExams(),
        api.getNotebooks(),
        api.getStudyAnalytics(),
        api.getStudyPlans(),
        api.getLectureStatus(),
      ]);
      setDocuments(docs);
      setAssignments(assigns);
      if (!activeAssignment && assigns.length) setActiveAssignment(assigns[0]);
      setDecks(dks);
      if (!activeDeck && dks.length) setActiveDeck(dks[0]);
      setExams(exs);
      if (!activeExam && exs.length) setActiveExam(exs[0]);
      setNotebooks(nbs);
      if (!activeNotebook && nbs.length) setActiveNotebook(nbs[0]);
      setAnalytics(an);
      setPlans(pls);
      setLectureStatus(lec);
    } catch (err) {
      console.error('Study Lab load error:', err);
    }
  };

  const handleUploadDoc = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    try {
      const res = await api.uploadStudyDocument(file, activeNotebook?.id);
      setNotice(`Uploaded ${res.filename} (${res.parsed?.questions?.length || 0} question(s) extracted).`);
      await refreshAll();
    } catch (err: any) {
      setNotice(err.message);
    } finally {
      setBusy(false);
      e.target.value = '';
    }
  };

  const handleCreateAndSolveAssignment = async () => {
    setBusy(true);
    setExportedUrl(null);
    try {
      const created = await api.createAssignment({
        title: assignTitle,
        course: activeNotebook?.course || 'General',
        notebook_id: activeNotebook?.id,
        mode: assignMode,
        questions: [{ id: 'q_1', question_text: assignQuestionText, source_ref: 'Manual Input', included: true }],
      });
      const solved = await api.solveAssignment(created.id, {
        model_id: selectedModelId,
        mode: assignMode,
        language: assignLang,
        difficulty: tutorLevel,
      });
      setActiveAssignment(solved);
      await refreshAll();
    } catch (err: any) {
      setNotice(err.message);
    } finally {
      setBusy(false);
    }
  };

  const handleVerifyHomework = async () => {
    setBusy(true);
    try {
      const res = await api.verifyHomework({
        question: verQuestion,
        student_solution: verStudent,
        expected_answer: verExpected,
        model_id: selectedModelId,
        language: assignLang,
      });
      setVerResult(res);
    } catch (err: any) {
      setNotice(err.message);
    } finally {
      setBusy(false);
    }
  };

  const handleTutorSend = async () => {
    setBusy(true);
    try {
      const res = await api.tutorRespond({
        prompt: tutorPrompt,
        model_id: selectedModelId,
        level: tutorLevel,
        language: assignLang,
        mode: tutorMode,
      });
      setTutorReply(res.response || '');
    } catch (err: any) {
      setNotice(err.message);
    } finally {
      setBusy(false);
    }
  };

  const handleLanguageTutorSend = async () => {
    setBusy(true);
    try {
      const res = await api.languageTutor({
        text: langText,
        target_language: 'English',
        learner_level: 'B1',
        task: 'grammar_and_correction',
        answer_language: assignLang,
        model_id: selectedModelId,
      });
      setLangReply(res.response || '');
    } catch (err: any) {
      setNotice(err.message);
    } finally {
      setBusy(false);
    }
  };

  const handleCreateDeck = async () => {
    const created = await api.createDeck({
      title: newDeckTitle,
      course: activeNotebook?.course || 'General',
      cards: [{ front: newCardFront, back: newCardBack, source_ref: 'Study Note' }],
    });
    setActiveDeck(created);
    setCardIdx(0);
    await refreshAll();
  };

  const handleReviewCard = async (rating: string) => {
    if (!activeDeck || !activeDeck.cards[cardIdx]) return;
    const updated = await api.reviewDeckCard(activeDeck.id, activeDeck.cards[cardIdx].id, rating);
    setActiveDeck(updated);
    setShowCardBack(false);
    setCardIdx((idx) => (idx + 1) % Math.max(1, updated.cards.length));
  };

  const handleCreateSampleExam = async () => {
    const created = await api.createExam({
      title: 'Quick STEM Checkpoint',
      mode: 'practice',
      time_limit_minutes: 15,
      questions: [
        {
          id: 'q1',
          question_text: 'What is the derivative of x^2?',
          question_type: 'math',
          correct_answer: '2*x',
          topic: 'Calculus',
          difficulty: 'easy',
          explanation: 'Power rule gives d/dx(x^2) = 2x.',
        },
        {
          id: 'q2',
          question_text: 'Binary search has O(log n) worst-case time complexity on sorted arrays.',
          question_type: 'true_false',
          options: ['True', 'False'],
          correct_answer: 'True',
          topic: 'Algorithms',
          difficulty: 'easy',
          explanation: 'Each step halves the search interval.',
        },
      ],
    });
    setActiveExam(created);
    setExamAnswers({});
    setExamAttemptResult(null);
    await refreshAll();
  };

  const handleSubmitExam = async () => {
    if (!activeExam) return;
    const res = await api.submitExam(activeExam.id, examAnswers, 90);
    setExamAttemptResult(res);
    await refreshAll();
  };

  const handleCreateNotebook = async () => {
    const nb = await api.createNotebook({
      title: newNbTitle,
      course: 'Engineering',
      notes_markdown: '# Course Notes\nAdd summaries, derivations, and source citations here.',
      formula_sheet: [{ name: "Ohm's Law", formula: 'V = I * R', units: 'V, A, Ohm', assumptions: 'Linear resistive element' }],
      mind_map: {
        nodes: [
          { id: 'c1', label: 'Circuits' },
          { id: 'c2', label: 'KVL / KCL' },
          { id: 'c3', label: 'RC Transient' },
        ],
        edges: [
          { from: 'c1', to: 'c2', label: 'laws' },
          { from: 'c1', to: 'c3', label: 'time domain' },
        ],
      },
      sources: documents.map((d) => d.id),
    });
    setActiveNotebook(nb);
    await refreshAll();
  };

  const handlePdfChat = async () => {
    if (!activeNotebook) return;
    setBusy(true);
    try {
      const res = await api.pdfChat(activeNotebook.id, {
        question: pdfChatQ,
        model_id: selectedModelId,
        document_ids: documents.map((d) => d.id),
      });
      setPdfChatRes(res);
    } finally {
      setBusy(false);
    }
  };

  const handleGeneratePptx = async () => {
    const art = await api.generatePresentation({
      title: pptxTitle,
      subtitle: 'Multiverse Study Lab Export',
      slides: [
        { title: 'Core Concepts', bullets: ['Definitions and governing assumptions', 'Key theorems and proofs'], speaker_notes: 'Introduce module overview.' },
        { title: 'Worked Example', bullets: ['Problem setup and constraints', 'Step-by-step derivation and verification'], speaker_notes: 'Walk through verified steps.' },
      ],
    });
    setPptxResult(art);
  };

  const handleCreatePlan = async () => {
    await api.createStudyPlan({
      title: planTitle,
      exam_date: planDate,
      daily_hours: planHours,
      courses: [
        { name: 'Mathematics', priority: 3, topics: ['Derivatives', 'Integrals', 'Series'] },
        { name: 'Algorithms', priority: 2, topics: ['Sorting', 'Graph Traversal'] },
      ],
      weak_topics: (analytics?.weaknesses || []).map((w: any) => w.topic),
    });
    await refreshAll();
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-space-950">
      {/* Study Lab Top Bar */}
      <div className="px-4 py-2.5 border-b border-slate-800 bg-space-900/70 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-1.5">
          {[
            { id: 'solve', label: 'Solve & Learn', icon: Sparkles },
            { id: 'practice', label: 'Practice', icon: GraduationCap },
            { id: 'materials', label: 'Materials', icon: BookOpen },
            { id: 'progress', label: 'Progress', icon: BarChart3 },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setSection(tab.id as any)}
                className={`inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl font-medium transition-colors ${
                  section === tab.id
                    ? 'bg-cyan-500 text-space-950 font-semibold'
                    : 'bg-space-850 text-slate-300 hover:bg-space-800 border border-slate-800'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-slate-400">Active Model:</span>
          <select
            value={selectedModelId}
            onChange={(e) => setSelectedModelId(e.target.value)}
            className="px-2.5 py-1 rounded-lg bg-space-950 border border-slate-700 text-slate-200 max-w-[220px]"
          >
            {models.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name} {m.is_local ? '(Local)' : ''}
              </option>
            ))}
          </select>
        </div>
      </div>

      {notice && (
        <div className="px-4 py-1.5 bg-cyan-950/40 border-b border-cyan-800/40 text-xs text-cyan-200 flex justify-between">
          <span>{notice}</span>
          <button onClick={() => setNotice(null)} className="text-slate-400 hover:text-white">×</button>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 custom-scrollbar">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* 1. SOLVE & LEARN */}
          {section === 'solve' && (
            <div className="space-y-5">
              {/* Document Upload Bar */}
              <div className="rounded-2xl bg-space-900 border border-slate-800 p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
                <div className="space-y-1">
                  <div className="font-semibold text-slate-200 flex items-center gap-2">
                    <FileUp className="w-4 h-4 text-cyan-400" />
                    Shared Document Intake (PDF, DOCX, PPTX, TXT, MD, PNG, JPG)
                  </div>
                  <p className="text-slate-400">
                    Uploaded files are treated as untrusted data. Local-only mode keeps inference off external endpoints.
                  </p>
                </div>
                <label className="px-4 py-2 rounded-xl bg-space-800 hover:bg-space-700 border border-slate-700 text-slate-100 font-medium cursor-pointer">
                  <span>{busy ? 'Processing...' : 'Upload Document'}</span>
                  <input type="file" onChange={handleUploadDoc} className="hidden" />
                </label>
              </div>

              {documents.length > 0 && (
                <div className="flex flex-wrap gap-2 text-xs">
                  {documents.map((d) => (
                    <div key={d.id} className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-space-900 border border-slate-800">
                      <span className="text-slate-200">{d.filename}</span>
                      <span className="text-[10px] text-slate-500">({d.metadata?.page_count || 1}p)</span>
                      <button
                        onClick={async () => { await api.deleteStudyDocument(d.id); refreshAll(); }}
                        className="text-slate-500 hover:text-rose-400"
                        title="Delete document"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Sub-tabs */}
              <div className="flex flex-wrap gap-2 text-xs">
                {[
                  { id: 'assignment', label: 'Assignment Solver' },
                  { id: 'verifier', label: 'Homework Verifier' },
                  { id: 'tutor', label: 'Tutor, Professor & Language' },
                  { id: 'interactive', label: 'Interactive Tools (Algo / Math / Circuits / Code / LaTeX)' },
                ].map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setSolveTab(t.id as any)}
                    className={`px-3 py-1.5 rounded-xl border font-medium ${
                      solveTab === t.id
                        ? 'bg-space-800 border-cyan-500 text-cyan-300'
                        : 'bg-space-900 border-slate-800 text-slate-400'
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              {solveTab === 'assignment' && (
                <div className="rounded-2xl bg-space-900 border border-slate-800 p-5 space-y-4 text-xs">
                  {assignments.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 items-center">
                      <span className="text-slate-400">Saved:</span>
                      {assignments.map((a) => (
                        <button
                          key={a.id}
                          onClick={() => setActiveAssignment(a)}
                          className={`px-2.5 py-1 rounded-lg border ${
                            activeAssignment?.id === a.id ? 'bg-space-800 border-cyan-500 text-cyan-300' : 'bg-space-950 border-slate-800 text-slate-400'
                          }`}
                        >
                          {a.title}
                        </button>
                      ))}
                    </div>
                  )}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <input value={assignTitle} onChange={(e) => setAssignTitle(e.target.value)} className="px-3 py-2 rounded-xl bg-space-950 border border-slate-800 text-slate-100" placeholder="Assignment title" />
                    <select value={assignMode} onChange={(e) => setAssignMode(e.target.value)} className="px-3 py-2 rounded-xl bg-space-950 border border-slate-800 text-slate-200">
                      <option value="direct">Direct Answer</option>
                      <option value="step_by_step">Step-by-Step</option>
                      <option value="hint_only">Hint Only</option>
                      <option value="tutor">Tutor Explanation</option>
                      <option value="council">Council Solve</option>
                    </select>
                    <select value={assignLang} onChange={(e) => setAssignLang(e.target.value)} className="px-3 py-2 rounded-xl bg-space-950 border border-slate-800 text-slate-200">
                      <option value="en">English</option>
                      <option value="tr">Turkish</option>
                    </select>
                  </div>
                  <textarea
                    rows={3}
                    value={assignQuestionText}
                    onChange={(e) => setAssignQuestionText(e.target.value)}
                    className="w-full p-3 rounded-xl bg-space-950 border border-slate-800 text-sm text-slate-100"
                  />
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      {onOpenInCouncil && (
                        <button
                          onClick={() => onOpenInCouncil(assignQuestionText)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-950/60 border border-indigo-700 text-indigo-200"
                        >
                          <Users className="w-3.5 h-3.5" /> Open in Council
                        </button>
                      )}
                      {activeAssignment && ['pdf', 'docx', 'md'].map((fmt) => (
                        <button
                          key={fmt}
                          onClick={async () => {
                            const art = await api.exportAssignment(activeAssignment.id, fmt);
                            setExportedUrl(art.download_url);
                          }}
                          className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-space-800 text-slate-200 uppercase"
                        >
                          <Download className="w-3 h-3" /> {fmt}
                        </button>
                      ))}
                    </div>
                    <button
                      onClick={handleCreateAndSolveAssignment}
                      disabled={busy}
                      className="px-4 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-space-950 font-semibold"
                    >
                      {busy ? 'Solving...' : 'Solve Assignment'}
                    </button>
                  </div>
                  {exportedUrl && (
                    <a href={exportedUrl} target="_blank" rel="noreferrer" className="inline-block text-emerald-300 underline">
                      Download Exported Assignment Report
                    </a>
                  )}
                  {activeAssignment?.questions?.map((q) => (
                    <div key={q.id} className="p-4 rounded-xl bg-space-950 border border-slate-800 space-y-2">
                      <div className="font-semibold text-slate-200">{q.question_text}</div>
                      {q.solution && <MarkdownRenderer content={q.solution} />}
                    </div>
                  ))}
                </div>
              )}

              {solveTab === 'verifier' && (
                <div className="rounded-2xl bg-space-900 border border-slate-800 p-5 space-y-3 text-xs">
                  <div className="font-semibold text-slate-100">Homework Verifier (SymPy Equivalence + Step Critique)</div>
                  <input value={verQuestion} onChange={(e) => setVerQuestion(e.target.value)} placeholder="Question" className="w-full px-3 py-2 rounded-xl bg-space-950 border border-slate-800 text-slate-100" />
                  <textarea rows={3} value={verStudent} onChange={(e) => setVerStudent(e.target.value)} placeholder="Your solution steps" className="w-full p-3 rounded-xl bg-space-950 border border-slate-800 font-mono text-slate-100" />
                  <input value={verExpected} onChange={(e) => setVerExpected(e.target.value)} placeholder="Optional expected expression for SymPy check" className="w-full px-3 py-2 rounded-xl bg-space-950 border border-slate-800 font-mono text-slate-200" />
                  <button onClick={handleVerifyHomework} disabled={busy} className="px-4 py-2 rounded-xl bg-cyan-500 text-space-950 font-semibold">
                    Verify Solution
                  </button>
                  {verResult && (
                    <div className="p-4 rounded-xl bg-space-950 border border-slate-800 space-y-2">
                      <div className="flex items-center gap-2 font-mono text-emerald-300">
                        <CheckCircle2 className="w-4 h-4" /> Status: {verResult.verification_badge}
                      </div>
                      {verResult.deterministic_check && (
                        <div className="text-slate-300">
                          SymPy Equivalence: {String(verResult.deterministic_check.is_equivalent)} ({verResult.deterministic_check.explanation})
                        </div>
                      )}
                      {verResult.feedback && <MarkdownRenderer content={verResult.feedback} />}
                    </div>
                  )}
                </div>
              )}

              {solveTab === 'tutor' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 text-xs">
                  <div className="rounded-2xl bg-space-900 border border-slate-800 p-4 space-y-3">
                    <div className="font-semibold text-slate-100">Interactive Tutor & Professor Mode</div>
                    <div className="flex gap-2">
                      <select value={tutorLevel} onChange={(e) => setTutorLevel(e.target.value)} className="px-2.5 py-1.5 rounded-lg bg-space-950 border border-slate-700 text-slate-200">
                        <option value="beginner">Beginner</option>
                        <option value="intermediate">Intermediate</option>
                        <option value="advanced">Advanced</option>
                      </select>
                      <select value={tutorMode} onChange={(e) => setTutorMode(e.target.value)} className="px-2.5 py-1.5 rounded-lg bg-space-950 border border-slate-700 text-slate-200">
                        <option value="tutor">Guided Tutor</option>
                        <option value="clarify_step">Clarify Step</option>
                        <option value="professor_practice">Professor Practice Generator</option>
                      </select>
                    </div>
                    <textarea rows={3} value={tutorPrompt} onChange={(e) => setTutorPrompt(e.target.value)} className="w-full p-2.5 rounded-xl bg-space-950 border border-slate-800 text-slate-100" />
                    <button onClick={handleTutorSend} className="px-4 py-1.5 rounded-lg bg-cyan-500 text-space-950 font-semibold">Ask Tutor</button>
                    {tutorReply && <MarkdownRenderer content={tutorReply} />}
                  </div>

                  <div className="rounded-2xl bg-space-900 border border-slate-800 p-4 space-y-3">
                    <div className="font-semibold text-slate-100 flex items-center gap-1.5"><Languages className="w-4 h-4 text-cyan-400" /> Language Tutor</div>
                    <textarea rows={3} value={langText} onChange={(e) => setLangText(e.target.value)} className="w-full p-2.5 rounded-xl bg-space-950 border border-slate-800 text-slate-100" />
                    <button onClick={handleLanguageTutorSend} className="px-4 py-1.5 rounded-lg bg-space-800 border border-slate-700 text-cyan-300 font-semibold">Review Grammar & Alternatives</button>
                    {langReply && <MarkdownRenderer content={langReply} />}
                  </div>
                </div>
              )}

              {solveTab === 'interactive' && <InteractiveLearningPanel />}
            </div>
          )}

          {/* 2. PRACTICE */}
          {section === 'practice' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 text-xs">
              {/* Flashcards */}
              <div className="rounded-2xl bg-space-900 border border-slate-800 p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                    <Layers className="w-4 h-4 text-cyan-400" /> Spaced-Repetition Flashcards (SM-2)
                  </h3>
                  {activeDeck && (
                    <button
                      onClick={async () => {
                        const art = await api.exportDeck(activeDeck.id, 'csv');
                        window.open(art.download_url, '_blank');
                      }}
                      className="text-cyan-400 hover:underline flex items-center gap-1"
                    >
                      <Download className="w-3 h-3" /> Export CSV
                    </button>
                  )}
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <input value={newDeckTitle} onChange={(e) => setNewDeckTitle(e.target.value)} placeholder="Deck" className="px-2 py-1.5 rounded bg-space-950 border border-slate-800" />
                  <input value={newCardFront} onChange={(e) => setNewCardFront(e.target.value)} placeholder="Question" className="px-2 py-1.5 rounded bg-space-950 border border-slate-800" />
                  <input value={newCardBack} onChange={(e) => setNewCardBack(e.target.value)} placeholder="Answer" className="px-2 py-1.5 rounded bg-space-950 border border-slate-800" />
                </div>
                <button onClick={handleCreateDeck} className="px-3 py-1.5 rounded-lg bg-space-800 text-cyan-300 font-medium">
                  + Create Deck
                </button>
                {decks.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {decks.map((dk) => (
                      <button
                        key={dk.id}
                        onClick={() => { setActiveDeck(dk); setCardIdx(0); setShowCardBack(false); }}
                        className={`px-2.5 py-1 rounded-lg border ${
                          activeDeck?.id === dk.id ? 'bg-space-800 border-cyan-500 text-cyan-300' : 'bg-space-950 border-slate-800 text-slate-400'
                        }`}
                      >
                        {dk.title} ({dk.due_count})
                      </button>
                    ))}
                  </div>
                )}

                {activeDeck && activeDeck.cards.length > 0 && (
                  <div className="p-4 rounded-xl bg-space-950 border border-slate-800 space-y-3">
                    <div className="flex justify-between text-slate-400">
                      <span>{activeDeck.title}</span>
                      <span>Due: {activeDeck.due_count}/{activeDeck.total_cards}</span>
                    </div>
                    <div className="text-sm font-semibold text-slate-100 py-3">
                      {activeDeck.cards[cardIdx % activeDeck.cards.length].front}
                    </div>
                    {showCardBack ? (
                      <div className="space-y-3">
                        <div className="p-3 rounded-lg bg-space-900 text-emerald-300">
                          {activeDeck.cards[cardIdx % activeDeck.cards.length].back}
                        </div>
                        <div className="flex gap-2">
                          {['again', 'hard', 'good', 'easy'].map((r) => (
                            <button key={r} onClick={() => handleReviewCard(r)} className="flex-1 py-1.5 rounded bg-space-800 hover:bg-space-700 capitalize text-slate-200">
                              {r}
                            </button>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <button onClick={() => setShowCardBack(true)} className="w-full py-2 rounded-lg bg-cyan-500 text-space-950 font-semibold">
                        Reveal Answer
                      </button>
                    )}
                  </div>
                )}
              </div>

              {/* Exam Simulator */}
              <div className="rounded-2xl bg-space-900 border border-slate-800 p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-100">Exam Simulator (Deterministic Grading)</h3>
                  <button onClick={handleCreateSampleExam} className="px-3 py-1.5 rounded-lg bg-space-800 text-cyan-300">
                    + New Practice Exam
                  </button>
                </div>
                {exams.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {exams.map((ex) => (
                      <button
                        key={ex.id}
                        onClick={() => { setActiveExam(ex); setExamAnswers({}); setExamAttemptResult(null); }}
                        className={`px-2.5 py-1 rounded-lg border ${
                          activeExam?.id === ex.id ? 'bg-space-800 border-cyan-500 text-cyan-300' : 'bg-space-950 border-slate-800 text-slate-400'
                        }`}
                      >
                        {ex.title}
                      </button>
                    ))}
                  </div>
                )}

                {activeExam && (
                  <div className="space-y-3">
                    <div className="font-semibold text-slate-200">{activeExam.title} ({activeExam.mode})</div>
                    {activeExam.questions.map((q) => (
                      <div key={q.id} className="p-3 rounded-xl bg-space-950 border border-slate-800 space-y-2">
                        <div className="text-slate-100 font-medium">{q.question_text}</div>
                        {q.options?.length ? (
                          <div className="flex gap-2">
                            {q.options.map((opt) => (
                              <button
                                key={opt}
                                onClick={() => setExamAnswers((prev) => ({ ...prev, [q.id]: opt }))}
                                className={`px-3 py-1 rounded border ${
                                  examAnswers[q.id] === opt ? 'bg-cyan-500/20 border-cyan-500 text-cyan-200' : 'bg-space-900 border-slate-700'
                                }`}
                              >
                                {opt}
                              </button>
                            ))}
                          </div>
                        ) : (
                          <input
                            type="text"
                            value={examAnswers[q.id] || ''}
                            onChange={(e) => setExamAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
                            placeholder="Enter answer..."
                            className="w-full px-2.5 py-1.5 rounded bg-space-900 border border-slate-700 font-mono text-slate-100"
                          />
                        )}
                      </div>
                    ))}
                    <button onClick={handleSubmitExam} className="w-full py-2 rounded-xl bg-cyan-500 text-space-950 font-semibold">
                      Submit Exam
                    </button>
                    {examAttemptResult && (
                      <div className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-800/60 text-emerald-200">
                        Score: {examAttemptResult.objective_correct}/{examAttemptResult.objective_total} ({examAttemptResult.score_percent}%)
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 3. MATERIALS */}
          {section === 'materials' && (
            <div className="space-y-6 text-xs">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Notebooks & PDF Chat */}
                <div className="rounded-2xl bg-space-900 border border-slate-800 p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-sm text-slate-100">Course Notebooks & Source PDF Chat</span>
                    <div className="flex gap-1.5">
                      <input value={newNbTitle} onChange={(e) => setNewNbTitle(e.target.value)} className="px-2 py-1 rounded bg-space-950 border border-slate-800 w-36" />
                      <button onClick={handleCreateNotebook} className="px-2.5 py-1 rounded bg-space-800 text-cyan-300 inline-flex items-center gap-1">
                        <Plus className="w-3 h-3" /> Add
                      </button>
                    </div>
                  </div>
                  {notebooks.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {notebooks.map((nb) => (
                        <button
                          key={nb.id}
                          onClick={() => setActiveNotebook(nb)}
                          className={`px-2.5 py-1 rounded-lg border ${
                            activeNotebook?.id === nb.id ? 'bg-space-800 border-cyan-500 text-cyan-300' : 'bg-space-950 border-slate-800 text-slate-400'
                          }`}
                        >
                          {nb.title}
                        </button>
                      ))}
                    </div>
                  )}
                  {activeNotebook && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-slate-300">
                        <span className="font-semibold">{activeNotebook.title}</span>
                        <div className="flex gap-2">
                          <button
                            onClick={async () => {
                              const art = await api.exportNotebookFormulas(activeNotebook.id, 'pdf');
                              window.open(art.download_url, '_blank');
                            }}
                            className="text-cyan-400 hover:underline"
                          >
                            Export Formula PDF
                          </button>
                          {onSendToWorkflow && (
                            <button
                              onClick={() => onSendToWorkflow(activeNotebook.notes_markdown)}
                              className="text-indigo-300 hover:underline"
                            >
                              Use in Workflow
                            </button>
                          )}
                        </div>
                      </div>
                      <input
                        value={pdfChatQ}
                        onChange={(e) => setPdfChatQ(e.target.value)}
                        className="w-full px-3 py-2 rounded-xl bg-space-950 border border-slate-800 text-slate-100"
                      />
                      <button onClick={handlePdfChat} disabled={busy} className="px-4 py-1.5 rounded-lg bg-cyan-500 text-space-950 font-semibold">
                        Ask Uploaded Sources
                      </button>
                      {pdfChatRes && (
                        <div className="p-3 rounded-xl bg-space-950 border border-slate-800 space-y-2">
                          <div className="text-[11px] text-emerald-300">
                            Grounded: {String(pdfChatRes.source_grounded)} • Citations: {pdfChatRes.citations?.length || 0}
                          </div>
                          <MarkdownRenderer content={pdfChatRes.answer || ''} />
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Lecture Assistant & Presentation Maker */}
                <div className="rounded-2xl bg-space-900 border border-slate-800 p-4 space-y-4">
                  <div className="space-y-2">
                    <div className="font-semibold text-sm text-slate-100 flex items-center gap-2">
                      <Mic className="w-4 h-4 text-cyan-400" /> Lecture Assistant
                    </div>
                    <div className="text-[11px] text-slate-400">
                      Offline Whisper audio transcription: {lectureStatus?.offline_audio_ready ? 'Available' : 'Not installed (paste transcript below)'}
                    </div>
                    <textarea
                      rows={3}
                      value={lectureTranscript}
                      onChange={(e) => setLectureTranscript(e.target.value)}
                      className="w-full p-2.5 rounded-xl bg-space-950 border border-slate-800 text-slate-100"
                    />
                    <button
                      onClick={async () => {
                        const res = await api.processLecture({ transcript: lectureTranscript, title: 'Lecture 1', model_id: selectedModelId, language: assignLang });
                        setLectureNotes(res.notes || '');
                      }}
                      className="px-3 py-1.5 rounded-lg bg-space-800 text-cyan-300 font-semibold"
                    >
                      Generate Notes & Quiz
                    </button>
                    {lectureNotes && <MarkdownRenderer content={lectureNotes} />}
                  </div>

                  <div className="pt-3 border-t border-slate-800 space-y-2">
                    <div className="font-semibold text-sm text-slate-100 flex items-center gap-2">
                      <Presentation className="w-4 h-4 text-cyan-400" /> Presentation Maker (.pptx)
                    </div>
                    <div className="flex gap-2">
                      <input value={pptxTitle} onChange={(e) => setPptxTitle(e.target.value)} className="flex-1 px-2.5 py-1.5 rounded-lg bg-space-950 border border-slate-800 text-slate-100" />
                      <button onClick={handleGeneratePptx} className="px-3 py-1.5 rounded-lg bg-cyan-500 text-space-950 font-semibold">
                        Export PPTX
                      </button>
                    </div>
                    {pptxResult && (
                      <a href={pptxResult.download_url} download={pptxResult.filename} className="inline-flex items-center gap-1 text-emerald-300 underline">
                        <Download className="w-3.5 h-3.5" /> Download {pptxResult.filename}
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 4. PROGRESS */}
          {section === 'progress' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 text-xs">
              <div className="rounded-2xl bg-space-900 border border-slate-800 p-5 space-y-3">
                <h3 className="text-sm font-semibold text-slate-100">Exam Analytics & Weakness Detector</h3>
                {analytics?.has_sufficient_data ? (
                  <div className="space-y-3">
                    <div className="text-slate-300">
                      Recorded Attempts: {analytics.total_exam_attempts} • Flagged Practice Questions: {analytics.needs_practice_questions}
                    </div>
                    {analytics.topic_accuracy?.map((t: any) => (
                      <div key={t.topic} className="p-2.5 rounded-lg bg-space-950 border border-slate-800 flex justify-between">
                        <span>{t.topic} ({t.correct}/{t.total})</span>
                        <span className="font-mono text-cyan-300">{t.accuracy_percent}%</span>
                      </div>
                    ))}
                    {analytics.weaknesses?.map((w: any) => (
                      <div key={w.topic} className="p-2.5 rounded-lg bg-amber-950/30 border border-amber-800/50 text-amber-200">
                        Weakness Detected: <strong>{w.topic}</strong> ({w.accuracy_percent}%) — {w.recommendation}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-400">
                    No exam attempts recorded yet. Complete a practice exam to measure topic accuracy and weakness recommendations.
                  </p>
                )}
              </div>

              <div className="rounded-2xl bg-space-900 border border-slate-800 p-5 space-y-3">
                <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-cyan-400" /> Study Planner
                </h3>
                <div className="grid grid-cols-3 gap-2">
                  <input value={planTitle} onChange={(e) => setPlanTitle(e.target.value)} className="px-2 py-1.5 rounded bg-space-950 border border-slate-800" />
                  <input type="date" value={planDate} onChange={(e) => setPlanDate(e.target.value)} className="px-2 py-1.5 rounded bg-space-950 border border-slate-800" />
                  <input type="number" step="0.5" value={planHours} onChange={(e) => setPlanHours(Number(e.target.value))} className="px-2 py-1.5 rounded bg-space-950 border border-slate-800" />
                </div>
                <button onClick={handleCreatePlan} className="px-4 py-1.5 rounded-lg bg-cyan-500 text-space-950 font-semibold">
                  Generate Schedule
                </button>
                {plans.map((pl) => (
                  <div key={pl.id} className="p-3 rounded-xl bg-space-950 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200">{pl.title} (Exam: {pl.exam_date})</span>
                      <button
                        onClick={async () => {
                          const art = await api.exportStudyPlanIcs(pl.id);
                          window.open(art.download_url, '_blank');
                        }}
                        className="text-cyan-400 hover:underline"
                      >
                        Export .ICS
                      </button>
                    </div>
                    <div className="max-h-36 overflow-y-auto space-y-1">
                      {pl.sessions.slice(0, 7).map((s) => (
                        <div key={s.id} className="flex items-center justify-between text-[11px] bg-space-900 px-2 py-1 rounded">
                          <span>{s.date} — {s.course}: {s.topic} ({s.hours}h)</span>
                          <span className="font-mono text-slate-400">{s.status}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
