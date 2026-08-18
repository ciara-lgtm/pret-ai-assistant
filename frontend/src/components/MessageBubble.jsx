import ReactMarkdown from 'react-markdown';
import rehypeSanitize from 'rehype-sanitize';
import remarkGfm from 'remark-gfm';

function normalizeEscapedMarkdown(value) {
  return value
    .replace(/\\(?=#{1,6}\s)/g, '')
    .replace(/\\(?=\*\*)/g, '')
    .replace(/\\(?=-\s)/g, '')
    .replace(/\\(?=\d+[.)]\s)/g, '');
}

function MessageBubble({ message }) {
  return (
    <article className={`message ${message.role} ${message.isError ? 'error-message' : ''}`}>
      {message.role === 'assistant' && (
        <span className="message-avatar" aria-hidden="true">P</span>
      )}
      <div className="message-content">
        {message.role === 'assistant' ? (
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeSanitize]}
          >
            {normalizeEscapedMarkdown(message.text)}
          </ReactMarkdown>
        ) : (
          <p>{message.text}</p>
        )}
      </div>
    </article>
  );
}

export default MessageBubble;