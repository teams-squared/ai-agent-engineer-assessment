import { useState, FormEvent } from 'react';
import './App.css';


interface PolicyResponse {
  summary: string;
  bullets: string[];
}

function App() {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<PolicyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    
    setLoading(true);
    setError('');
    setResponse(null);
    
    try {
      console.log(question)
      const res = await fetch('http://localhost:5000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question.trim() })
      });
      
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      
      const data: PolicyResponse = await res.json();
      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>Company Policy Assistant</h1>
        <p>Ask questions about company policies</p>
      </header>
      
      <main>
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What's the vacation policy?"
              disabled={loading}
              aria-label="Ask a policy question"
            />
            <button 
              type="submit" 
              disabled={loading || !question.trim()}
              aria-busy={loading}
            >
              {loading ? 'Asking...' : 'Ask'}
            </button>
          </div>
        </form>

        {loading && <div className="loading" aria-live="polite">Searching policies...</div>}
        
        {error && (
          <div className="error" role="alert">
            <strong>Error:</strong> {error}
          </div>
        )}

        {response && (
          <div className="response">
            <div className="summary">
              <h2>Summary</h2>
              <p>{response.summary}</p>
            </div>
            
            {response.bullets.length > 0 && (
              <div className="bullets">
                <h2>Key Details</h2>
                <ul>
                  {response.bullets.map((bullet, i) => (
                    <li key={i}>{bullet}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </main>

    </div>
  );
}

export default App;