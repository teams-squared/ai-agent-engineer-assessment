import './App.css';

function App() {
  // Static example response for design
  const staticResponse = {
    summary: "Employees are entitled to 15 days of paid vacation per year. Vacation requests must be submitted at least two weeks in advance for approval by the manager.",
    bullets: [
      "15 days paid vacation per year for full-time employees",
      "Requests require manager approval",
      "Submit requests at least 2 weeks in advance",
      "Accrues at a rate of 1.25 days per month"
    ]
  };

  return (
    <div className="app">
      <header>
        <h1>Company Policy Assistant</h1>
        <p>Ask questions about company policies</p>
      </header>
      
      <main>
        <form onSubmit={(e) => e.preventDefault()}>
          <div className="input-group">
            <input
              type="text"
              placeholder="What's the vacation policy?"
              aria-label="Ask a policy question"
            />
            <button type="submit">
              Ask
            </button>
          </div>
        </form>

        {/* Static response example */}
        <div className="response">
          <div className="summary">
            <h2>Summary</h2>
            <p>{staticResponse.summary}</p>
          </div>
          
          <div className="bullets">
            <h2>Key Details</h2>
            <ul>
              {staticResponse.bullets.map((bullet, i) => (
                <li key={i}>{bullet}</li>
              ))}
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;