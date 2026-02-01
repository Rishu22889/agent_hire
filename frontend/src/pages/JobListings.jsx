import { useState, useEffect } from 'react'
import { useAuth } from '../components/AuthContext'
import { api } from '../api'

function JobListings() {
  const [jobsData, setJobsData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [profileStatus, setProfileStatus] = useState(null)
  const [portalStatus, setPortalStatus] = useState(null)
  const { user, isAuthenticated } = useAuth()

  useEffect(() => {
    if (isAuthenticated()) {
      checkProfileAndLoadJobs()
      loadPortalStatus()
      
      // Set up auto-refresh every 10 seconds to catch updates
      const interval = setInterval(() => {
        loadAIRankedJobs()
        loadPortalStatus()
      }, 10000)
      
      return () => clearInterval(interval)
    }
  }, [])

  const checkProfileAndLoadJobs = async () => {
    try {
      // First check if user has a complete profile
      const profileResult = await api.getUserProfile()
      
      if (!profileResult.success || !profileResult.profile) {
        setProfileStatus('missing')
        setLoading(false)
        return
      }

      setProfileStatus('found')
      
      // Load AI-ranked jobs based on profile
      await loadAIRankedJobs()
      
    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`)
      setLoading(false)
    }
  }

  const loadAIRankedJobs = async () => {
    try {
      setMessage('🔄 Refreshing job analysis...')
      
      // This would call the AI job matching service
      const result = await api.getAIRankedJobs()
      
      if (result.success) {
        setJobsData(result.data)
        setMessage('')
      } else {
        setMessage('❌ Failed to load AI-ranked jobs')
      }
    } catch (error) {
      setMessage(`❌ Error loading AI jobs: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const loadPortalStatus = async () => {
    try {
      const response = await fetch('/api/portal/status')
      const result = await response.json()
      
      if (result.success) {
        setPortalStatus(result)
      }
    } catch (error) {
      console.log('Portal status check failed:', error)
      // Don't show error to user - portal integration is optional
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'will_apply': return 'bg-green-500'
      case 'applied': return 'bg-blue-500'
      case 'rejected_by_ai': return 'bg-red-500'
      case 'blocked': return 'bg-gray-500'
      default: return 'bg-gray-400'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'will_apply': return '🎯 Will Apply'
      case 'applied': return '✅ Applied'
      case 'rejected_by_ai': return '❌ AI Rejected'
      case 'blocked': return '🚫 Blocked'
      default: return '⏳ Analyzing'
    }
  }

  if (!isAuthenticated()) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center animate-fade-in-up">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Please log in to view AI job matching</h2>
        </div>
      </div>
    )
  }

  if (profileStatus === 'missing') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="card max-w-2xl animate-fade-in-up">
          <div className="text-center">
            <div className="text-6xl mb-6">📝</div>
            <h2 className="text-3xl font-bold text-gray-800 mb-4">Profile Required</h2>
            <p className="text-gray-600 mb-8 text-lg">
              You need to complete your profile before AI can find and rank jobs for you.
            </p>
            <button
              onClick={() => window.location.href = '/profile'}
              className="btn-primary text-lg px-8 py-4"
            >
              Complete Your Profile →
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center animate-fade-in-up">
          <div className="spinner mx-auto mb-4"></div>
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">🤖 AI is analyzing your profile and finding jobs...</h2>
          <p className="text-gray-500">This may take a few moments</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 pt-4">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="space-y-8 animate-fade-in-up">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gradient mb-4">
              AI Job Matching & Applications 🤖
            </h1>
            <p className="text-xl text-gray-600">
              AI automatically finds, ranks, and applies to jobs based on your profile and preferences.
            </p>
          </div>

      {/* AI Summary Stats */}
      {jobsData && (
        <div className="card-gradient animate-slide-in-right">
          <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
            <span className="mr-3">📊</span>
            AI Job Analysis Summary
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-4xl font-bold text-yellow-200 mb-2">
                {jobsData.summary?.total_found || 0}
              </div>
              <div className="text-white opacity-90">Jobs Found</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-200 mb-2">
                {jobsData.summary?.will_apply || 0}
              </div>
              <div className="text-white opacity-90">Will Apply</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-200 mb-2">
                {jobsData.summary?.applied || 0}
              </div>
              <div className="text-white opacity-90">Applied</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-red-200 mb-2">
                {jobsData.summary?.rejected || 0}
              </div>
              <div className="text-white opacity-90">AI Rejected</div>
            </div>
          </div>
        </div>
      )}

      {/* Portal Integration Status */}
      {portalStatus && (
        <div className={`card ${portalStatus.integration_status?.portal_available ? 'border-green-200 bg-green-50' : 'border-yellow-200 bg-yellow-50'}`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold flex items-center">
              <span className="mr-3">{portalStatus.integration_status?.portal_available ? '🌐✅' : '🌐⚠️'}</span>
              Sandbox Portal (Jobs Source)
            </h3>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              portalStatus.integration_status?.portal_available 
                ? 'bg-green-100 text-green-800' 
                : 'bg-yellow-100 text-yellow-800'
            }`}>
              {portalStatus.integration_status?.portal_available ? 'Active' : 'Offline'}
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <strong>Portal Status:</strong> {portalStatus.integration_status?.portal_available ? '🟢 Active' : '🔴 Offline'}
            </div>
            <div>
              <strong>Available Jobs:</strong> {portalStatus.integration_status?.portal_jobs_count || 0}
            </div>
            <div>
              <strong>Mode:</strong> Portal Only
            </div>
            <div>
              <strong>AI Agent:</strong> {portalStatus.integration_status?.autonomous_agent_active ? '🤖 Active' : '⏸️ Inactive'}
            </div>
          </div>
          {!portalStatus.integration_status?.portal_available && (
            <div className="mt-4 p-3 bg-yellow-100 rounded-lg border border-yellow-300">
              <strong className="text-yellow-800">⚠️ Portal Required:</strong>
              <span className="text-yellow-700 ml-2">
                The sandbox portal must be running for job applications. 
                Start the portal at <code className="bg-yellow-200 px-1 rounded">http://localhost:5001</code> to enable job matching.
              </span>
            </div>
          )}
        </div>
      )}

      {/* Job Listings */}
      {jobsData?.jobs && jobsData.jobs.length > 0 ? (
        <div className="card">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-2xl font-bold text-gray-800 flex items-center">
              <span className="mr-3">💼</span>
              AI-Ranked Jobs ({jobsData.jobs.length} found)
            </h3>
            <button
              onClick={loadAIRankedJobs}
              className="btn-primary"
            >
              🔄 Refresh
            </button>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {jobsData.jobs.map((job) => (
              <div
                key={job.job_id}
                className="card hover:shadow-large transform hover:scale-105 transition-all duration-300"
              >
                {/* Job Header */}
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h4 className="text-xl font-bold text-gray-800 mb-2">{job.role}</h4>
                    <p className="text-blue-600 font-semibold mb-1">{job.company}</p>
                    <p className="text-gray-500 text-sm">{job.location}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-white text-sm font-medium ${getStatusColor(job.status)}`}>
                    {getStatusText(job.status)}
                  </span>
                </div>

                {/* AI Match Score */}
                <div className="mb-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">AI Match Score</span>
                    <span className={`text-sm font-bold ${
                      job.match_score >= 0.8 ? 'text-green-600' : 
                      job.match_score >= 0.6 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {Math.round(job.match_score * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-500 ${
                        job.match_score >= 0.8 ? 'bg-green-500' : 
                        job.match_score >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${job.match_score * 100}%` }}
                    />
                  </div>
                </div>

                {/* Skills Match */}
                <div className="mb-4">
                  <div className="flex flex-wrap gap-2">
                    {job.matched_skills?.slice(0, 4).map((skill, index) => (
                      <span
                        key={index}
                        className="badge-success"
                      >
                        ✓ {skill}
                      </span>
                    ))}
                    {job.matched_skills?.length > 4 && (
                      <span className="text-gray-500 text-sm">
                        +{job.matched_skills.length - 4} more matches
                      </span>
                    )}
                  </div>
                </div>

                {/* AI Reasoning */}
                {job.ai_reasoning && (
                  <div className="bg-gray-50 p-3 rounded-lg mb-4">
                    <p className="text-sm text-gray-700">
                      <strong className="text-gray-800">AI Decision:</strong> {job.ai_reasoning}
                    </p>
                  </div>
                )}

                {/* Job Details */}
                <div className="flex justify-between items-center text-sm text-gray-500 pt-4 border-t border-gray-100">
                  <span>{job.min_experience_years} years exp</span>
                  <span className="capitalize">{job.job_type}</span>
                  {job.salary_range && <span>{job.salary_range}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="card text-center py-12">
          <div className="text-6xl mb-6">🔍</div>
          <h3 className="text-2xl font-bold text-gray-800 mb-4">No jobs found yet</h3>
          <p className="text-gray-600 mb-8">AI is still searching for jobs that match your profile. Check back soon!</p>
          <button
            onClick={loadAIRankedJobs}
            className="btn-primary"
          >
            🔄 Refresh Search
          </button>
        </div>
      )}

      {message && (
        <div className={`p-4 rounded-xl font-medium ${
          message.includes('✅') 
            ? 'bg-green-100 text-green-800 border border-green-200' 
            : message.includes('🤖') || message.includes('🚀') || message.includes('🔄')
            ? 'bg-blue-100 text-blue-800 border border-blue-200'
            : 'bg-red-100 text-red-800 border border-red-200'
        }`}>
          {message}
          {message.includes('completed') && (
            <div className="mt-4">
              <button
                onClick={() => window.location.href = '/dashboard'}
                className="btn-success"
              >
                📊 View Application History in Dashboard
              </button>
            </div>
          )}
        </div>
      )}
        </div>
      </div>
    </div>
  )
}

export default JobListings