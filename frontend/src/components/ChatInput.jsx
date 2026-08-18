import { useState } from 'react';

function ChatInput({ onSubmit, disabled }) {
  const [value, setValue] = useState('');

  function handleSubmit(event) {
    event.preventDefault();
    const message = value.trim();

    if (!message || disabled) {
      return;
    }

    setValue('');
    onSubmit(message);
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form.requestSubmit();
    }
  }

  return (
    <form className="chat-input" aria-label="Message composer" onSubmit={handleSubmit}>
      <textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask about a store procedure or equipment issue..."
        aria-label="Your message"
        rows="1"
        disabled={disabled}
      />
      <button type="submit" disabled={disabled || !value.trim()} aria-label="Send message">
        <span>Send</span>
        <span className="send-arrow" aria-hidden="true">↗</span>
      </button>
    </form>
  );
}

export default ChatInput;
