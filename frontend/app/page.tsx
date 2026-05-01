"use client";

import { useState, useRef, useEffect } from "react";
import styles from "./page.module.css";

type Message = {
  id: string;
  role: "user" | "ai";
  content: string;
  sources?: string[];
  suggested_questions?: string[];
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userQuery = input.trim();
    setInput("");
    setError(null);
    
    // Add user message to UI immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: userQuery,
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          query: userQuery,
          history: messages.map(m => ({ role: m.role, content: m.content }))
        }),
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }

      const aiMessageId = (Date.now() + 1).toString();
      let aiMessage: Message = {
        id: aiMessageId,
        role: "ai",
        content: "",
      };

      setMessages((prev) => [...prev, aiMessage]);

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (!line.trim()) continue;
            try {
              const data = JSON.parse(line);
              if (data.type === "chunk") {
                aiMessage.content += data.content;
              } else if (data.type === "sources") {
                aiMessage.sources = data.content;
              } else if (data.type === "suggested_questions") {
                aiMessage.suggested_questions = data.content;
              }
              setMessages((prev) => 
                prev.map(m => m.id === aiMessageId ? { ...aiMessage } : m)
              );
            } catch (e) {
              console.error("Error parsing NDJSON line:", line, e);
            }
          }
        }
      }
    } catch (err: unknown) {
      console.error("API Error:", err);
      const errorMessage = err instanceof Error ? err.message : "Failed to connect to the API. Is the backend running?";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSubmit();
    }
  };

  const setCardQuery = (query: string) => {
    setInput(query);
  };

  return (
    <main className={styles.container}>
      {/* Top Navigation Bar */}
      <nav className={styles.topNav}>
        <div className={styles.navGroup}>
          <button className={styles.pillBtn} onClick={() => setMessages([])}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            New Chat
          </button>
        </div>
        <div className={styles.logoWrapper}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
            <path d="M2 17l10 5 10-5"></path>
            <path d="M2 12l10 5 10-5"></path>
          </svg>
          <span className={styles.logoText}>PG-RAG</span>
        </div>
      </nav>

      <div className={styles.chatBox}>
        <div className={styles.messages}>
          {messages.length === 0 ? (
            <div className={styles.welcomeContainer}>
              <h1 className={styles.welcomeTitle}>Good Morning, Founder</h1>
              <p className={styles.welcomeSubtitle}>Hey there! What can I tell you about Paul Graham&apos;s essays today?</p>

              <div className={styles.cardsGrid}>
                <div className={styles.card} onClick={() => setCardQuery("How to get startup ideas?")}>
                  <div className={styles.cardIcon}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>
                  </div>
                  <h3 className={styles.cardTitle}>Startup Ideas</h3>
                  <p className={styles.cardDesc}>Get a quick overview of how to find organic, meaningful startup ideas.</p>
                  <button className={styles.cardAction}>View Essay</button>
                </div>
                
                <div className={styles.card} onClick={() => setCardQuery("How to create wealth?")}>
                  <div className={styles.cardIcon}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                  </div>
                  <h3 className={styles.cardTitle}>Wealth Creation</h3>
                  <p className={styles.cardDesc}>Identify the core mechanics of creating wealth and optimizing your leverage.</p>
                  <button className={styles.cardAction}>Analyze Wealth</button>
                </div>

                <div className={styles.card} onClick={() => setCardQuery("Why Lisp is powerful?")}>
                  <div className={styles.cardIcon}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                  </div>
                  <h3 className={styles.cardTitle}>Programming Languages</h3>
                  <p className={styles.cardDesc}>See the top-performing languages based on leverage, speed, and abstraction.</p>
                  <button className={styles.cardAction}>View Insights</button>
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`${styles.messageWrapper} ${styles[msg.role]}`}
                >
                  <div
                    className={`${styles.message} ${
                      msg.role === "user" ? styles.userMessage : styles.aiMessage
                    }`}
                  >
                    <div className={styles.content}>{msg.content}</div>
                    
                    {msg.sources && msg.sources.length > 0 && (
                      <div className={styles.sources}>
                        <div className={styles.sourceTitle}>Sources</div>
                        <div className={styles.sourcePills}>
                          {msg.sources.map((source, idx) => (
                            <div key={idx} className={styles.sourcePill}>
                              {source}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {msg.suggested_questions && msg.suggested_questions.length > 0 && (
                      <div className={styles.suggestedQuestions}>
                        <div className={styles.suggestedTitle}>Suggested Follow-ups</div>
                        <div className={styles.suggestedPills}>
                          {msg.suggested_questions.map((question, idx) => (
                            <button 
                              key={idx} 
                              className={styles.suggestedPill}
                              onClick={() => {
                                setInput(question);
                                // setTimeout(() => handleSubmit(), 0); // optional auto-submit
                              }}
                            >
                              {question}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className={`${styles.messageWrapper} ${styles.ai}`}>
                  <div className={`${styles.message} ${styles.aiMessage}`}>
                    <div className={styles.loadingIndicator}>
                      <div className={styles.dot}></div>
                      <div className={styles.dot}></div>
                      <div className={styles.dot}></div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
          
          {messages.length > 0 && <div ref={messagesEndRef} style={{ height: "100px", flexShrink: 0 }} />}
        </div>

        <div className={styles.inputContainer}>
          <form className={styles.form} onSubmit={handleSubmit}>
            {error && <div className={styles.error}>{error}</div>}
            
            <input
              className={styles.input}
              placeholder="Write a message here..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
            />
            
            <button
              type="submit"
              className={`${styles.inputActionBtn} ${styles.submit}`}
              disabled={!input.trim() || isLoading}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="19" x2="12" y2="5"></line><polyline points="5 12 12 5 19 12"></polyline></svg>
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
