import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

function SetPolicy() {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const navigate = useNavigate()

  const resumeHash = localStorage.getItem('resumeHash')

  useEffect(() => {
    if (resumeHash) {
      loadProfile()
    }
  }, [resumeHash])

  const loadProfile = async () => {
    try {
      const result = await api.getProfile(resumeHash)
      setProfile(result.profile_data)
    } catch (error) {
      setMessage('❌ Please complete your profile first')
    }
  }

  const updateConstraints = (field, value) => {
    setProfile(prev => ({
      ...prev,
      constraints: {
        ...prev.constraints,
        [field]: value
      }
    }))
  }

  const addBlockedCompany = () => {
    const company = prompt('Enter company name to block:')
    if (company && company.trim()) {
      updateConstraints('blocked_companies', [
        ...(profile.constraints?.blocked_companies || []),
        company.trim()
      ])
    }
  }

  const removeBlockedCompany = (index) => {
    const newList = [...(profile.constraints?.blocked_companies || [])]
    newList.splice(index, 1)
    updateConstraints('blocked_companies', newList)
  }

  const handleSave = async () => {
    if (!profile || !resumeHash) {
      setMessage('❌ No profile data to save')
      return
    }

    setLoading(true)
    try {
      const result = await api.saveProfile(resumeHash, profile)
      
      if (result.success) {
        setMessage('✅ Policy saved successfully!')
        setTimeout(() => {
          navigate('/dashboard')
        }, 2000)
      } else {
        setMessage('❌ Failed to save policy')
      }
    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  if (!resumeHash) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <h2>No Resume Found</h2>
        <p>Please upload a resume and complete your profile first.</p>
        <button 
          onClick={() => navigate('/')}
          style={{
            backgroundColor: '#2563eb',
            color: 'white',
            padding: '0.75rem 2rem',
            border: 'none',
            borderRadius: '0.375rem',
            cursor: 'pointer'
          }}
        >
          Start Over
        </button>
      </div>
    )
  }

  if (!profile) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <h2>Loading Profile...</h2>
      </div>
    )
  }

  const constraints = profile.constraints || {}

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <div style={{
        backgroundColor: 'white',
        padding: '2rem',
        borderRadius: '0.5rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ marginTop: 0, color: '#1f2937' }}>Set Application Policy</h2>
        <p style={{ color: '#6b7280', marginBottom: '2rem' }}>
          Configure your application constraints and preferences. These settings control how the autonomous engine behaves.
        </p>

        <div style={{ marginBottom: '2rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#374151' }}>
            Maximum Applications Per Day
          </label>
          <input
            type="number"
            min="1"
            max="50"
            value={constraints.max_apps_per_day || 5}
            onChange={(e) => updateConstraints('max_apps_per_day', parseInt(e.target.value))}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #d1d5db',
              borderRadius: '0.375rem',
              fontSize: '1rem'
            }}
          />
          <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: '0.5rem 0 0 0' }}>
            Recommended: 5-10 applications per day to maintain quality
          </p>
        </div>

        <div style={{ marginBottom: '2rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#374151' }}>
            Minimum Match Score (0.0 - 1.0)
          </label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.1"
            value={constraints.min_match_score || 0.7}
            onChange={(e) => updateConstraints('min_match_score', parseFloat(e.target.value))}
            style={{
              width: '100%',
              padding: '0.75rem',
              border: '1px solid #d1d5db',
              borderRadius: '0.375rem',
              fontSize: '1rem'
            }}
          />
          <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: '0.5rem 0 0 0' }}>
            Only apply to jobs with match score above this threshold. Recommended: 0.6-0.8
          </p>
        </div>

        <div style={{ marginBottom: '2rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#374151' }}>
            Blocked Companies
          </label>
          <div style={{ marginBottom: '1rem' }}>
            {(constraints.blocked_companies || []).map((company, index) => (
              <div key={index} style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.5rem',
                backgroundColor: '#fee2e2',
                borderRadius: '0.375rem',
                marginBottom: '0.5rem'
              }}>
                <span style={{ color: '#991b1b' }}>{company}</span>
                <button
                  onClick={() => removeBlockedCompany(index)}
                  style={{
                    backgroundColor: '#dc2626',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0.25rem',
                    padding: '0.25rem 0.5rem',
                    cursor: 'pointer',
                    fontSize: '0.75rem'
                  }}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
          <button
            onClick={addBlockedCompany}
            style={{
              backgroundColor: '#6b7280',
              color: 'white',
              padding: '0.5rem 1rem',
              border: 'none',
              borderRadius: '0.375rem',
              cursor: 'pointer'
            }}
          >
            Add Blocked Company
          </button>
          <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: '0.5rem 0 0 0' }}>
            Companies you never want to apply to
          </p>
        </div>

        <div style={{
          padding: '1rem',
          backgroundColor: '#dbeafe',
          borderRadius: '0.375rem',
          marginBottom: '2rem'
        }}>
          <h4 style={{ margin: '0 0 0.5rem 0', color: '#1e40af' }}>Current Policy Summary</h4>
          <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#1e40af', fontSize: '0.875rem' }}>
            <li>Apply to max {constraints.max_apps_per_day || 5} jobs per day</li>
            <li>Only apply to jobs with {((constraints.min_match_score || 0.7) * 100).toFixed(0)}%+ match score</li>
            <li>Never apply to {(constraints.blocked_companies || []).length} blocked companies</li>
            <li>All applications use only verified profile data</li>
            <li>All decisions are logged and auditable</li>
          </ul>
        </div>

        <button
          onClick={handleSave}
          disabled={loading}
          style={{
            backgroundColor: loading ? '#9ca3af' : '#2563eb',
            color: 'white',
            padding: '0.75rem 2rem',
            border: 'none',
            borderRadius: '0.375rem',
            fontSize: '1rem',
            cursor: loading ? 'not-allowed' : 'pointer',
            width: '100%'
          }}
        >
          {loading ? 'Saving...' : 'Save Policy & Continue'}
        </button>

        {message && (
          <div style={{
            padding: '1rem',
            borderRadius: '0.375rem',
            backgroundColor: message.includes('✅') ? '#d1fae5' : '#fee2e2',
            color: message.includes('✅') ? '#065f46' : '#991b1b',
            marginTop: '1rem'
          }}>
            {message}
          </div>
        )}
      </div>
    </div>
  )
}

export default SetPolicy