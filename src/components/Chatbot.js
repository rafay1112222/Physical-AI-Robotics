import React, { useState, useRef, useEffect } from 'react';
import { useColorMode } from '@docusaurus/theme-common';
import styles from './Chatbot.module.css';

// --- THE FIX: HARD-CODED BACKEND URL ---
const BACKEND_URL = "https://abd9668-physical-ai-chatbot.hf.space/chat";

const getSessionId = () => {
  if (typeof window === 'undefined') return 'ssr';
  let id = localStorage.getItem('chatSessionId');
  if (!id) {
    id = 'session-' + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('chatSessionId', id);
  }
  return id;
};

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { type: 'bot', content: "Hello! I'm the Embodied Intelligence Assistant. How can I help with the textbook today?" }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const { colorMode } = useColorMode();
  const isDark = colorMode === 'dark';

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userText = inputValue.trim();
    // 1. Log to console so you can see it working
    console.log("🚀 Pinging AI at:", BACKEND_URL);

    setMessages(prev => [...prev, { type: 'user', content: userText }]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(BACKEND_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_input: userText,
          session_id: getSessionId(),
          history: messages.map(m => ({
            role: m.type === 'user' ? 'user' : 'assistant',
            content: m.content
          }))
        }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      setMessages(prev => [...prev, { type: 'bot', content: data.answer }]);
    } catch (err) {
      console.error("❌ API ERROR:", err);
      setMessages(prev => [...prev, { type: 'bot', content: "Connection error. Please ensure the Hugging Face Space is 'Running'." }]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className={styles.chatbotContainer}>
      {!isOpen && (
        <button className={styles.chatbotButton} onClick={() => setIsOpen(true)}>🤖</button>
      )}
      {isOpen && (
        <div className={`${styles.chatbotWindow} ${isDark ? styles.darkTheme : ''}`}>
          <div className={styles.chatbotHeader}>
            <span>AI Assistant</span>
            <button onClick={() => setIsOpen(false)}>✕</button>
          </div>
          <div className={styles.chatbotMessages}>
            {messages.map((m, i) => (
              <div key={i} className={`${styles.message} ${styles[m.type]}`}>{m.content}</div>
            ))}
            {isLoading && <div className={styles.typing}>AI is thinking...</div>}
            <div ref={messagesEndRef} />
          </div>
          <div className={styles.chatbotInputArea}>
            <input 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Type a message..."
            />
            <button onClick={handleSendMessage}>Send</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbot;