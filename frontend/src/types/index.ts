export type AppWorkspace = 'compare' | 'council' | 'workflows' | 'study';

export interface ModelCapabilities {
  chat: boolean;
  vision: boolean;
  structured_output: boolean;
  tool_calling: boolean;
  streaming: boolean;
  context_length: number;
  modalities: string[];
}

export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  provider_id?: string;
  is_local?: boolean;
  is_free_tier?: boolean;
  description: string;
  category: string;
  context_length: number;
  is_available: boolean;
  is_default: boolean;
  tags: string[];
  capabilities?: ModelCapabilities;
}

export interface ModelListResponse {
  models: ModelInfo[];
  default_models: string[];
  total: number;
}

export interface ProviderConfigItem {
  provider_id: string;
  name: string;
  base_url: string;
  is_local: boolean;
  is_enabled: boolean;
  status: string;
  discovered_models: string[];
  error?: string | null;
}

export interface ExecutionPolicy {
  local_only: boolean;
  free_only: boolean;
  max_calls_per_run: number;
  max_parallel: number;
}

export interface ArtifactRef {
  id: string;
  filename: string;
  media_type: string;
  size_bytes: number;
  content_hash: string;
  origin_type: string;
  origin_id?: string | null;
  metadata?: Record<string, any>;
  download_url: string;
  created_at?: string;
}

export interface AttachmentItem {
  filename: string;
  content_type: string;
  file_type: 'image' | 'document';
  size: number;
  data_url?: string;
  extracted_text?: string;
  preview?: string;
  page_count?: number;
  page_images?: string[];
}

export interface ModelResult {
  model_id: string;
  model_name: string;
  provider: string;
  response_text: string | null;
  response_time_ms: number | null;
  status: 'success' | 'error' | 'timeout' | 'loading' | 'canceled';
  error_message: string | null;
}

export interface WebSearchResultItem {
  title: string;
  link: string;
  snippet: string;
}

export interface CompareRequest {
  prompt: string;
  model_ids: string[];
  conversation_id?: string;
  system_prompt?: string;
  timeout?: number;
  attachments?: AttachmentItem[];
  web_search?: boolean;
}

export interface CompareResponse {
  conversation_id: string;
  turn_id: string;
  prompt: string;
  results: ModelResult[];
  total_models: number;
  successful_models: number;
  failed_models: number;
  attachments?: AttachmentItem[];
  web_search_results?: WebSearchResultItem[];
}

export interface RetryModelRequest {
  conversation_id: string;
  turn_id: string;
  model_id: string;
  prompt: string;
  system_prompt?: string;
  timeout?: number;
  attachments?: AttachmentItem[];
}

export interface TurnDetail {
  id: string;
  prompt: string;
  system_prompt?: string | null;
  created_at: string;
  responses: ModelResult[];
  attachments?: AttachmentItem[];
  web_search_results?: WebSearchResultItem[];
}

export interface ConversationSummary {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  turns_count: number;
}

export interface ConversationDetail {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  turns: TurnDetail[];
}

export interface RouteResponse {
  category: string;
  category_label: string;
  confidence: number;
  reasoning: string;
  recommended_model_ids: string[];
}

export interface ProviderHealth {
  status: string;
  provider: string;
  base_url: string;
  api_key_set: boolean;
}

export interface EnhancePromptResponse {
  original_prompt: string;
  enhanced_prompt: string;
  latency_ms: number;
  model_used: string;
}

export interface SynthesizeResponse {
  arbiter_model: string;
  synthesis_text: string;
  latency_ms: number;
}

// --- Council ---
export interface CouncilRole {
  id: string;
  name: string;
  instructions: string;
  allowed_tools: string[];
}

export interface CouncilMember {
  role_id: string;
  model_id: string;
  instructions?: string;
}

export interface CouncilPreset {
  id: string;
  name: string;
  description: string;
  config: {
    members: CouncilMember[];
    chair_model_id: string;
    review_rounds: number;
    enable_verification?: boolean;
  };
  is_builtin: boolean;
}

export interface CouncilSession {
  id: string;
  title: string;
  prompt: string;
  status: string;
  preset_id?: string | null;
  config: Record<string, any>;
  proposals: Array<{
    member_index: number;
    label: string;
    role_id: string;
    role_name: string;
    model_id: string;
    model_name: string;
    provider: string;
    status: string;
    response_text?: string | null;
    response_time_ms?: number | null;
    error_message?: string | null;
  }>;
  reviews: Array<Record<string, any>>;
  revisions: Array<Record<string, any>>;
  verifications: Array<{ tool: string; status: string; summary: string; details?: any }>;
  disagreements: Array<{ source: string; point: string }>;
  synthesis?: {
    chair_model_id: string;
    status: string;
    final_answer: string;
    response_time_ms?: number;
    error_message?: string | null;
  } | null;
  usage: { calls?: number; tokens?: number };
  job_id?: string | null;
  created_at?: string;
}

// --- Workflows ---
export interface WorkflowNodeCatalogItem {
  type: string;
  label: string;
  category: string;
  description: string;
  inputs: string[];
  outputs: string[];
  available: boolean;
  unavailable_reason?: string;
  default_config: Record<string, any>;
}

export interface WorkflowGraphNode {
  id: string;
  type: string;
  label?: string;
  position: { x: number; y: number };
  config: Record<string, any>;
}

export interface WorkflowGraphEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
}

export interface WorkflowDefinition {
  id: string;
  name: string;
  description: string;
  version: number;
  graph: {
    nodes: WorkflowGraphNode[];
    edges: WorkflowGraphEdge[];
  };
  is_template: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface WorkflowRun {
  id: string;
  workflow_id: string;
  workflow_version: number;
  status: string;
  inputs: Record<string, any>;
  node_states: Record<string, { status: string; logs: string[]; started_at?: string; finished_at?: string }>;
  outputs: Record<string, any>;
  usage: { calls?: number; tokens?: number };
  job_id?: string | null;
  created_at?: string;
}

// --- Study Lab ---
export interface StudyNotebook {
  id: string;
  title: string;
  course: string;
  description: string;
  tags: string[];
  notes_markdown: string;
  formula_sheet: Array<{ name: string; formula: string; assumptions?: string; units?: string; example?: string }>;
  mind_map: { nodes?: Array<{ id: string; label: string }>; edges?: Array<{ from: string; to: string; label?: string }>; mermaid?: string };
  sources: string[];
  saved_items: Array<{ title: string; content: string; origin?: string }>;
  created_at?: string;
}

export interface StudyAssignment {
  id: string;
  notebook_id?: string | null;
  title: string;
  course: string;
  mode: string;
  artifact_id?: string | null;
  questions: Array<{
    id: string;
    question_text: string;
    page?: number;
    source_ref?: string;
    status: string;
    included?: boolean;
    solution?: string;
    council_session_id?: string;
  }>;
}

export interface FlashcardDeck {
  id: string;
  notebook_id?: string | null;
  title: string;
  course: string;
  total_cards: number;
  due_count: number;
  cards: Array<{
    id: string;
    front: string;
    back: string;
    source_ref?: string;
    repetitions: number;
    interval_days: number;
    ease_factor: number;
    due_at?: string | null;
  }>;
}

export interface StudyExam {
  id: string;
  notebook_id?: string | null;
  title: string;
  mode: string;
  time_limit_minutes?: number | null;
  questions: Array<{
    id: string;
    question_text: string;
    question_type: 'mcq' | 'true_false' | 'short_answer' | 'math' | 'open_ended';
    options?: string[];
    correct_answer?: string;
    explanation?: string;
    topic?: string;
    difficulty?: string;
  }>;
  attempts: Array<Record<string, any>>;
}

export interface StudyPlan {
  id: string;
  title: string;
  exam_date: string;
  daily_hours: number;
  courses: Array<{ name: string; priority: number; topics: string[] }>;
  sessions: Array<{
    id: string;
    date: string;
    course: string;
    topic: string;
    hours: number;
    priority_weakness?: boolean;
    status: 'planned' | 'done' | 'missed';
  }>;
}
