function ChatInput() {
  return (
    <form className="chat-input" aria-label="Message composer">
      <input
        type="text"
        placeholder="Describe the issue you are seeing..."
        aria-label="Troubleshooting message"
        disabled
      />
      <button type="submit" disabled>
        Send
      </button>
    </form>
  );
}

export default ChatInput;
