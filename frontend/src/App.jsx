import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';

function App() {
  return (
    <main className="app-shell">
      <header className="top-bar">
        <div>
          <p className="eyebrow">Pret AI Assistant</p>
          <h1>Coffee machine troubleshooting</h1>
        </div>
      </header>

      <ChatWindow />
      <ChatInput />
    </main>
  );
}

export default App;
