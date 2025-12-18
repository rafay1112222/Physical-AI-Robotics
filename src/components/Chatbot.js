import React, { useState, useRef, useEffect } from 'react';
import { useColorMode } from '@docusaurus/theme-common';
import styles from './Chatbot.module.css';

// --- Configuration ---
const API_URL = "https://abd9668-physical-ai-chatbot.hf.space/chat";

// Function to generate and manage a session ID
const getSessionId = () => {
    let id = typeof window !== 'undefined' ? localStorage.getItem('chatSessionId') : null;
    if (!id && typeof window !== 'undefined') {
        id = 'session-' + Date.now().toString(36) + Math.random().toString(36).substring(2);
        localStorage.setItem('chatSessionId', id);
    }
    return id || 'default-session';
};

// Custom hook to safely get color mode with a fallback
function useSafeColorMode() {
    try {
        return useColorMode();
    } catch (error) {
        return { colorMode: 'light', setColorMode: () => {} };
    }
}

const Chatbot = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { type: 'bot', content: "Hello! I'm your AI assistant for the EMBODIED INTELLIGENCE textbook by Abdur Rafay. How can I help you today?" }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const { colorMode, setColorMode } = useSafeColorMode();
    const isDarkTheme = colorMode === 'dark';

    const toggleTheme = () => {
        if (setColorMode) setColorMode(isDarkTheme ? 'light' : 'dark');
    };

    const toggleChat = () => setIsOpen(!isOpen);

    const handleInputChange = (e) => setInputValue(e.target.value);

    const handleSendMessage = async () => {
        if (!inputValue.trim()) return;

        const userInput = inputValue.trim();
        
        // 1. Update UI with User Message
        const userMessage = { type: 'user', content: userInput };
        const updatedMessages = [...messages, userMessage];
        setMessages(updatedMessages);
        setInputValue('');
        setIsLoading(true);

        // 2. Format history for the backend (Python RAG API expects list of dicts)
        const historyPayload = updatedMessages
            .slice(0, -1) // Everything except the very last message we just added
            .filter(msg => msg.type !== 'error') // Clean history
            .map(msg => ({
                role: msg.type === 'user' ? 'user' : 'assistant',
                content: msg.content
            }));

        // 3. Construct API payload
        const payload = {
            user_input: userInput,
            session_id: getSessionId(),
            history: historyPayload
        };

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`Server Error: ${response.status}`);
            }

            const data = await response.json();
            
            // 4. Update UI with Bot Response
            setMessages(prev => [...prev, { type: 'bot', content: data.answer }]);

        } catch (error) {
            console.error('API Error:', error);
            setMessages(prev => [...prev, { type: 'bot', content: "Sorry, I'm having trouble connecting to my brain. Please check if the Hugging Face Space is running!" }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    return (
        <div className={styles.chatbotContainer}>
            {!isOpen && (
                <button className={styles.chatbotButton} onClick={toggleChat}>
                    <svg className={styles.botIcon} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1H5C3.89 1 3 1.89 3 3V19C3 20.1 3.9 21 5 21H11V19H5V3H13V9H21ZM11 11H13V13H11V11ZM15 11H17V13H15V11ZM11 15H13V17H11V15ZM15 15H17V17H15V15Z" />
                    </svg>
                </button>
            )}

            {isOpen && (
                <div className={`${styles.chatbotWindow} ${isDarkTheme ? styles.darkTheme : styles.lightTheme}`}>
                    <div className={styles.chatbotHeader}>
                        <div className={styles.chatbotTitle}>Embodied Intelligence Assistant</div>
                        <div className={styles.headerActions}>
                            <button className={styles.themeToggle} onClick={toggleTheme} title="Toggle theme">
                                {isDarkTheme ? '☀️' : '🌙'}
                            </button>
                            <button className={styles.closeButton} onClick={toggleChat} aria-label="Close chat">✕</button>
                        </div>
                    </div>
                    
                    <div className={styles.chatbotMessages}>
                        {messages.map((message, index) => (
                            <div key={index} className={`${styles.message} ${styles[message.type]} ${isDarkTheme ? styles.darkMode : ''}`}>
                                {message.content}
                            </div>
                        ))}
                        {isLoading && (
                            <div className={`${styles.message} ${styles.bot} ${isDarkTheme ? styles.darkMode : ''}`}>
                                <div className={styles.typingIndicator}>
                                    <span></span><span></span><span></span>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                    
                    <div className={styles.chatbotInputArea}>
                        <textarea
                            value={inputValue}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask about Physical AI..."
                            className={styles.chatbotInput}
                            rows="1"
                        />
                        <button 
                            onClick={handleSendMessage} 
                            disabled={isLoading || !inputValue.trim()}
                            className={styles.sendButton}
                        >
                            Send
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Chatbot;