import React, { useState, useEffect } from 'react';
import { useAnalytics } from '../hooks/useAnalytics';
import '../styles/AnalyticsPage.css';

function AnalyticsPage() {
  const { analytics, loading, error } = useAnalytics();

  const strategyColors = {
    direct_llm: '#4CAF50',
    document_rag: '#2196F3',
    web_search_rag: '#FF9800',
    hybrid_rag: '#9C27B0',
    graph_rag: '#F44336',
    self_rag: '#00BCD4',
  };

  return (
    <div className="analytics-page">
      <div className="analytics-container">
        <h1>📊 Analytics Dashboard</h1>

        {error && (
          <div className="error-message">
            <span>❌</span> {error}
          </div>
        )}

        {loading ? (
          <div className="loading">Loading analytics...</div>
        ) : analytics ? (
          <div className="analytics-grid">
            <div className="metric-card">
              <div className="metric-label">Total Queries</div>
              <div className="metric-value">{analytics.total_queries || 0}</div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Avg Response Time</div>
              <div className="metric-value">
                {analytics.avg_latency ? analytics.avg_latency.toFixed(3) : '0'}s
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Avg Confidence</div>
              <div className="metric-value">
                {analytics.avg_confidence
                  ? Math.round(analytics.avg_confidence * 100)
                  : 0}%
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-label">Success Rate</div>
              <div className="metric-value">
                {analytics.success_rate ? Math.round(analytics.success_rate * 100) : 0}%
              </div>
            </div>

            {analytics.strategy_distribution && (
              <div className="chart-card wide">
                <h3>Strategy Distribution</h3>
                <div className="strategy-list">
                  {Object.entries(analytics.strategy_distribution).map(
                    ([strategy, count]) => (
                      <div key={strategy} className="strategy-row">
                        <div className="strategy-info">
                          <div
                            className="strategy-color"
                            style={{
                              backgroundColor: strategyColors[strategy] || '#999',
                            }}
                          />
                          <span className="strategy-name">
                            {strategy.replace(/_/g, ' ')}
                          </span>
                        </div>
                        <div className="strategy-stat">
                          <span className="count">{count}</span>
                          <span className="percent">
                            (
                            {analytics.total_queries > 0
                              ? Math.round((count / analytics.total_queries) * 100)
                              : 0}
                            %)
                          </span>
                        </div>
                      </div>
                    )
                  )}
                </div>
              </div>
            )}

            {analytics.top_queries && analytics.top_queries.length > 0 && (
              <div className="chart-card wide">
                <h3>Top Queries</h3>
                <div className="queries-list">
                  {analytics.top_queries.slice(0, 5).map((q, idx) => (
                    <div key={idx} className="query-item">
                      <span className="query-rank">#{idx + 1}</span>
                      <span className="query-text">{q.query}</span>
                      <span className="query-count">{q.count}x</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="empty-state">
            <p>No analytics data available yet.</p>
            <p>Start using the query interface to see analytics!</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default AnalyticsPage;
