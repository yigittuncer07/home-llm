import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { useState } from 'react';
import { Copy, Check, RefreshCw } from 'lucide-react';
import TypingIndicator from '../ui/TypingIndicator';
import type { Message, MessageRole } from '../../types';

interface MessageBubbleProps {
  role: MessageRole;
  content: string;
  isStreaming?: boolean;
  interrupted?: boolean;
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <button
      onClick={handleCopy}
      className="absolute top-2 right-2 p-1.5 rounded-md bg-gray-700/60 hover:bg-gray-600 text-gray-300 hover:text-white opacity-0 group-hover/code:opacity-100 transition-all"
      title="Copy code"
    >
      {copied ? <Check size={13} /> : <Copy size={13} />}
    </button>
  );
}

export default function MessageBubble({ role, content, isStreaming, interrupted }: MessageBubbleProps) {
  const isUser = role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end px-4 py-1 animate-in fade-in slide-in-from-bottom-2 duration-200">
        <div className="max-w-[75%] md:max-w-2xl bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap break-words">
          {content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start px-4 py-1 animate-in fade-in slide-in-from-bottom-2 duration-200">
      <div className="max-w-[85%] md:max-w-3xl min-w-0">
        {isStreaming && !content ? (
          <div className="bg-white dark:bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-3 border border-gray-100 dark:border-gray-700">
            <TypingIndicator />
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-3 border border-gray-100 dark:border-gray-700 text-gray-800 dark:text-gray-100 text-sm leading-relaxed">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
              components={{
                pre: ({ children, ...props }) => (
                  <div className="relative group/code my-3">
                    <pre
                      {...props}
                      className="overflow-x-auto rounded-lg text-xs leading-relaxed"
                    >
                      {children}
                    </pre>
                    {/* Extract text content for copy button */}
                    <CopyButton
                      text={
                        typeof (children as React.ReactElement)?.props?.children === 'string'
                          ? (children as React.ReactElement).props.children
                          : content
                      }
                    />
                  </div>
                ),
                code: ({ className, children, ...props }) => {
                  const isBlock = className?.includes('language-');
                  if (isBlock) {
                    return (
                      <code className={`${className ?? ''} text-xs`} {...props}>
                        {children}
                      </code>
                    );
                  }
                  return (
                    <code
                      className="bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded px-1 py-0.5 text-xs font-mono"
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },
                a: ({ children, href, ...props }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 dark:text-blue-400 hover:underline"
                    {...props}
                  >
                    {children}
                  </a>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc list-outside ml-4 space-y-1 my-2">{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-outside ml-4 space-y-1 my-2">{children}</ol>
                ),
                p: ({ children }) => <p className="my-1.5 last:mb-0">{children}</p>,
                h1: ({ children }) => (
                  <h1 className="text-lg font-bold mt-4 mb-2">{children}</h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-base font-semibold mt-3 mb-1.5">{children}</h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-sm font-semibold mt-2 mb-1">{children}</h3>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-4 italic text-gray-500 dark:text-gray-400 my-2">
                    {children}
                  </blockquote>
                ),
                table: ({ children }) => (
                  <div className="overflow-x-auto my-3">
                    <table className="min-w-full border-collapse text-xs">{children}</table>
                  </div>
                ),
                th: ({ children }) => (
                  <th className="border border-gray-300 dark:border-gray-600 px-3 py-1.5 bg-gray-50 dark:bg-gray-700 font-semibold text-left">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="border border-gray-300 dark:border-gray-600 px-3 py-1.5">
                    {children}
                  </td>
                ),
              }}
            >
              {content}
            </ReactMarkdown>

            {/* Blinking cursor while streaming */}
            {isStreaming && (
              <span className="inline-block w-0.5 h-4 bg-gray-500 animate-pulse ml-0.5 align-middle" />
            )}

            {/* Interrupted state indicator */}
            {interrupted && (
              <p className="mt-2 text-xs text-amber-600 dark:text-amber-400 italic">
                ⚠ Response interrupted
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// Re-export typed version for the message list
export function MessageBubbleFromMessage({
  message,
  onRetry,
}: {
  message: Message;
  onRetry?: () => void;
}) {
  return (
    <div>
      <MessageBubble role={message.role} content={message.content} />
      {onRetry && message.role === 'user' && (
        <div className="flex justify-end px-4 mt-1">
          <button
            onClick={onRetry}
            className="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
          >
            <RefreshCw size={11} />
            Retry
          </button>
        </div>
      )}
    </div>
  );
}
