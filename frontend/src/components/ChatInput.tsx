import React, { useState, useRef, useEffect } from 'react';
import { Send, Layers, Sparkles, SlidersHorizontal, Paperclip, FileText, Image as ImageIcon, X, Loader2 } from 'lucide-react';
import { ModelInfo, AttachmentItem } from '../types';
import { api } from '../services/api';
import { useLanguage } from '../i18n/LanguageContext';

interface ChatInputProps {
  onSendMessage: (prompt: string, systemPrompt?: string, attachments?: AttachmentItem[]) => void;
  isLoading: boolean;
  selectedModels: ModelInfo[];
  onOpenModelSelector: () => void;
  onPromptChange?: (prompt: string) => void;
  onAddVisionModel?: () => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
  selectedModels,
  onOpenModelSelector,
  onPromptChange,
  onAddVisionModel,
}) => {
  const { t } = useLanguage();
  const [prompt, setPrompt] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [showSystemPrompt, setShowSystemPrompt] = useState(false);
  const [attachments, setAttachments] = useState<AttachmentItem[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  const handleUploadFiles = async (files: FileList | File[]) => {
    if (!files || files.length === 0) return;
    setIsUploading(true);

    try {
      const uploadPromises = Array.from(files).map((f) => api.uploadFile(f));
      const uploadedItems = await Promise.all(uploadPromises);
      setAttachments((prev) => [...prev, ...uploadedItems]);
    } catch (err: any) {
      alert(`Dosya yüklenirken hata oluştu: ${err.message}`);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleUploadFiles(e.target.files);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleUploadFiles(e.dataTransfer.files);
    }
  };

  const handleRemoveAttachment = (indexToRemove: number) => {
    setAttachments((prev) => prev.filter((_, idx) => idx !== indexToRemove));
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if ((!prompt.trim() && attachments.length === 0) || isLoading || isUploading) return;
    
    // Fallback prompt if user only uploads document/image without text
    const finalPrompt = prompt.trim() || (
      attachments.some((a) => a.file_type === 'image' || (a.page_images && a.page_images.length > 0))
        ? (t.langLabel === 'TR' ? 'Analyze this circuit schematic and calculate output voltage Vo and currents.' : 'Bu devre şemasını ve görseli analiz et, Vo gerilimini ve akımları hesapla.')
        : (t.langLabel === 'TR' ? 'Analyze and summarize the attached document.' : 'Bu ekli belgeyi incele, özetle ve önemli noktalarını çıkar.')
    );

    onSendMessage(
      finalPrompt,
      systemPrompt.trim() ? systemPrompt.trim() : undefined,
      attachments.length > 0 ? attachments : undefined
    );

    setPrompt('');
    setAttachments([]);
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
      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="image/*,application/pdf,text/*,.py,.js,.ts,.tsx,.jsx,.json,.csv,.md,.txt,.html,.css,.sql,.sh,.yml,.yaml"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Optional System Prompt Bar */}
      {showSystemPrompt && (
        <div className="mb-2 p-2.5 rounded-xl bg-space-900 border border-slate-800 shadow-md">
          <div className="flex items-center justify-between mb-1.5 px-1">
            <span className="text-[11px] font-medium text-slate-400">
              {t.systemToggle}
            </span>
            <button
              type="button"
              onClick={() => setShowSystemPrompt(false)}
              className="text-[10px] text-slate-500 hover:text-slate-300"
            >
              ✕
            </button>
          </div>
          <input
            type="text"
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            placeholder={t.systemPlaceholder}
            className="w-full bg-space-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60"
          />
        </div>
      )}

      {/* Main Prompt Input Box with Drag & Drop */}
      <form
        onSubmit={handleSubmit}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`relative flex flex-col rounded-2xl bg-space-900 border transition-all duration-200 shadow-2xl ${
          isDragging
            ? 'border-cyan-400 bg-space-850 ring-2 ring-cyan-500/30'
            : 'border-slate-800 focus-within:border-cyan-500/60'
        }`}
      >
        {/* Model Chips Bar */}
        <div className="flex items-center justify-between gap-2 px-3.5 py-2 border-b border-slate-800/60 bg-space-850/40 text-xs">
          <div className="flex items-center gap-1.5 overflow-x-auto custom-scrollbar py-0.5">
            <span className="text-slate-500 text-[11px] font-medium shrink-0">{t.modelsLabel} ({selectedModels.length}):</span>
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
              title={t.systemToggle}
            >
              <SlidersHorizontal className="w-3 h-3" />
              <span className="hidden sm:inline">{t.systemBtn}</span>
            </button>

            <button
              type="button"
              onClick={onOpenModelSelector}
              className="flex items-center gap-1 text-[11px] font-medium text-cyan-400 hover:text-cyan-300 px-2.5 py-1 rounded-lg bg-cyan-950/60 border border-cyan-800/60 hover:bg-cyan-900/40 transition-colors"
            >
              <Layers className="w-3 h-3" />
              <span>{t.changeModels}</span>
            </button>
          </div>
        </div>

        {/* Vision Model Recommendation Banner for Schematics/Diagrams */}
        {attachments.length > 0 && !selectedModels.some((m) => m.id.includes('vl') || m.id.includes('vision')) && (
          <div className="flex items-center justify-between gap-2 px-3.5 py-1.5 bg-cyan-950/40 border-b border-cyan-800/40 text-[11px] text-cyan-200">
            <div className="flex items-center gap-1.5 truncate">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span className="truncate">{t.visionRecommend}</span>
            </div>
            {onAddVisionModel && (
              <button
                type="button"
                onClick={onAddVisionModel}
                className="px-2 py-0.5 rounded bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-400/40 text-cyan-300 font-medium text-[10px] shrink-0 transition-colors"
              >
                {t.addVisionModel}
              </button>
            )}
          </div>
        )}

        {/* Uploaded Attachments Preview Bar */}
        {(attachments.length > 0 || isUploading) && (
          <div className="flex flex-wrap items-center gap-2 p-2.5 px-3.5 border-b border-slate-800/60 bg-space-950/50">
            {attachments.map((att, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-space-800 border border-slate-700/80 text-xs text-slate-200 group animate-fadeIn"
              >
                {att.file_type === 'image' || (att.page_images && att.page_images.length > 0) ? (
                  <div className="w-6 h-6 rounded overflow-hidden bg-space-900 border border-slate-700 shrink-0 flex items-center justify-center">
                    {att.data_url ? (
                      <img src={att.data_url} alt={att.filename} className="w-full h-full object-cover" />
                    ) : (
                      <ImageIcon className="w-3.5 h-3.5 text-emerald-400" />
                    )}
                  </div>
                ) : (
                  <FileText className="w-4 h-4 text-cyan-400 shrink-0" />
                )}
                <div className="flex flex-col max-w-[160px] truncate">
                  <span className="truncate font-medium text-[11px] text-slate-200" title={att.filename}>
                    {att.filename}
                  </span>
                  <span className="text-[9px] text-slate-400">
                    {roundSize(att.size)} {att.page_count ? `• ${att.page_count} sayfa` : ''}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => handleRemoveAttachment(idx)}
                  className="text-slate-400 hover:text-rose-400 p-0.5 rounded transition-colors"
                  title="Kaldır"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}

            {isUploading && (
              <div className="flex items-center gap-1.5 text-xs text-cyan-400 px-2 py-1 rounded bg-cyan-950/40 border border-cyan-800/50 animate-pulse">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>{t.uploadingHint}</span>
              </div>
            )}
          </div>
        )}

        {/* Text Input Area & Action Buttons */}
        <div className="flex items-end gap-2 p-3">
          {/* File Upload Trigger Button */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading || isUploading}
            className="flex items-center justify-center w-10 h-10 rounded-xl bg-space-850 hover:bg-space-800 text-slate-300 hover:text-cyan-400 border border-slate-700/60 hover:border-cyan-500/50 transition-all shrink-0 active:scale-95 disabled:opacity-50"
            title="Belge veya devre fotoğrafı yükle (PDF, Resim, Kod, Metin)"
          >
            <Paperclip className="w-4 h-4" />
          </button>

          <textarea
            ref={textareaRef}
            value={prompt}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={
              attachments.length > 0
                ? t.inputPlaceholderDocs
                : t.inputPlaceholder
            }
            rows={1}
            disabled={isLoading}
            className="flex-1 bg-transparent text-sm text-slate-100 placeholder-slate-500 resize-none focus:outline-none min-h-[44px] max-h-[180px] py-2 px-1 leading-relaxed custom-scrollbar"
          />

          <button
            type="submit"
            disabled={(!prompt.trim() && attachments.length === 0) || isLoading || isUploading}
            className={`flex items-center justify-center w-10 h-10 rounded-xl transition-all shrink-0 ${
              (!prompt.trim() && attachments.length === 0) || isLoading || isUploading
                ? 'bg-space-800 text-slate-600 cursor-not-allowed border border-slate-700/40'
                : 'bg-cyan-500 hover:bg-cyan-400 text-space-950 shadow-md shadow-cyan-950/40 active:scale-95'
            }`}
            title={t.sendBtn}
          >
            <Send className="w-4 h-4 stroke-[2.5]" />
          </button>
        </div>

        {/* Footnote */}
        <div className="flex items-center justify-between px-3.5 pb-2 text-[10px] text-slate-500">
          <span>{t.dropHint}</span>
          <span>{t.footerInfo}</span>
        </div>
      </form>
    </div>
  );
};

function roundSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
