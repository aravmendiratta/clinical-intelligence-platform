// frontend/src/hooks/useChat.ts
import { useState, useCallback, useRef } from 'react';
import api, { API_BASE } from '../lib/api';

export interface ChatMessage {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  citations?: string | null;
  created_at?: string | null;
}

export interface Conversation {
  id: string;
  title: string;
  created_at?: string | null;
  updated_at?: string | null;
}

export function useChat() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const fetchConversations = useCallback(async () => {
    const res = await api.get('/chat/');
    setConversations(res.data);
  }, []);

  const createConversation = useCallback(async (title?: string): Promise<string> => {
    const res = await api.post('/chat/', { title: title || 'New Conversation' });
    const conv = res.data;
    setConversations((prev) => [conv, ...prev]);
    setActiveConversation(conv.id);
    setMessages([]);
    return conv.id;
  }, []);

  const loadMessages = useCallback(async (conversationId: string) => {
    setActiveConversation(conversationId);
    const res = await api.get(`/chat/${conversationId}/messages`);
    setMessages(res.data);
  }, []);

  const sendMessage = useCallback(async (content: string, conversationId?: string) => {
    let convId = conversationId || activeConversation;
    if (!convId) {
      convId = await createConversation();
    }

    // Add user message locally
    const userMsg: ChatMessage = { role: 'user', content };
    setMessages((prev) => [...prev, userMsg]);

    // Stream response via SSE
    setStreaming(true);
    const assistantMsg: ChatMessage = { role: 'assistant', content: '' };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      const token = localStorage.getItem('medintel_token');
      const controller = new AbortController();
      abortRef.current = controller;

      const response = await fetch(`${API_BASE}/chat/${convId}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ content }),
        signal: controller.signal,
      });

      if (!response.ok) throw new Error('Stream failed');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          // Parse SSE events
          const lines = chunk.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                if (data.citations) {
                  const citationsStr = typeof data.citations === 'string' ? data.citations : JSON.stringify(data.citations);
                  setMessages((prev) => {
                    const updated = [...prev];
                    if (updated.length > 0) {
                      updated[updated.length - 1] = {
                        ...updated[updated.length - 1],
                        citations: citationsStr,
                      };
                    }
                    return updated;
                  });
                } else if (data.token) {
                  fullContent += data.token;
                  setMessages((prev) => {
                    const updated = [...prev];
                    updated[updated.length - 1] = {
                      ...updated[updated.length - 1],
                      content: fullContent,
                    };
                    return updated;
                  });
                }
              } catch {
                // skip malformed events
              }
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('Chat stream error:', err);
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: 'An error occurred while generating the response. Please try again.',
          };
          return updated;
        });
      }
    } finally {
      setStreaming(false);
      abortRef.current = null;
    }
  }, [activeConversation, createConversation]);

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort();
    setStreaming(false);
  }, []);

  return {
    conversations,
    activeConversation,
    messages,
    streaming,
    fetchConversations,
    createConversation,
    loadMessages,
    sendMessage,
    stopStreaming,
    setActiveConversation,
  };
}
