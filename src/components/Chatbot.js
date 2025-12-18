import React, { useState, useRef, useEffect } from 'react';
import { useColorMode } from '@docusaurus/theme-common';
import styles from './Chatbot.module.css';

// --- HARD-WIRED BACKEND ---
const BACKEND_URL = "https://abd9668-physical-ai-chatbot.hf.space/chat";

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([{ type: 'bot', content: "AI is online. Version: 2.1" }]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;
    
    // THIS ALERT PROVES THE NEW CODE IS RUNNING
    alert("Attempting to talk to: " + BACKEND_URL);

    const userText = inputValue.trim();
    setMessages(prev => [...prev, { type: 'user', content: userText }]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(BACKEND_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_input: userText,
          session_id: "test-session",
          history: [] 
        }),
      });

      const data = await response.json();
      setMessages(prev => [...prev, { type: 'bot', content: data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { type: 'bot', content: "Error: " + err.message }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.chatbotContainer}>
      {!isOpen && <button className={styles.chatbotButton} onClick={() => setIsOpen(true)}>🤖</button>}
      {isOpen && (
        <div className={styles.chatbotWindow}>
          <div className={styles.chatbotHeader}>AI Assistant <button onClick={() => setIsOpen(false)}>✕</button></div>
          <div className={styles.chatbotMessages}>
            {messages.map((m, i) => <div key={i} className={`${styles.message} ${styles[m.type]}`}>{m.content}</div>)}
            <div ref={messagesEndRef} />
          </div>
          <div className={styles.chatbotInputArea}>
            <input value={inputValue} onChange={(e)=>setInputValue(e.target.value)} onKeyDown={(e)=>e.key==='Enter' && handleSendMessage()}/>
            <button onClick={handleSendMessage}>Send</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbot;