import { useState } from 'react';

import { sendChatMessage } from './api/chatApi';
import ChatInput from './components/ChatInput';
import ChatWindow from './components/ChatWindow';

const welcomeMessage = {
  id: 'welcome',
  role: 'assistant',
  text: "Hi! I'm the Pret Employee Assistant. I can help with store procedures, equipment issues and other internal guidance.",
};

function App() {
  const [messages, setMessages] = useState([welcomeMessage]);
  const [conversationId, setConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(message) {
    const userMessage = {
      id: `${Date.now()}-user`,
      role: 'user',
      text: message,
    };

    setMessages((currentMessages) => [...currentMessages, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(message, conversationId);

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `${Date.now()}-assistant`,
          role: 'assistant',
          text: response.message,
        },
      ]);
      return true;
    } catch {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `${Date.now()}-error`,
          role: 'assistant',
          text: "Sorry, I'm having trouble connecting right now. Please try again.",
          isError: true,
        },
      ]);
      return false;
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="top-bar">
        <div className="brand-lockup" aria-label="Pret Employee Assistant">
          <img className="pret-logo" src="/pret-logo.png" alt="Pret" />
          <div>
            <p className="eyebrow">Employee support</p>
            <h1>Pret Employee Assistant</h1>
            <p className="subtitle">Your guide to Pret store procedures and support</p>
          </div>
        </div>
        <div className="status-chip">
          <span className="status-dot" aria-hidden="true" />
          Ready to help
        </div>
      </header>

      <section className="chat-card" aria-label="Pret Employee Assistant chat">
        <div className="chat-card-header">
          <div>
            <p className="section-label">Conversation</p>
            <h2>How can I help today?</h2>
          </div>
          <span className="context-note">Internal guidance</span>
        </div>
        <ChatWindow messages={messages} isLoading={isLoading} />
        <ChatInput onSubmit={handleSubmit} disabled={isLoading} />
      </section>

      <footer className="app-footer">
        <span>Check with your manager when a situation is urgent or unclear.</span>
        <span className="footer-rule" aria-hidden="true" />
        <span>POC assistant</span>
      </footer>
    </main>
  );
}

export default App;
