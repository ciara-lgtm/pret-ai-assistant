const messages = [
  {
    id: 1,
    role: 'assistant',
    text: 'Hello! I can help you troubleshoot a coffee machine issue. Share what you are seeing and I will guide you to the next step.',
  },
  {
    id: 2,
    role: 'user',
    text: 'The machine is not dispensing coffee.',
  },
  {
    id: 3,
    role: 'assistant',
    text: 'Let us first confirm the basics: power, water level, and whether the machine is showing an error code.',
  },
];

function ChatWindow() {
  return (
    <section className="chat-window" aria-label="Conversation history">
      {messages.map((message) => (
        <article key={message.id} className={`message ${message.role}`}>
          <p>{message.text}</p>
        </article>
      ))}
    </section>
  );
}

export default ChatWindow;
