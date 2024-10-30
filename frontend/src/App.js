import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [question, setQuestion] = useState('');
  const [sqlQuery, setSqlQuery] = useState('');
  const [editableSqlQuery, setEditableSqlQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [feedbackLoop, setFeedbackLoop] = useState(false);

  const handleGenerate = async (e, includeError = false) => {
    e?.preventDefault();
    setLoading(true);
    setError('');
    setResults(null);

    try {
      // Get SQL query with optional error feedback
      const queryResponse = await axios.post('http://localhost:8000/query', {
        question: question,
        previous_error: includeError ? error : null,
        previous_query: includeError ? editableSqlQuery : null
      });
      const generatedQuery = queryResponse.data.sql_query;
      setSqlQuery(generatedQuery);
      setEditableSqlQuery(generatedQuery);
      setFeedbackLoop(false); // Reset feedback loop if successful
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during generation');
      setFeedbackLoop(true);
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    setLoading(true);
    setError('');
    setResults(null);
    try {
      const response = await axios.post('http://localhost:8000/execute-query', {
        query: editableSqlQuery
      });
      setResults(response.data.results);
      setFeedbackLoop(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred');
      setFeedbackLoop(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>SQL Query Generator</h1>
      </header>

      <main className="App-main">
        <section className="input-section">
          <h2>Enter Your Question</h2>
          <form onSubmit={handleGenerate}>
            <div className="input-group">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Enter your question..."
                className="question-input"
              />
              <button type="submit" disabled={loading}>
                {loading ? 'Generating...' : 'Generate SQL'}
              </button>
            </div>
          </form>
        </section>

        {error && (
          <div className="error-section">
            <div className="error">{error}</div>
            {feedbackLoop && (
              <button 
                onClick={(e) => handleGenerate(e, true)}
                className="retry-button"
                disabled={loading}
              >
                Retry with Error Feedback
              </button>
            )}
          </div>
        )}

        {sqlQuery && (
          <section className="query-section">
            <h2>Generated SQL Query</h2>
            <div className="query-editor">
              <textarea
                value={editableSqlQuery}
                onChange={(e) => setEditableSqlQuery(e.target.value)}
                className="sql-editor"
                rows={5}
              />
              <button
                onClick={handleExecute}
                className="execute-button"
                disabled={loading}
              >
                {loading ? 'Executing...' : 'Execute Query'}
              </button>
            </div>
          </section>
        )}

        {results && (
          <section className="result-section">
            <h2>Results</h2>
            <div className="results-table">
              {results.length > 0 ? (
                <table>
                  <tbody>
                    {results.map((row, i) => (
                      <tr key={i}>
                        {row.map((cell, j) => (
                          <td key={j}>{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p>No results found</p>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;