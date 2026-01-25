import React, { useState } from 'react';
import './App.css';

interface ValidationResult {
  question: string;
  layer1_result: string;
  layer2_result?: string;
  final_status: string;
  explanation?: string;
  message?: string;
  confidence: number;
  total_latency_ms: number;
}

function App() {
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [loading, setLoading] = useState(false);

  const validateQuestion = async () => {
    if (!question.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'VALID': return '#4CAF50';
      case 'WARNING': return '#FF9800';
      case 'OUT_OF_SYLLABUS': return '#f44336';
      default: return '#757575';
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>CA3104 Academic Doubt Clarification System</h1>
        <p>Two-Layer AI Validation for Computer Networks Questions</p>
      </header>

      <main className="main-content">
        <div className="input-section">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Enter your Computer Networks question here..."
            rows={4}
            className="question-input"
          />
          <button 
            onClick={validateQuestion}
            disabled={loading || !question.trim()}
            className="validate-btn"
          >
            {loading ? 'Validating...' : 'Validate Question'}
          </button>
        </div>

        {result && (
          <div className="result-section">
            <div className="result-header">
              <h3>Validation Result</h3>
              <span 
                className="status-badge"
                style={{ backgroundColor: getStatusColor(result.final_status) }}
              >
                {result.final_status}
              </span>
            </div>

            <div className="result-details">
              <div className="layer-results">
                <div className="layer-result">
                  <h4>Layer 1 (Syllabus Check)</h4>
                  <p>{result.layer1_result}</p>
                </div>
                {result.layer2_result && (
                  <div className="layer-result">
                    <h4>Layer 2 (Academic Quality)</h4>
                    <p>{result.layer2_result}</p>
                  </div>
                )}
              </div>

              <div className="explanation">
                <h4>Explanation</h4>
                <p>{result.explanation || result.message}</p>
              </div>

              <div className="metrics">
                <div className="metric">
                  <span>Confidence:</span>
                  <span>{(result.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="metric">
                  <span>Processing Time:</span>
                  <span>{result.total_latency_ms.toFixed(0)}ms</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;