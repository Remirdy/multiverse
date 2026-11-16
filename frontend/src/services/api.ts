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
  AttachmentItem
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
        // use fallback
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

    const res = await fetch(`${BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      let err = 'Dosya yükleme başarısız oldu';
      try {
        const j = await res.json();
        err = j.detail || err;
      } catch {}
      throw new Error(err);
    }

    return res.json();
  }

  // Models
  async getModels(): Promise<ModelListResponse> {
    return this.request<ModelListResponse>('/models');
  }

  async getHealth(): Promise<ProviderHealth> {
    return this.request<ProviderHealth>('/models/health');
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
    await this.request<void>(`/conversations/${id}`, {
      method: 'DELETE',
    });
  }

  // Routing
  async routePrompt(prompt: string): Promise<RouteResponse> {
    return this.request<RouteResponse>('/route', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });
  }
}

export const api = new ApiClient();
