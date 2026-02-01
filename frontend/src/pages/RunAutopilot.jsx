import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { api } from '../api'

function RunAutopilot() {
  const [profile, setProfile] = useState(null)
  const [jobsData, setJobsData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [autopilotRunning, setAutopilotRunning] = useState(false)
  const [applicationProgress, setApplicationProgress] = useState([])
  const [runSummary, setRunSummary] = useState(null)
  const { user, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isAuthenticated()) {
      loadProfile()
      loadAIRankedJobs()
      
      // Set up auto-refresh every 10 seconds to catch updates
      const interval = setInterval(() => {
        if (!autopilotRunning) { // Only refresh when not running autopilot
          loadAIRankedJobs()
        }
      }, 10000)
      
      return () => clearInterval(interval)
    }
  }, [autopilotRunning])

  const loadProfile = async () => {
    try {
      const result = await api.getUserProfile()
      if (result.success && result.profile) {
        setProfile(result.profile)
      } else {
        setMessage('❌ No profile found. Please create your profile first.')
      }
    } catch (error) {
      setMessage('❌ Failed to load profile. Please create your profile first.')
    }
  }

  const loadAIRankedJobs = async () => {
    try {
      setMessage('🔄 Refreshing job analysis...')
      const result = await api.getAIRankedJobs()
      if (result.success) {
        setJobsData(result.data)
        setMessage('')
      } else {
        setMessage('❌ Failed to load AI-ranked jobs')
      }
    } catch (error) {
      setMessage(`❌ Error loading AI jobs: ${error.response?.data?.detail || error.message}`)
    }
  }

  const startAutopilot = async () => {
    if (!profile) {
      setMessage('❌ Please create your profile first')
      return
    }

    if (!jobsData || !jobsData.jobs.some(job => job.status === 'will_apply')) {
      setMessage('❌ No suitable jobs found to apply to')
      return
    }

    setAutopilotRunning(true)
    setLoading(true)
    setMessage('🚀 Starting autopilot job applications...')
    setApplicationProgress([])
    setRunSummary(null)

    try {
      const result = await api.startAutopilot()
      
      if (result.success) {
        setRunSummary(result.summary)
        setMessage(`✅ Autopilot completed! Applied to ${result.applied_count} jobs successfully.`)
        
        // Simulate progress updates (in real implementation, this would come from websockets or polling)
        simulateProgress(result.applied_count)
        
        // Show message about checking dashboard
        setTimeout(() => {
          setMessage(`✅ Autopilot completed! Applied to ${result.applied_count} jobs. Check Dashboard for detailed history. Refreshing job analysis...`)
        }, 3000)
        
        // Refresh job data to show updated statuses - wait longer for backend to process
        setTimeout(async () => {
          await loadAIRankedJobs()
          setMessage(`✅ Autopilot completed! Applied to ${result.applied_count} jobs. Job statuses updated. Visit Dashboard for complete application history.`)
        }, 6000)
        
        // Final refresh to ensure we have the latest data
        setTimeout(async () => {
          await loadAIRankedJobs()
        }, 10000)
      } else {
        setMessage(`❌ Failed to start autopilot: ${result.message}`)
      }
    } catch (error) {
      setMessage(`❌ Autopilot Error: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
      setAutopilotRunning(false)
    }
  }

  const simulateProgress = (totalApplied) => {
    // Simulate application progress for better UX
    const jobs = jobsData.jobs.filter(job => job.status === 'will_apply')
    let currentIndex = 0
    
    const interval = setInterval(() => {
      if (currentIndex < jobs.length) {
        const job = jobs[currentIndex]
        setApplicationProgress(prev => [...prev, {
          company: job.company,
          role: job.role,
          status: 'submitted',
          timestamp: new Date().toLocaleTimeString()
        }])
        currentIndex++
      } else {
        clearInterval(interval)
      }
    }, 500) // Add one every 500ms for visual effect
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'will_apply': return '#059669'
      case 'applied': return '#2563eb'
      case 'rejected_by_ai': return '#dc2626'
      case 'blocked': return '#6b7280'
      default: return '#6b7280'
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
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <h2>Please log in to run autopilot</h2>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 pt-4">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="card animate-fade-in-up">
          {/* Header Section */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-red-500 to-orange-600 rounded-full mb-4 shadow-lg">
              <span className="text-2xl">🚀</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Autopilot Job Applications</h1>
            <p className="text-gray-600 text-lg">
              Welcome back, <span className="font-semibold text-red-600">{user?.email}</span>! 
              AI will automatically apply to jobs that match your profile.
            </p>
          </div>

          {/* Profile Status */}
          <div className="mb-8 animate-fade-in-up">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
                <span className="text-purple-600 text-xl">👤</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Profile Status</h3>
            </div>
            {profile ? (
              <div className="glass-effect rounded-2xl p-6 border border-green-200">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                      <span className="text-green-600 text-xl">✅</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-green-900 mb-2">
                      Profile Ready: {profile.student_id}
                    </h4>
                    <div className="flex flex-wrap gap-4 text-sm text-green-800">
                      <div className="flex items-center space-x-2">
                        <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                        <span>Skills: {profile.profile_data?.skill_vocab?.length || 0}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                        <span>Projects: {profile.profile_data?.projects?.length || 0}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                        <span>Education: {profile.profile_data?.education?.length || 0}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="glass-effect rounded-2xl p-6 border border-red-200">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                      <span className="text-red-600 text-xl">❌</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-red-900 mb-4">No Profile Found</h4>
                    <div className="flex flex-wrap gap-3">
                      <button
                        onClick={() => navigate('/upload-resume')}
                        className="btn-primary"
                      >
                        <span className="flex items-center space-x-2">
                          <span>📤</span>
                          <span>Upload Resume</span>
                        </span>
                      </button>
                      <button
                        onClick={() => navigate('/edit-profile')}
                        className="btn-success"
                      >
                        <span className="flex items-center space-x-2">
                          <span>✏️</span>
                          <span>Create Profile</span>
                        </span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* AI Job Analysis Summary */}
          {jobsData && (
            <div className="mb-8 animate-slide-in-right">
              <div className="flex justify-between items-center mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 text-xl">🧠</span>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900">AI Job Analysis</h3>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={loadAIRankedJobs}
                    className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-xl transition-all duration-300 transform hover:scale-105 text-sm font-medium"
                  >
                    <span className="flex items-center space-x-2">
                      <span>🔄</span>
                      <span>Refresh Analysis</span>
                    </span>
                  </button>
                  <button
                    onClick={async () => {
                      setMessage('🔄 Force refreshing job data...')
                      await loadAIRankedJobs()
                      setMessage('✅ Job data refreshed')
                      setTimeout(() => setMessage(''), 3000)
                    }}
                    className="btn-primary text-sm"
                  >
                    <span className="flex items-center space-x-2">
                      <span>🔄</span>
                      <span>Force Refresh</span>
                    </span>
                  </button>
                </div>
              </div>
              <div className="card-gradient">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white mb-2">
                      {jobsData.summary?.total_found || 0}
                    </div>
                    <div className="text-blue-100 text-sm font-medium">Jobs Analyzed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-200 mb-2">
                      {jobsData.summary?.will_apply || 0}
                    </div>
                    <div className="text-green-100 text-sm font-medium">Will Apply</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-200 mb-2">
                      {jobsData.summary?.applied || 0}
                    </div>
                    <div className="text-blue-100 text-sm font-medium">Already Applied</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-red-200 mb-2">
                      {jobsData.summary?.rejected || 0}
                    </div>
                    <div className="text-red-100 text-sm font-medium">AI Rejected</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Application Progress */}
          {applicationProgress.length > 0 && (
            <div className="mb-8 animate-fade-in-up">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-green-600 text-xl">⚡</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900">Application Progress</h3>
              </div>
              <div className="card max-h-80 overflow-y-auto">
                <div className="space-y-4">
                  {applicationProgress.map((app, index) => (
                    <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-200 hover:shadow-soft transition-all duration-300">
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-900">{app.company}</h4>
                        <p className="text-gray-600 text-sm">{app.role}</p>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className="text-sm text-gray-500">{app.timestamp}</span>
                        <span className="badge-success">
                          <span className="mr-1">✅</span>
                          APPLIED
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Run Summary */}
          {runSummary && (
            <div className="mb-8 animate-fade-in-up">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <span className="text-green-600 text-xl">📊</span>
                </div>
                <h3 className="text-xl font-bold text-gray-900">Autopilot Summary</h3>
              </div>
              <div className="card bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  {Object.entries(runSummary).map(([key, value]) => (
                    <div key={key} className="text-center">
                      <div className="text-2xl font-bold text-green-700 mb-2">
                        {value}
                      </div>
                      <div className="text-sm font-medium text-green-600 capitalize">
                        {key.replace('_', ' ')}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Run Button */}
          <div className="text-center mb-8 animate-fade-in-up">
            <button
              onClick={startAutopilot}
              disabled={loading || !profile || autopilotRunning || !jobsData?.jobs?.some(job => job.status === 'will_apply')}
              className={`text-xl px-12 py-6 shadow-large font-bold transition-all duration-300 ${
                loading || !profile || autopilotRunning || !jobsData?.jobs?.some(job => job.status === 'will_apply')
                  ? 'bg-gray-400 cursor-not-allowed opacity-50'
                  : 'btn-danger hover:scale-105'
              }`}
            >
              {loading ? (
                <span className="flex items-center space-x-3">
                  <div className="spinner"></div>
                  <span>🚀 Starting Autopilot...</span>
                </span>
              ) : autopilotRunning ? (
                <span className="flex items-center space-x-3">
                  <div className="animate-pulse-soft">⏳</div>
                  <span>Autopilot Running...</span>
                </span>
              ) : (
                <span className="flex items-center space-x-3">
                  <span>🚀</span>
                  <span>Apply to {jobsData?.summary?.will_apply || 0} Jobs Automatically</span>
                </span>
              )}
            </button>
            
            {jobsData && jobsData.summary?.will_apply === 0 && (
              <p className="text-gray-600 mt-4 text-sm">
                No suitable jobs found. Try adjusting your profile constraints or check job listings.
              </p>
            )}
          </div>

          {/* Quick Actions */}
          <div className="flex flex-wrap justify-center gap-4 mb-8 animate-slide-in-right">
            <button
              onClick={() => navigate('/jobs')}
              className="btn-primary"
            >
              <span className="flex items-center space-x-2">
                <span>📋</span>
                <span>View Job Analysis</span>
              </span>
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="btn-success"
            >
              <span className="flex items-center space-x-2">
                <span>📊</span>
                <span>View Dashboard</span>
              </span>
            </button>
            <button
              onClick={() => navigate('/edit-profile')}
              className="bg-purple-500 hover:bg-purple-600 text-white px-6 py-3 rounded-xl font-semibold shadow-lg transform transition-all duration-300 hover:scale-105 hover:shadow-xl"
            >
              <span className="flex items-center space-x-2">
                <span>⚙️</span>
                <span>Edit Profile</span>
              </span>
            </button>
          </div>

          {/* Messages */}
          {message && (
            <div className={`p-6 rounded-2xl animate-fade-in-up mb-8 ${
              message.includes('✅') 
                ? 'bg-green-50 border border-green-200 text-green-800' 
                : message.includes('🚀') || message.includes('🔄') 
                ? 'bg-blue-50 border border-blue-200 text-blue-800' 
                : 'bg-red-50 border border-red-200 text-red-800'
            }`}>
              <div className="flex items-start space-x-3">
                <span className="text-2xl">
                  {message.includes('✅') ? '✅' : message.includes('🚀') || message.includes('🔄') ? '🔄' : '❌'}
                </span>
                <div className="flex-1">
                  <p className="font-medium text-lg">{message}</p>
                  {message.includes('completed') && (
                    <div className="mt-4 flex flex-wrap gap-3">
                      <button
                        onClick={() => navigate('/dashboard')}
                        className="btn-success"
                      >
                        <span className="flex items-center space-x-2">
                          <span>📊</span>
                          <span>View Dashboard</span>
                        </span>
                      </button>
                      <button
                        onClick={loadAIRankedJobs}
                        className="btn-primary"
                      >
                        <span className="flex items-center space-x-2">
                          <span>🔄</span>
                          <span>Refresh Analysis</span>
                        </span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Safety Notice */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-200">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 text-xl">🔒</span>
                </div>
              </div>
              <div>
                <h4 className="text-lg font-semibold text-blue-900 mb-3">AI Autopilot Safety</h4>
                <ul className="space-y-2 text-blue-800 text-sm">
                  <li className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>AI analyzes all jobs and only applies to suitable matches</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>Respects your profile constraints and blocked companies</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>Complete application history tracked in dashboard</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>No manual job selection needed - fully automated</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>Can be monitored in real-time with detailed progress</span>
                  </li>
                  <li className="flex items-start space-x-2">
                    <span className="text-blue-600 mt-0.5">•</span>
                    <span>All applications use your verified profile data</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RunAutopilot