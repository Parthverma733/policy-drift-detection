import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts'
import './DriftDashboard.css'

const API_BASE = 'https://policy-drift-detection-1.onrender.com'

function DriftDashboard() {
  const location = useLocation()
  const [drifts, setDrifts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({
    policy_id: '',
    district_id: '',
    drift_type: '',
    severity: '',
    month: ''
  })

  useEffect(() => {
    if (location.state?.driftResults) {
      setDrifts(location.state.driftResults.drifts || [])
      setLoading(false)
    } else {
      loadDrifts()
    }
  }, [location.state])

  const loadDrifts = async () => {
    try {
      setLoading(true)
      const params = {}
      if (filters.policy_id) params.policy_id = filters.policy_id
      if (filters.district_id) params.district_id = filters.district_id
      if (filters.drift_type) params.drift_type = filters.drift_type
      if (filters.severity) params.severity = filters.severity
      if (filters.month) params.month = filters.month

      const response = await axios.get(`${API_BASE}/drift/results`, { params })
      setDrifts(response.data.drifts || [])
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load drift results')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!location.state?.driftResults) {
      loadDrifts()
    }
  }, [filters])

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return '#ef4444'
      case 'medium': return '#f59e0b'
      case 'low': return '#3b82f6'
      default: return '#6b7280'
    }
  }

  const summaryData = {
    total: drifts.length,
    high: drifts.filter(d => d.severity === 'high').length,
    medium: drifts.filter(d => d.severity === 'medium').length,
    low: drifts.filter(d => d.severity === 'low').length
  }

  const byTypeData = drifts.reduce((acc, drift) => {
    acc[drift.drift_type] = (acc[drift.drift_type] || 0) + 1
    return acc
  }, {})

  const chartData = Object.entries(byTypeData).map(([type, count]) => ({
    type,
    count
  }))

  const byMonthData = drifts.reduce((acc, drift) => {
    const month = drift.month || 'Unknown'
    acc[month] = (acc[month] || 0) + 1
    return acc
  }, {})

  const timelineData = Object.entries(byMonthData)
    .sort()
    .map(([month, count]) => ({
      month,
      count
    }))

  if (loading) {
    return <div className="loading">Loading drift results...</div>
  }

  return (
    <div className="drift-dashboard">
      <h2>Drift Dashboard</h2>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="summary-cards">
        <div className="summary-card">
          <div className="summary-value">{summaryData.total}</div>
          <div className="summary-label">Total Drifts</div>
        </div>
        <div className="summary-card" style={{ background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' }}>
          <div className="summary-value">{summaryData.high}</div>
          <div className="summary-label">High Severity</div>
        </div>
        <div className="summary-card" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
          <div className="summary-value">{summaryData.medium}</div>
          <div className="summary-label">Medium Severity</div>
        </div>
        <div className="summary-card" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}>
          <div className="summary-value">{summaryData.low}</div>
          <div className="summary-label">Low Severity</div>
        </div>
      </div>

      <div className="filters-section">
        <h3>Filters</h3>
        <div className="filters-grid">
          <input
            type="text"
            placeholder="Policy ID"
            value={filters.policy_id}
            onChange={(e) => setFilters({ ...filters, policy_id: e.target.value })}
            className="filter-input"
          />
          <input
            type="text"
            placeholder="District ID"
            value={filters.district_id}
            onChange={(e) => setFilters({ ...filters, district_id: e.target.value })}
            className="filter-input"
          />
          <select
            value={filters.drift_type}
            onChange={(e) => setFilters({ ...filters, drift_type: e.target.value })}
            className="filter-input"
          >
            <option value="">All Types</option>
            <option value="metric">Metric</option>
            <option value="temporal">Temporal</option>
            <option value="allocation">Allocation</option>
          </select>
          <select
            value={filters.severity}
            onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
            className="filter-input"
          >
            <option value="">All Severities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <input
            type="text"
            placeholder="Month (e.g., 2024-01)"
            value={filters.month}
            onChange={(e) => setFilters({ ...filters, month: e.target.value })}
            className="filter-input"
          />
        </div>
      </div>

      {chartData.length > 0 && (
        <div className="chart-section">
          <h3>Drifts by Type</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="type" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#667eea" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {timelineData.length > 0 && (
        <div className="chart-section">
          <h3>Drift Timeline</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timelineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="count" stroke="#667eea" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="drifts-list">
        <h3>Detailed Findings ({drifts.length})</h3>
        {drifts.length === 0 ? (
          <div className="no-drifts">
            <p>✓ No policy drift detected. Implementation aligns with policy intent.</p>
          </div>
        ) : (
          drifts.map((drift, index) => (
            <div key={drift._id || index} className="drift-card">
              <div className="drift-header">
                <span className="drift-number">#{index + 1}</span>
                <span
                  className="severity-badge"
                  style={{ backgroundColor: getSeverityColor(drift.severity) }}
                >
                  {drift.severity?.toUpperCase() || 'UNKNOWN'}
                </span>
              </div>
              <div className="drift-content">
                <p className="drift-explanation">
                  District {drift.district_name} ({drift.district_id}) in {drift.month}: 
                  {drift.metric} value {drift.actual_value?.toFixed(2)} violates threshold of {drift.expected_threshold?.toFixed(2)}.
                  Severity: {drift.severity}.
                </p>
                <div className="drift-details">
                  <div className="detail-item">
                    <strong>Type:</strong> {drift.drift_type}
                  </div>
                  <div className="detail-item">
                    <strong>Constraint:</strong> {drift.constraint_type}
                  </div>
                  <div className="detail-item">
                    <strong>Metric:</strong> {drift.metric}
                  </div>
                  <div className="detail-item">
                    <strong>Actual Value:</strong> {drift.actual_value?.toFixed(2)}
                  </div>
                  <div className="detail-item">
                    <strong>Expected Threshold:</strong> {drift.expected_threshold?.toFixed(2)}
                  </div>
                  <div className="detail-item">
                    <strong>Month:</strong> {drift.month}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default DriftDashboard
