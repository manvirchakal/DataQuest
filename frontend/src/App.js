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

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSqlQuery('');
    setEditableSqlQuery('');
    setResults(null);

    try {
      // Get SQL query
      const queryResponse = await axios.post('http://localhost:8000/query', {
        question: question
      });
      const generatedQuery = queryResponse.data.sql_query;
      setSqlQuery(generatedQuery);
      setEditableSqlQuery(generatedQuery);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during generation');
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteQuery = async () => {
    setLoading(true);
    setError('');
    setResults(null);

    try {
      const resultsResponse = await axios.post('http://localhost:8000/execute-query', {
        query: editableSqlQuery
      });
      setResults(resultsResponse.data.results);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred during execution');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>DataQuest</h1>
        <p>Natural Language to SQL Query Converter</p>
      </header>

      <main className="App-main">
        {/* Question Input Section */}
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

        {error && <div className="error">{error}</div>}

        {/* SQL Query Section */}
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
                onClick={handleExecuteQuery} 
                disabled={loading || !editableSqlQuery}
                className="execute-button"
              >
                {loading ? 'Executing...' : 'Execute Query'}
              </button>
            </div>
          </section>
        )}

        {/* Results Section */}
        {results && (
          <section className="result-section">
            <h2>Query Results</h2>
            <div className="results-table">
              {results.length > 0 ? (
                <table>
                  <thead>
                    <tr>
                      {Object.keys(results[0]).map(key => (
                        <th key={key}>{key}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((row, i) => (
                      <tr key={i}>
                        {Object.values(row).map((value, j) => (
                          <td key={j}>{value}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="no-results">No results found</p>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}

export default App;
