import { createRoot } from 'react-dom/client';
import './index.css';

// Since we're using vanilla HTML/CSS/JS for the AI assistant,
// we'll just redirect to the index.html
window.location.href = '/index.html';

// Fallback React component if needed
function App() {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>AI Coding Assistant</h1>
      <p>Redirecting to AI Coding Assistant...</p>
      <a href="/index.html">Click here if not redirected automatically</a>
    </div>
  );
}

const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(<App />);
}