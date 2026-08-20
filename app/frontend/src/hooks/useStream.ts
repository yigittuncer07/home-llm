import { useCallback, useRef } from 'react';
import { toast } from 'sonner';
import { openStream } from '../api/stream';
import { useChatStore } from '../store/chatStore';
import { useAuthStore } from '../store/authStore';

export function useStream(chatId: number) {
  const abortRef = useRef<AbortController | null>(null);
  const { token } = useAuthStore();
  const { startStreaming, appendStreamToken, finalizeStream, interruptStream } = useChatStore();

  const startStream = useCallback(async () => {
    if (!token) return;

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    startStreaming();

    const runStream = async (isRetry = false): Promise<void> => {
      try {
        for await (const event of openStream(chatId, token, controller.signal)) {
          if (event.is_finished) {
            finalizeStream(chatId);
            return;
          }
          if (event.token !== undefined) {
            appendStreamToken(event.token);
          }
        }
        // Stream closed without is_finished — treat as complete
        finalizeStream(chatId);
      } catch (err) {
        if ((err as Error).name === 'AbortError') return;
        if (!isRetry) {
          await runStream(true);
        } else {
          interruptStream();
          toast.error('Connection interrupted. The response may be incomplete.');
        }
      }
    };

    await runStream();
  }, [chatId, token, startStreaming, appendStreamToken, finalizeStream, interruptStream]);

  const stopStream = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
  }, []);

  return { startStream, stopStream };
}
