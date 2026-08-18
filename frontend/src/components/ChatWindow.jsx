import MessageBubble from './MessageBubble';

function ChatWindow({ messages, isLoading }) {
  return (
    <section className="chat-window" aria-label="Conversation history">
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      {isLoading && (
        <div className="message assistant loading-message" aria-label="Assistant is typing">
          <span className="message-avatar" aria-hidden="true">P</span>
          <div className="typing-indicator">
            <span />
            <span />
            <span />
          </div>
        </div>
      )}
    </section>
  );
}

export default ChatWindow;
