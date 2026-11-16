import React, { useState, useRef, useEffect } from 'react';
import { Send, Layers, Sparkles, SlidersHorizontal } from 'lucide-react';
import { ModelInfo } from '../types';

interface ChatInputProps {
  onSendMessage: (prompt: string, systemPrompt?: string) => void;
  isLoading: boolean;
  selectedModels: ModelInfo[];
  onOpenModelSelector: () => void;
  onPromptChange?: (prompt: string) => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
  selectedModels,
  onOpenModelSelector,
  onPromptChange,
}) => {
  const [prompt, setPrompt] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [showSystemPrompt, setShowSystemPrompt] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [prompt]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setPrompt(val);
    if (onPromptChange) {
      onPromptChange(val);
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    onSendMessage(prompt.trim(), systemPrompt.trim() ? systemPrompt.trim() : undefined);
    setPrompt('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full max-w-5xl mx-auto px-4 pb-4">
      {/* Optional System Prompt Bar */}
      {showSystemPrompt && (
        <div className="mb-2 p-2.5 rounded-xl bg-space-900 border border-slate-800 shadow-md">
          <div className="flex items-center justify-between mb-1.5 px-1">
            <span className="text-[11px] font-medium text-slate-400">
              System Instructions (Optional)
            </span>
            <button
              type="button"
              onClick={() => setShowSystemPrompt(false)}
              className="text-[10px] text-slate-500 hover:text-slate-300"
            >
              Hide
            </button>
          </div>
          <input
            type="text"
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            placeholder="e.g. You are a senior engineer. Provide concise code examples and benchmarks."
            className="w-full bg-space-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60"
          />
        </div>
      )}

      {/* Main Prompt Input Box */}
      <form
        onSubmit={handleSubmit}
        className="relative flex flex-col rounded-2xl bg-space-900 border border-slate-800 shadow-2xl focus-within:border-cyan-500/60 transition-all duration-200"
      >
        {/* Model Chips Bar */}
        <div className="flex items-center justify-between gap-2 px-3.5 py-2 border-b border-slate-800/60 bg-space-850/40 text-xs">
          <div className="flex items-center gap-1.5 overflow-x-auto custom-scrollbar py-0.5">
            <span className="text-slate-500 text-[11px] font-medium shrink-0">Models ({selectedModels.length}):</span>
            {selectedModels.map((m) => (
              <span
                key={m.id}
                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-space-800 text-slate-300 border border-slate-700/60 text-[11px] font-medium shrink-0"
              >
                <Sparkles className="w-2.5 h-2.5 text-cyan-400" />
                <span>{m.name}</span>
              </span>
            ))}
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            <button
              type="button"
              onClick={() => setShowSystemPrompt(!showSystemPrompt)}
              className="flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-200 px-2 py-1 rounded hover:bg-space-800 transition-colors"
              title="Toggle system prompt instructions"
            >
              <SlidersHorizontal className="w-3 h-3" />
              <span className="hidden sm:inline">System</span>
            </button>

            <button
              type="button"
              onClick={onOpenModelSelector}
              className="flex items-center gap-1 text-[11px] font-medium text-cyan-400 hover:text-cyan-300 px-2.5 py-1 rounded-lg bg-cyan-950/60 border border-cyan-800/60 hover:bg-cyan-900/40 transition-colors"
            >
              <Layers className="w-3 h-3" />
              <span>Change</span>
            </button>
          </div>
        </div>

        {/* Text Input Area */}
        <div className="flex items-end gap-2 p-3">
          <textarea
            ref={textareaRef}
            value={prompt}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask one question to all selected models concurrently..."
            rows={1}
            disabled={isLoading}
            className="flex-1 bg-transparent text-sm text-slate-100 placeholder-slate-500 resize-none focus:outline-none min-h-[44px] max-h-[180px] py-2 px-1 leading-relaxed custom-scrollbar"
          />

          <button
            type="submit"
            disabled={!prompt.trim() || isLoading}
            className={`flex items-center justify-center w-10 h-10 rounded-xl transition-all shrink-0 ${
              !prompt.trim() || isLoading
                ? 'bg-space-800 text-slate-600 cursor-not-allowed border border-slate-700/40'
                : 'bg-cyan-500 hover:bg-cyan-400 text-space-950 shadow-md shadow-cyan-950/40 active:scale-95'
            }`}
            title="Send to all models (Enter)"
          >
            <Send className="w-4 h-4 stroke-[2.5]" />
          </button>
        </div>

        {/* Footnote */}
        <div className="flex items-center justify-between px-3.5 pb-2 text-[10px] text-slate-500">
          <span>Press Enter to send, Shift+Enter for new line</span>
          <span>NVIDIA Build NIM Multi-Model Engine</span>
        </div>
      </form>
    </div>
  );
};
