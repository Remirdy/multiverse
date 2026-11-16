export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
  description: string;
  category: string;
  context_length: number;
  is_available: boolean;
  is_default: boolean;
  tags: string[];
}

export interface ModelListResponse {
  models: ModelInfo[];
  default_models: string[];
  total: number;
}

export interface ModelResult {
  model_id: string;
  model_name: string;
  provider: string;
  response_text: string | null;
  response_time_ms: number | null;
  status: 'success' | 'error' | 'timeout' | 'loading';
  error_message: string | null;
}

export interface CompareRequest {
  prompt: string;
  model_ids: string[];
  conversation_id?: string;
  system_prompt?: string;
  timeout?: number;
}

export interface CompareResponse {
  conversation_id: string;
  turn_id: string;
  prompt: string;
  results: ModelResult[];
  total_models: number;
  successful_models: number;
  failed_models: number;
}

export interface RetryModelRequest {
  conversation_id: string;
  turn_id: string;
  model_id: string;
  prompt: string;
  system_prompt?: string;
  timeout?: number;
}

export interface TurnDetail {
  id: string;
  prompt: string;
  system_prompt?: string | null;
  created_at: string;
  responses: ModelResult[];
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
