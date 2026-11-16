import {
  ModelListResponse,
  CompareRequest,
  CompareResponse,
  RetryModelRequest,
  ModelResult,
  ConversationSummary,
  ConversationDetail,
  RouteResponse,
  ProviderHealth,
  AttachmentItem,
  ProviderConfigItem,
  ExecutionPolicy,
  ArtifactRef,
  CouncilRole,
  CouncilPreset,
  CouncilSession,
  CouncilMember,
  WorkflowNodeCatalogItem,
  WorkflowDefinition,
  WorkflowRun,
  StudyNotebook,
  StudyAssignment,
  FlashcardDeck,
  StudyExam,
  StudyPlan,
} from '../types';

const BASE_URL = '/api';

class ApiClient {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${BASE_URL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const res = await fetch(url, { ...options, headers });

    if (!res.ok) {
      let errorMsg = `HTTP Error ${res.status}`;
      try {
        const errJson = await res.json();
        errorMsg = errJson.detail || errJson.message || errorMsg;
      } catch {
        // fallback message
      }
      throw new Error(errorMsg);
    }

    if (res.status === 204) {
      return null as unknown as T;
    }

    return res.json();
  }

  // Upload
  async uploadFile(file: File): Promise<AttachmentItem> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${BASE_URL}/upload`, { method: 'POST', body: formData });
    if (!res.ok) {
      let err = 'File upload failed';
      try {
        const j = await res.json();
        err = j.detail || err;
      } catch {}
      throw new Error(err);
    }
    return res.json();
  }

  // Models, Providers & Policy
  async getModels(): Promise<ModelListResponse> {
    return this.request<ModelListResponse>('/models');
  }

  async getHealth(): Promise<ProviderHealth> {
    return this.request<ProviderHealth>('/models/health');
  }

  async getProviders(): Promise<ProviderConfigItem[]> {
    return this.request<ProviderConfigItem[]>('/models/providers');
  }

  async configureProvider(payload: {
    provider_id: string;
    name?: string;
    base_url: string;
    api_key?: string;
    is_local?: boolean;
    is_enabled?: boolean;
  }): Promise<ProviderConfigItem> {
    return this.request<ProviderConfigItem>('/models/providers/configure', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async testProvider(payload: { provider_id: string; base_url?: string; api_key?: string }): Promise<{
    provider_id: string;
    status: string;
    discovered_models: string[];
    error?: string | null;
  }> {
    return this.request('/models/providers/test', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getExecutionPolicy(): Promise<ExecutionPolicy> {
    return this.request<ExecutionPolicy>('/models/policy');
  }

  async updateExecutionPolicy(payload: Partial<ExecutionPolicy>): Promise<ExecutionPolicy> {
    return this.request<ExecutionPolicy>('/models/policy', {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  }

  // Jobs & Artifacts
  async getJob(jobId: string): Promise<any> {
    return this.request(`/jobs/${jobId}`);
  }

  async cancelJob(jobId: string): Promise<any> {
    return this.request(`/jobs/${jobId}/cancel`, { method: 'POST' });
  }

  async getArtifacts(originType?: string): Promise<ArtifactRef[]> {
    const qs = originType ? `?origin_type=${encodeURIComponent(originType)}` : '';
    return this.request<ArtifactRef[]>(`/artifacts${qs}`);
  }

  // Comparison
  async compare(data: CompareRequest): Promise<CompareResponse> {
    return this.request<CompareResponse>('/compare', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async retry(data: RetryModelRequest): Promise<ModelResult> {
    return this.request<ModelResult>('/compare/retry', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async synthesize(data: {
    prompt: string;
    responses: Array<{ model_id: string; model_name: string; response_text: string }>;
    language?: string;
  }): Promise<{ arbiter_model: string; synthesis_text: string; latency_ms: number }> {
    return this.request('/compare/synthesize', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Conversations
  async getConversations(): Promise<ConversationSummary[]> {
    return this.request<ConversationSummary[]>('/conversations');
  }

  async getConversation(id: string): Promise<ConversationDetail> {
    return this.request<ConversationDetail>(`/conversations/${id}`);
  }

  async createConversation(title?: string): Promise<ConversationSummary> {
    return this.request<ConversationSummary>('/conversations', {
      method: 'POST',
      body: JSON.stringify({ title }),
    });
  }

  async deleteConversation(id: string): Promise<void> {
    await this.request<void>(`/conversations/${id}`, { method: 'DELETE' });
  }

  // Routing & Prompt Enhancement
  async routePrompt(prompt: string): Promise<RouteResponse> {
    return this.request<RouteResponse>('/route', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  }

  async enhancePrompt(prompt: string, language: string = 'tr'): Promise<{
    original_prompt: string;
    enhanced_prompt: string;
    latency_ms: number;
    model_used: string;
  }> {
    return this.request('/route/enhance', {
      method: 'POST',
      body: JSON.stringify({ prompt, language }),
    });
  }

  // Council
  async getCouncilRoles(): Promise<CouncilRole[]> {
    return this.request<CouncilRole[]>('/council/roles');
  }

  async getCouncilPresets(): Promise<CouncilPreset[]> {
    return this.request<CouncilPreset[]>('/council/presets');
  }

  async estimateCouncil(payload: { members: CouncilMember[]; review_rounds: number; enable_review: boolean }): Promise<any> {
    return this.request('/council/estimate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getCouncilSessions(): Promise<CouncilSession[]> {
    return this.request<CouncilSession[]>('/council/sessions');
  }

  async createCouncilSession(payload: {
    title?: string;
    prompt: string;
    preset_id?: string;
    members: CouncilMember[];
    chair_model_id: string;
    review_rounds: number;
    enable_review: boolean;
    enable_verification: boolean;
    instructions?: string;
    pause_after_proposals?: boolean;
  }): Promise<CouncilSession> {
    return this.request<CouncilSession>('/council/sessions', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async resumeCouncilSession(sessionId: string): Promise<CouncilSession> {
    return this.request<CouncilSession>(`/council/sessions/${sessionId}/resume`, { method: 'POST' });
  }

  async retryCouncilMember(sessionId: string, memberIndex: number): Promise<CouncilSession> {
    return this.request<CouncilSession>(`/council/sessions/${sessionId}/retry-member`, {
      method: 'POST',
      body: JSON.stringify({ member_index: memberIndex }),
    });
  }

  async forkCouncilSession(sessionId: string): Promise<CouncilSession> {
    return this.request<CouncilSession>(`/council/sessions/${sessionId}/fork`, { method: 'POST' });
  }

  async deleteCouncilSession(sessionId: string): Promise<void> {
    await this.request(`/council/sessions/${sessionId}`, { method: 'DELETE' });
  }

  async exportCouncilSession(sessionId: string, format: string, includeFull: boolean = true): Promise<ArtifactRef> {
    return this.request<ArtifactRef>(`/council/sessions/${sessionId}/export`, {
      method: 'POST',
      body: JSON.stringify({ format, include_full: includeFull }),
    });
  }

  // Workflows
  async getWorkflowNodeCatalog(): Promise<WorkflowNodeCatalogItem[]> {
    return this.request<WorkflowNodeCatalogItem[]>('/workflows/node-catalog');
  }

  async getWorkflowTemplates(): Promise<WorkflowDefinition[]> {
    return this.request<WorkflowDefinition[]>('/workflows/templates');
  }

  async getWorkflows(): Promise<WorkflowDefinition[]> {
    return this.request<WorkflowDefinition[]>('/workflows');
  }

  async createWorkflow(payload: { name: string; description: string; graph: WorkflowDefinition['graph'] }): Promise<WorkflowDefinition> {
    return this.request<WorkflowDefinition>('/workflows', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async updateWorkflow(id: string, payload: { name: string; description: string; graph: WorkflowDefinition['graph'] }): Promise<WorkflowDefinition> {
    return this.request<WorkflowDefinition>(`/workflows/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  }

  async cloneWorkflow(id: string): Promise<WorkflowDefinition> {
    return this.request<WorkflowDefinition>(`/workflows/${id}/clone`, { method: 'POST' });
  }

  async deleteWorkflow(id: string): Promise<void> {
    await this.request(`/workflows/${id}`, { method: 'DELETE' });
  }

  async validateWorkflowGraph(graph: WorkflowDefinition['graph']): Promise<{
    valid: boolean;
    errors: string[];
    warnings: string[];
    estimated_calls: number;
  }> {
    return this.request('/workflows/validate', {
      method: 'POST',
      body: JSON.stringify({ graph }),
    });
  }

  async importWorkflow(payload: Record<string, any>, save: boolean = true): Promise<any> {
    return this.request(`/workflows/import?save=${save}`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async exportWorkflowJson(id: string): Promise<any> {
    return this.request(`/workflows/${id}/export`);
  }

  async runWorkflow(id: string, inputs: Record<string, any>): Promise<WorkflowRun> {
    return this.request<WorkflowRun>(`/workflows/${id}/runs`, {
      method: 'POST',
      body: JSON.stringify({ inputs }),
    });
  }

  async getWorkflowRuns(id: string): Promise<WorkflowRun[]> {
    return this.request<WorkflowRun[]>(`/workflows/${id}/runs`);
  }

  async approveWorkflowRun(runId: string, nodeId: string, approved: boolean): Promise<WorkflowRun> {
    return this.request<WorkflowRun>(`/workflows/runs/${runId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ node_id: nodeId, approved }),
    });
  }

  async retryWorkflowNode(runId: string, nodeId: string): Promise<WorkflowRun> {
    return this.request<WorkflowRun>(`/workflows/runs/${runId}/retry-node`, {
      method: 'POST',
      body: JSON.stringify({ node_id: nodeId }),
    });
  }

  // Study Lab
  async uploadStudyDocument(file: File, notebookId?: string): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    if (notebookId) formData.append('notebook_id', notebookId);
    const res = await fetch(`${BASE_URL}/study/documents/upload`, { method: 'POST', body: formData });
    if (!res.ok) {
      let err = 'Study document upload failed';
      try {
        const j = await res.json();
        err = j.detail || err;
      } catch {}
      throw new Error(err);
    }
    return res.json();
  }

  async getStudyDocuments(): Promise<ArtifactRef[]> {
    return this.request<ArtifactRef[]>('/study/documents');
  }

  async deleteStudyDocument(id: string): Promise<void> {
    await this.request(`/study/documents/${id}`, { method: 'DELETE' });
  }

  async getAssignments(): Promise<StudyAssignment[]> {
    return this.request<StudyAssignment[]>('/study/assignments');
  }

  async createAssignment(payload: {
    title: string;
    course: string;
    notebook_id?: string;
    artifact_id?: string;
    mode: string;
    questions: any[];
  }): Promise<StudyAssignment> {
    return this.request<StudyAssignment>('/study/assignments', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async solveAssignment(id: string, payload: {
    model_id: string;
    mode: string;
    language: string;
    difficulty: string;
  }): Promise<StudyAssignment> {
    return this.request<StudyAssignment>(`/study/assignments/${id}/solve`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async exportAssignment(id: string, fmt: string): Promise<ArtifactRef> {
    return this.request<ArtifactRef>(`/study/assignments/${id}/export?fmt=${encodeURIComponent(fmt)}`, { method: 'POST' });
  }

  async verifyHomework(payload: {
    question: string;
    student_solution: string;
    expected_answer?: string;
    rubric?: string;
    model_id: string;
    language: string;
  }): Promise<any> {
    return this.request('/study/assignments/verify-homework', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async tutorRespond(payload: {
    prompt: string;
    model_id: string;
    level: string;
    language: string;
    mode: string;
    context_text?: string;
  }): Promise<any> {
    return this.request('/study/tutor/respond', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async languageTutor(payload: {
    text: string;
    target_language: string;
    learner_level: string;
    task: string;
    answer_language: string;
    model_id: string;
  }): Promise<any> {
    return this.request('/study/language-tutor', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async runMathTool(payload: Record<string, any>): Promise<any> {
    return this.request('/study/tools/math', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async runAlgorithmTool(payload: Record<string, any>): Promise<any> {
    return this.request('/study/tools/algorithms', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async runElectronicsTool(payload: { topology: string; params: Record<string, any> }): Promise<any> {
    return this.request('/study/tools/electronics', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async runCodeLab(payload: { code: string; stdin_data?: string; test_cases?: any[] }): Promise<any> {
    return this.request('/study/tools/code-lab', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getNotebooks(q?: string): Promise<StudyNotebook[]> {
    const qs = q ? `?q=${encodeURIComponent(q)}` : '';
    return this.request<StudyNotebook[]>(`/study/notebooks${qs}`);
  }

  async createNotebook(payload: Partial<StudyNotebook> & { title: string }): Promise<StudyNotebook> {
    return this.request<StudyNotebook>('/study/notebooks', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async updateNotebook(id: string, payload: Partial<StudyNotebook> & { title: string }): Promise<StudyNotebook> {
    return this.request<StudyNotebook>(`/study/notebooks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  }

  async deleteNotebook(id: string): Promise<void> {
    await this.request(`/study/notebooks/${id}`, { method: 'DELETE' });
  }

  async pdfChat(notebookId: string, payload: { question: string; model_id: string; document_ids?: string[] }): Promise<any> {
    return this.request(`/study/notebooks/${notebookId}/pdf-chat`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async researchCompare(notebookId: string, payload: { question: string; model_id: string; document_ids?: string[] }): Promise<any> {
    return this.request(`/study/notebooks/${notebookId}/research-compare`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async exportNotebookFormulas(notebookId: string, fmt: string): Promise<ArtifactRef> {
    return this.request<ArtifactRef>(`/study/notebooks/${notebookId}/formula-export?fmt=${encodeURIComponent(fmt)}`, {
      method: 'POST',
    });
  }

  async getDecks(): Promise<FlashcardDeck[]> {
    return this.request<FlashcardDeck[]>('/study/decks');
  }

  async createDeck(payload: { title: string; course: string; cards: any[]; notebook_id?: string }): Promise<FlashcardDeck> {
    return this.request<FlashcardDeck>('/study/decks', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async reviewDeckCard(deckId: string, cardId: string, rating: string): Promise<FlashcardDeck> {
    return this.request<FlashcardDeck>(`/study/decks/${deckId}/review`, {
      method: 'POST',
      body: JSON.stringify({ card_id: cardId, rating }),
    });
  }

  async exportDeck(deckId: string, fmt: string): Promise<ArtifactRef> {
    return this.request<ArtifactRef>(`/study/decks/${deckId}/export?fmt=${encodeURIComponent(fmt)}`);
  }

  async getQuestionBank(): Promise<any[]> {
    return this.request<any[]>('/study/question-bank');
  }

  async addQuestionBankItem(payload: Record<string, any>): Promise<any> {
    return this.request('/study/question-bank', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getExams(): Promise<StudyExam[]> {
    return this.request<StudyExam[]>('/study/exams');
  }

  async createExam(payload: { title: string; mode: string; time_limit_minutes?: number; questions: any[] }): Promise<StudyExam> {
    return this.request<StudyExam>('/study/exams', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async submitExam(examId: string, answers: Record<string, string>, elapsedSeconds: number): Promise<any> {
    return this.request(`/study/exams/${examId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers, elapsed_seconds: elapsedSeconds }),
    });
  }

  async getStudyAnalytics(): Promise<any> {
    return this.request('/study/analytics');
  }

  async getStudyPlans(): Promise<StudyPlan[]> {
    return this.request<StudyPlan[]>('/study/planner');
  }

  async createStudyPlan(payload: { title: string; exam_date: string; daily_hours: number; courses: any[]; weak_topics?: string[] }): Promise<StudyPlan> {
    return this.request<StudyPlan>('/study/planner', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async updateStudyPlan(planId: string, sessions: StudyPlan['sessions']): Promise<StudyPlan> {
    return this.request<StudyPlan>(`/study/planner/${planId}`, {
      method: 'PUT',
      body: JSON.stringify({ sessions }),
    });
  }

  async exportStudyPlanIcs(planId: string): Promise<ArtifactRef> {
    return this.request<ArtifactRef>(`/study/planner/${planId}/export-ics`, { method: 'POST' });
  }

  async getLectureStatus(): Promise<any> {
    return this.request('/study/lecture/status');
  }

  async processLecture(payload: { transcript: string; title: string; model_id: string; language: string }): Promise<any> {
    return this.request('/study/lecture/process', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async generatePresentation(payload: { title: string; subtitle: string; slides: any[] }): Promise<ArtifactRef> {
    return this.request<ArtifactRef>('/study/presentations/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }
}

export const api = new ApiClient();
