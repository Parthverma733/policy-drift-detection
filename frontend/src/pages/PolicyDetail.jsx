import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import PolicyChatbot from '../components/PolicyChatbot'
import './PolicyDetail.css'

const API_BASE = 'https://policy-drift-detection-1.onrender.com'

function PolicyDetail() {
  const { policyId } = useParams()
  const navigate = useNavigate()
  const [policy, setPolicy] = useState(null)
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [uploadingDataset, setUploadingDataset] = useState(false)
  const [runningDrift, setRunningDrift] = useState(false)
  const [selectedDataset, setSelectedDataset] = useState(null)

  useEffect(() => {
    loadPolicy()
    loadDatasets()
  }, [policyId])

  const loadPolicy = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/policies/${policyId}`)
      setPolicy(response.data)
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load policy')
    } finally {
      setLoading(false)
    }
  }

  const loadDatasets = async () => {
    try {
      const response = await axios.get(`${API_BASE}/datasets/policy/${policyId}`)
      setDatasets(response.data.datasets || [])
    } catch (err) {
      console.error('Failed to load datasets:', err)
    }
  }

  const handleDatasetUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    try {
      setUploadingDataset(true)
      setError(null)
      const formData = new FormData()
      formData.append('file', file)
      formData.append('policy_id', policyId)

      await axios.post(`${API_BASE}/datasets/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      await loadDatasets()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload dataset')
    } finally {
      setUploadingDataset(false)
    }
  }

  const handleRunDrift = async (datasetId) => {
    try {
      setRunningDrift(true)
      setError(null)
      const response = await axios.post(`${API_BASE}/drift/run`, null, {
        params: {
          policy_id: policyId,
          dataset_id: datasetId
        }
      })

      navigate('/drift', { state: { driftResults: response.data } })
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to run drift detection')
    } finally {
      setRunningDrift(false)
    }
  }

  if (loading) {
    return <div className="loading">Loading policy details...</div>
  }

  if (!policy) {
    return <div className="error-message">Policy not found</div>
  }

  const intent = policy.extracted_intent || {}

  return (
    <div className="policy-detail">
      <div className="detail-header">
        <button className="btn btn-secondary" onClick={() => navigate('/')}>
          ← Back to Registry
        </button>
        <h2>{policy.title}</h2>
      </div>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="detail-content">
        <div className="detail-section">
          <h3>Policy Information</h3>
          <div className="info-grid">
            <div className="info-item">
              <strong>Ministry:</strong> {policy.ministry}
            </div>
            <div className="info-item">
              <strong>Version:</strong> {policy.version}
            </div>
            <div className="info-item">
              <strong>Domain:</strong> {intent.policy_domain || 'N/A'}
            </div>
            <div className="info-item">
              <strong>Effective Period:</strong> {policy.effective_period?.from || 'N/A'} to {policy.effective_period?.to || 'Ongoing'}
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>Extracted Intent</h3>
          <div className="intent-display">
            <div className="intent-group">
              <h4>Target Groups</h4>
              <ul>
                {intent.target_groups?.map((group, idx) => (
                  <li key={idx}>
                    <strong>{group.name}:</strong> {JSON.stringify(group.criteria)}
                  </li>
                ))}
              </ul>
            </div>
            <div className="intent-group">
              <h4>Constraints</h4>
              <ul>
                {intent.constraints?.map((constraint, idx) => (
                  <li key={idx}>
                    <strong>{constraint.type}:</strong> {constraint.metric} ≥ {constraint.threshold}
                    {constraint.applies_to && ` (applies to: ${constraint.applies_to})`}
                  </li>
                ))}
              </ul>
            </div>
            <div className="intent-group">
              <h4>Temporal Rules</h4>
              <p>{JSON.stringify(intent.temporal_rules || {})}</p>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>Implementation Datasets</h3>
          <div className="dataset-actions">
            <label htmlFor="dataset-upload" className="btn btn-primary">
              {uploadingDataset ? 'Uploading...' : 'Upload Dataset (CSV)'}
            </label>
            <input
              id="dataset-upload"
              type="file"
              accept=".csv"
              style={{ display: 'none' }}
              onChange={handleDatasetUpload}
              disabled={uploadingDataset}
            />
          </div>

          {datasets.length === 0 ? (
            <p className="empty-message">No datasets uploaded yet.</p>
          ) : (
            <div className="datasets-list">
              {datasets.map((dataset) => (
                <div key={dataset._id} className="dataset-card">
                  <div className="dataset-info">
                    <strong>Uploaded:</strong> {new Date(dataset.uploaded_at).toLocaleString()}
                    <br />
                    <strong>Time Range:</strong> {dataset.time_range?.start} to {dataset.time_range?.end}
                  </div>
                  <button
                    className="btn btn-primary"
                    onClick={() => handleRunDrift(dataset._id)}
                    disabled={runningDrift}
                  >
                    {runningDrift ? 'Running...' : 'Run Drift Detection'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="detail-section">
          <h3>Policy Intelligence Assistant</h3>
          <PolicyChatbot policyId={policyId} />
        </div>
      </div>
    </div>
  )
}

export default PolicyDetail
