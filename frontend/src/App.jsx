import React from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import PolicyRegistry from './pages/PolicyRegistry'
import PolicyDetail from './pages/PolicyDetail'
import DriftDashboard from './pages/DriftDashboard'
import './App.css'

function App() {
  const location = useLocation()

  return (
    <div className="app">
      <header className="header">
        <h1>PolicyLens</h1>
        <p>NLP-Driven Detection of Policy–Implementation Drift</p>
      </header>

      <nav className="navbar">
        <Link 
          to="/" 
          className={location.pathname === '/' ? 'nav-link active' : 'nav-link'}
        >
          Policy Registry
        </Link>
        <Link 
          to="/drift" 
          className={location.pathname === '/drift' ? 'nav-link active' : 'nav-link'}
        >
          Drift Dashboard
        </Link>
      </nav>

      <div className="container">
        <Routes>
          <Route path="/" element={<PolicyRegistry />} />
          <Route path="/policy/:policyId" element={<PolicyDetail />} />
          <Route path="/drift" element={<DriftDashboard />} />
        </Routes>
      </div>
    </div>
  )
}

export default App
