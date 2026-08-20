import { BASE_URL } from './client';
import type { StreamEvent } from '../types';

/**
 * Parses one SSE `data:` payload into a StreamEvent.
 *
 * All stream parsing is isolated here — swap this function if the backend
 * event shape changes.
 *
 * Backend format: {"token": "...", "is_finished": false}
 * Terminal event: {"is_finished": true}
 * Fallback:       treat raw text as a plain token.
 */
export function parseStreamEvent(data: string): StreamEvent {
  try {
    const parsed = JSON.parse(data) as Record<string, unknown>;
    return {
      token: typeof parsed.token === 'string' ? parsed.token : undefined,
      is_finished: parsed.is_finished === true,
    };
  } catch {
    return { token: data };
  }
}

/**
 * Fetch-based SSE reader — avoids the native EventSource limitation of not
 * being able to send custom headers. The Authorization token is sent as a
 * normal request header, keeping it out of the URL.
 *
 * Yields parsed StreamEvents until `is_finished` is received, the signal is
 * aborted, or the connection closes.
 */
export async function* openStream(
  chatId: number,
  token: string,
  signal: AbortSignal,
): AsyncGenerator<StreamEvent> {
  const response = await fetch(`${BASE_URL}/chats/${chatId}/stream`, {
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: 'text/event-stream',
      'Cache-Control': 'no-cache',
    },
    signal,
  });

  if (!response.ok) {
    throw new Error(`Stream connection failed: ${response.status} ${response.statusText}`);
  }

  if (!response.body) {
    throw new Error('Response body is null');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // SSE events are separated by blank lines (\n\n).
      const parts = buffer.split('\n\n');
      buffer = parts.pop() ?? '';

      for (const part of parts) {
        for (const line of part.split('\n')) {
          if (line.startsWith('data: ')) {
            const payload = line.slice(6).trim();
            if (payload) {
              yield parseStreamEvent(payload);
            }
          }
          // Ignore `event:` and `id:` lines — backend only uses `data:` lines.
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}
