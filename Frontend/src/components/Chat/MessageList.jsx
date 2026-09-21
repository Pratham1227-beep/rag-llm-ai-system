import React, { useEffect, useRef } from 'react';
import { MessageCircle, Bot, User, Copy, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const MarkdownRenderer = ({ content }) => {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => (
          <h1 className="text-lg font-bold text-gray-900 mt-3 mb-2 border-b border-gray-200 pb-1">{children}</h1>
        ),
        h2: ({ children }) => (
          <h2 className="text-base font-bold text-gray-900 mt-3 mb-1.5">{children}</h2>
        ),
        h3: ({ children }) => (
          <h3 className="text-sm font-semibold text-gray-800 mt-2 mb-1">{children}</h3>
        ),
        p: ({ children }) => (
          <p className="mb-2 leading-relaxed text-gray-800 last:mb-0">{children}</p>
        ),
        strong: ({ children }) => (
          <strong className="font-semibold text-gray-900">{children}</strong>
        ),
        ul: ({ children }) => (
          <ul className="list-disc pl-5 space-y-1 mb-2 text-gray-800">{children}</ul>
        ),
        ol: ({ children }) => (
          <ol className="list-decimal pl-5 space-y-1 mb-2 text-gray-800">{children}</ol>
        ),
        li: ({ children }) => (
          <li className="leading-relaxed">{children}</li>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-emerald-500 pl-3 italic my-2 text-gray-600 bg-emerald-50/50 py-1.5 rounded-r">
            {children}
          </blockquote>
        ),
        table: ({ children }) => (
          <div className="overflow-x-auto my-3 border border-gray-200 rounded-lg shadow-sm">
            <table className="min-w-full divide-y divide-gray-200 text-xs md:text-sm text-left">
              {children}
            </table>
          </div>
        ),
        thead: ({ children }) => (
          <thead className="bg-emerald-50 text-gray-700 font-semibold uppercase tracking-wider text-[11px]">
            {children}
          </thead>
        ),
        tbody: ({ children }) => (
          <tbody className="divide-y divide-gray-100 bg-white">
            {children}
          </tbody>
        ),
        tr: ({ children }) => (
          <tr className="hover:bg-gray-50 transition-colors">
            {children}
          </tr>
        ),
        th: ({ children }) => (
          <th className="px-3.5 py-2.5 font-semibold text-emerald-900 border-b border-emerald-100">
            {children}
          </th>
        ),
        td: ({ children }) => (
          <td className="px-3.5 py-2.5 text-gray-700 border-b border-gray-100">
            {children}
          </td>
        ),
        code: ({ inline, className, children, ...props }) => {
          if (inline) {
            return (
              <code className="bg-gray-100 text-emerald-700 font-mono text-xs px-1.5 py-0.5 rounded border border-gray-200">
                {children}
              </code>
            );
          }
          return (
            <div className="my-2 bg-gray-900 text-gray-100 rounded-lg p-3 overflow-x-auto font-mono text-xs shadow-inner">
              <pre {...props}><code>{children}</code></pre>
            </div>
          );
        },
        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-emerald-600 hover:text-emerald-700 underline font-medium"
          >
            {children}
          </a>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
};

const MessageList = ({ messages, isTyping }) => {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center p-6 max-w-md">
          <div className="w-16 h-16 bg-emerald-50 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-emerald-100 shadow-sm">
            <MessageCircle size={32} className="text-emerald-600" />
          </div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">Welcome to Enterprise RAG AI</h2>
          <p className="text-gray-500 text-sm leading-relaxed">
            Upload documents, reports, or research materials to get instant summaries, contextual Q&A, and detailed analysis.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="flex-1 overflow-y-auto p-4 md:p-6 space-y-5 bg-gray-50/70"
      style={{
        backgroundImage: 'radial-gradient(#e5e7eb 1px, transparent 1px)',
        backgroundSize: '20px 20px',
      }}
    >
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          {msg.sender !== 'user' && (
            <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center flex-shrink-0 shadow-sm mt-0.5">
              <Bot size={18} />
            </div>
          )}

          <div
            className={`max-w-[90%] md:max-w-[78%] px-4 py-3.5 rounded-2xl shadow-sm text-sm leading-relaxed ${
              msg.sender === 'user'
                ? 'bg-emerald-600 text-white rounded-tr-none'
                : 'bg-white text-gray-800 rounded-tl-none border border-gray-200/80 shadow-sm'
            }`}
          >
            {msg.sender === 'user' ? (
              <p className="whitespace-pre-wrap">{msg.text}</p>
            ) : (
              <div className="prose prose-sm max-w-none">
                <MarkdownRenderer content={msg.text} />
              </div>
            )}

            <div
              className={`text-[10px] mt-2 flex items-center justify-end ${
                msg.sender === 'user' ? 'text-emerald-100' : 'text-gray-400'
              }`}
            >
              <span>
                {new Date(msg.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </div>
          </div>

          {msg.sender === 'user' && (
            <div className="w-8 h-8 rounded-full bg-gray-700 text-white flex items-center justify-center flex-shrink-0 shadow-sm mt-0.5">
              <User size={16} />
            </div>
          )}
        </div>
      ))}

      {isTyping && (
        <div className="flex gap-3 justify-start items-center">
          <div className="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center flex-shrink-0 shadow-sm">
            <Bot size={18} />
          </div>
          <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-none shadow-sm border border-gray-200/80">
            <div className="flex items-center space-x-1.5">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce [animation-delay:0.15s]"></div>
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-bounce [animation-delay:0.3s]"></div>
            </div>
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;