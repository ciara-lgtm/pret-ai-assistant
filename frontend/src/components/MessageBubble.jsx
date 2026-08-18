function MessageBubble({ message }) {
  const lines = message.text.split('\n');

  return (
    <article className={`message ${message.role} ${message.isError ? 'error-message' : ''}`}>
      {message.role === 'assistant' && (
        <span className="message-avatar" aria-hidden="true">P</span>
      )}
      <div className="message-content">
        {lines.map((line, index) => {
          const numberedItem = line.match(/^(\d+)[.)]\s+(.*)$/);

          if (numberedItem) {
            return (
              <div className="numbered-line" key={`${message.id}-${index}`}>
                <span>{numberedItem[1]}.</span>
                <p>{numberedItem[2]}</p>
              </div>
            );
          }

          return <p key={`${message.id}-${index}`}>{line || '\u00a0'}</p>;
        })}
      </div>
    </article>
  );
}

export default MessageBubble;