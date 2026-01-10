import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import './PolicyRegistry.css'

const API_BASE = 'http://localhost:8000'

function PolicyRegistry() {
  const [policies, setPolicies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [deleting, setDeleting] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    loadPolicies()
  }, [])

  const loadPolicies = async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${API_BASE}/policies`)
      setPolicies(response.data.policies || [])
      setError(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load policies')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    try {
      setUploading(true)
      setError(null)
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', file.name.replace('.pdf', '').replace('.txt', ''))
      formData.append('ministry', 'General')

      const response = await axios.post(`${API_BASE}/policies/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      await loadPolicies()
      navigate(`/policy/${response.data.policy_id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload policy')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (policyId, e) => {
    e.stopPropagation() // Prevent navigation when clicking delete
    
    if (!window.confirm('Are you sure you want to delete this policy? This will also delete all associated datasets, drift results, and chat sessions.')) {
      return
    }

    try {
      setDeleting(policyId)
      setError(null)
      await axios.delete(`${API_BASE}/policies/${policyId}`)
      await loadPolicies()
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete policy')
    } finally {
      setDeleting(null)
    }
  }

  if (loading) {
    return <div className="loading">Loading policies...</div>
  }

  return (
    <div className="policy-registry">
      <div className="registry-header">
        <h2>Policy Registry</h2>
        <div>
          <label htmlFor="policy-upload" className="btn btn-primary">
            {uploading ? 'Uploading...' : 'Upload Policy'}
          </label>
          <input
            id="policy-upload"
            type="file"
            accept=".pdf,.txt"
            style={{ display: 'none' }}
            onChange={handleFileUpload}
            disabled={uploading}
          />
        </div>
      </div>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {policies.length === 0 ? (
        <div className="empty-state">
          <p>No policies uploaded yet.</p>
          <p>Upload a PDF or TXT policy document to get started.</p>
        </div>
      ) : (
        <div className="policies-grid">
          {policies.map((policy) => (
            <div
              key={policy._id}
              className="policy-card"
            >
              <div className="policy-card-header">
                <h3 onClick={() => navigate(`/policy/${policy._id}`)}>{policy.title}</h3>
                <button
                  className="btn-delete"
                  onClick={(e) => handleDelete(policy._id, e)}
                  disabled={deleting === policy._id}
                  title="Delete policy"
                >
                  {deleting === policy._id ? 'Deleting...' : '🗑️'}
                </button>
              </div>
              <div 
                className="policy-card-content"
                onClick={() => navigate(`/policy/${policy._id}`)}
              >
                <div className="policy-meta">
                  <span className="meta-item">
                    <strong>Ministry:</strong> {policy.ministry}
                  </span>
                  <span className="meta-item">
                    <strong>Version:</strong> {policy.version}
                  </span>
                  <span className="meta-item">
                    <strong>Domain:</strong> {policy.extracted_intent?.policy_domain || 'N/A'}
                  </span>
                </div>
                <div className="policy-intent-preview">
                  <strong>Extracted Intent:</strong>
                  <ul>
                    <li>Target Groups: {policy.extracted_intent?.target_groups?.length || 0}</li>
                    <li>Constraints: {policy.extracted_intent?.constraints?.length || 0}</li>
                  </ul>
                </div>
              </div>
              <div className="policy-footer">
                <span className="policy-date">
                  Created: {new Date(policy.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default PolicyRegistry
