import {
  useState,
  useRef,
  useEffect,
  type KeyboardEvent,
} from 'react';
import { SendHorizontal, Square } from 'lucide-react';
import type { ModelBalance } from '../../types';

interface MessageInputProps {
  onSend: (prompt: string, model: string) => Promise<void>;
  onStop: () => void;
  isStreaming: boolean;
  disabled?: boolean;
  initialValue?: string;
  onInitialValueConsumed?: () => void;
  models: ModelBalance[];
  selectedModel: string;
  onModelChange: (model: string) => void;
  tokenBalance: number | null;
}

export default function MessageInput({
  onSend,
  onStop,
  isStreaming,
  disabled,
  initialValue,
  onInitialValueConsumed,
  models,
  selectedModel,
  onModelChange,
  tokenBalance,
}: MessageInputProps) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Prefill from suggestion chip
  useEffect(() => {
    if (initialValue) {
      setValue(initialValue);
      onInitialValueConsumed?.();
      textareaRef.current?.focus();
    }
  }, [initialValue, onInitialValueConsumed]);

  // Auto-grow textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }, [value]);

  async function handleSend() {
    const trimmed = value.trim();
    if (!trimmed || isStreaming || disabled) return;
    setValue('');
    await onSend(trimmed, selectedModel);
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  const canSend = value.trim().length > 0 && !isStreaming && !disabled && selectedModel !== '';

  return (
    <div className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 px-4 py-3">
      <div className="max-w-3xl mx-auto">
        {/* Model selector — small and unobtrusive */}
        <div className="flex items-center gap-2 mb-2">
          <label
            htmlFor="model-select"
            className="text-xs text-gray-400 dark:text-gray-500 shrink-0"
          >
            Model
          </label>
          <select
            id="model-select"
            value={selectedModel}
            onChange={(e) => onModelChange(e.target.value)}
            disabled={models.length === 0}
            className="text-xs bg-white dark:bg-gray-900 text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700 focus:outline-none focus:border-blue-500 py-0.5 disabled:opacity-50"
          >
            {models.length === 0 && <option value="">Loading…</option>}
            {models.map((m) => (
              <option key={m.model_name} value={m.model_name}>{m.model_name}</option>
            ))}
          </select>
          {tokenBalance !== null && (
            <span className="text-xs text-gray-400 dark:text-gray-500">
              {Math.max(0, tokenBalance).toLocaleString()} tokens
            </span>
          )}
        </div>

        {/* Input row */}
        <div className="flex items-end gap-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl px-4 py-3 focus-within:border-blue-400 dark:focus-within:border-blue-600 transition-colors">
          <textarea
            ref={textareaRef}
            rows={1}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder="Message…"
            className="flex-1 bg-transparent text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 resize-none focus:outline-none leading-relaxed disabled:opacity-50 max-h-[200px] overflow-y-auto"
          />

          {isStreaming ? (
            // TODO: wire up a backend cancellation endpoint when the API supports it.
            // Currently this only aborts the client-side SSE fetch connection.
            <button
              onClick={onStop}
              title="Stop generating"
              className="shrink-0 w-8 h-8 flex items-center justify-center rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              <Square size={14} className="text-gray-700 dark:text-gray-300" fill="currentColor" />
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!canSend}
              title="Send message"
              className="shrink-0 w-8 h-8 flex items-center justify-center rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <SendHorizontal size={15} className="text-white" />
            </button>
          )}
        </div>

        <p className="text-center text-xs text-gray-400 dark:text-gray-600 mt-2">
          Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
