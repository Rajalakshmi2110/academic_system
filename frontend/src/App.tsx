import React, { useState } from 'react';
import './App.css';

interface IntermediateStep {
  step: number;
  name: string;
  description: string;
  input: string;
  output: any;
  time_ms: number;
  status: string;
}

interface ValidationResult {
  question: string;
  layer1_result: string;
  layer2_result?: string;
  final_status: string;
  explanation?: string;
  message?: string;
  confidence: number;
  total_latency_ms: number;
  intermediate_steps?: IntermediateStep[];
}

function App() {
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const validateQuestion = async () => {
    if (!question.trim()) return;
    
    setLoading(true);
    setError('');
    try {
      const response = await fetch('http://localhost:5000/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setError('Failed to connect to validation service');
      console.error('Error:', error);
    }
    setLoading(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'VALID': return '✓';
      case 'WARNING': return '⚠';
      case 'OUT_OF_SYLLABUS': return '✗';
      default: return '?';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'VALID': return '#10b981';
      case 'WARNING': return '#f59e0b';
      case 'OUT_OF_SYLLABUS': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const clearResult = () => {
    setResult(null);
    setError('');
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <div className="header-content">
            <div className="logo">
              <div className="logo-icon">CA</div>
              <div>
                <h1>CA3104 Academic Question Validator</h1>
                <p>Computer Networks</p>
              </div>
            </div>
            <div className="header-badge">Two-Layer AI System</div>
          </div>
        </header>

        <main className="main">
          <div className="input-card">
            <div className="input-header">
              <h2>Submit Your Question</h2>
              <p>Enter your Computer Networks question for academic validation</p>
            </div>
            
            <div className="input-group">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., Explain the TCP three-way handshake process..."
                rows={4}
                className="question-input"
                maxLength={500}
              />
              <div className="input-footer">
                <span className="char-count">{question.length}/500</span>
                <div className="button-group">
                  {result && (
                    <button onClick={clearResult} className="btn-secondary">
                      Clear
                    </button>
                  )}
                  <button 
                    onClick={validateQuestion}
                    disabled={loading || !question.trim()}
                    className="btn-primary"
                  >
                    {loading ? (
                      <><span className="spinner"></span> Validating...</>
                    ) : (
                      <>Validate Question</>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {error && (
            <div className="error-card">
              <div className="error-icon">!</div>
              <div>
                <h3>Connection Error</h3>
                <p>{error}</p>
              </div>
            </div>
          )}

          {result && (
            <div className="result-card">
              <div className="result-header">
                <div className="result-title">
                  <h2>Validation Result</h2>
                  <div className="result-timestamp">
                    {new Date().toLocaleTimeString()}
                  </div>
                </div>
                <div 
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(result.final_status) }}
                >
                  <span className="status-icon">{getStatusIcon(result.final_status)}</span>
                  {result.final_status.replace('_', ' ')}
                </div>
              </div>

              <div className="question-display">
                <h4>Question Analyzed:</h4>
                <p>"{result.question}"</p>
              </div>

              <div className="layers-grid">
                <div className="layer-card layer1">
                  <div className="layer-header">
                    <div className="layer-icon">L1</div>
                    <div>
                      <h3>Layer 1</h3>
                      <p>Syllabus Relevance</p>
                    </div>
                  </div>
                  <div className="layer-result">
                    {result.layer1_result}
                  </div>
                </div>

                {result.layer2_result && (
                  <div className="layer-card layer2">
                    <div className="layer-header">
                      <div className="layer-icon">L2</div>
                      <div>
                        <h3>Layer 2</h3>
                        <p>Academic Quality</p>
                      </div>
                    </div>
                    <div className="layer-result">
                      {result.layer2_result}
                    </div>
                  </div>
                )}
              </div>

              <div className="explanation-card">
                <h3>Detailed Explanation</h3>
                <p>{result.explanation || result.message}</p>
              </div>

              {result.intermediate_steps && (
                <div className="steps-card">
                  <h3>Processing Steps</h3>
                  <div className="steps-list">
                    {result.intermediate_steps.map((step, index) => (
                      <div key={index} className="step-item">
                        <div className="step-header">
                          <div className="step-number">Step {step.step}</div>
                          <div className="step-info">
                            <h4>{step.name}</h4>
                            <p>{step.description}</p>
                          </div>
                          <div className="step-time">{step.time_ms.toFixed(1)}ms</div>
                        </div>
                        <div className="step-status" style={{ color: getStatusColor(step.status) }}>
                          {step.status}
                        </div>
                        <div className="step-output">
                          <details>
                            <summary>View Details</summary>
                            <pre>{JSON.stringify(step.output, null, 2)}</pre>
                          </details>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-icon">%</div>
                  <div className="metric-content">
                    <div className="metric-value">{(result.confidence * 100).toFixed(1)}%</div>
                    <div className="metric-label">Confidence Score</div>
                  </div>
                </div>
                <div className="metric-card">
                  <div className="metric-icon">ms</div>
                  <div className="metric-content">
                    <div className="metric-value">{result.total_latency_ms.toFixed(0)}ms</div>
                    <div className="metric-label">Processing Time</div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>

        <footer className="footer">
          <p>© 2024 CA3104 Academic System • Powered by DistilBERT & FLAN-T5</p>
        </footer>
      </div>
    </div>
  );
}

export default App;