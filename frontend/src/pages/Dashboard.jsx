import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { api } from '../api'

function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [selectedRun, setSelectedRun] = useState(null)
  const [applicationHistory, setApplicationHistory] = useState([])
  const [historyFilter, setHistoryFilter] = useState('')
  const [portalStatus, setPortalStatus] = useState(null)
  const { user, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isAuthenticated()) {
      loadDashboard()
      loadApplicationHistory()
      loadPortalStatus()
      // Refresh every 3 seconds for more responsive updates during autonomous runs
      const interval = setInterval(() => {
        loadDashboard()
        loadApplicationHistory()
        loadPortalStatus()
      }, 3000)
      return () => clearInterval(interval)
    }
  }, [])

  const loadDashboard = async () => {
    try {
      const result = await api.getDashboard()
      if (result.success) {
        setDashboardData(result)
        
        // Auto-select the most recent run
        if (result.recent_runs.length > 0 && !selectedRun) {
          setSelectedRun(result.recent_runs[0])
        }
      }
    } catch (error) {
      setMessage('❌ Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const loadApplicationHistory = async (filter = null) => {
    try {
      const filterValue = filter !== null ? filter : historyFilter
      const result = await api.getApplicationHistory(100, filterValue || null)
      if (result.success) {
        setApplicationHistory(result.history)
      }
    } catch (error) {
      console.error('Failed to load application history:', error)
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

  const handleRunSelect = (run) => {
    setSelectedRun(run)
  }

  const deleteHistoryEntry = async (historyId) => {
    if (!confirm('Are you sure you want to delete this history entry? This will not affect backend safety logs.')) {
      return
    }

    try {
      await api.deleteHistoryEntry(user.id, historyId)
      loadApplicationHistory() // Refresh the list
      setMessage('✅ History entry deleted')
      setTimeout(() => setMessage(''), 3000)
    } catch (error) {
      setMessage('❌ Failed to delete history entry')
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      'running': '#f59e0b',
      'completed': '#059669',
      'failed': '#dc2626',
      'queued': '#6b7280',
      'skipped': '#f59e0b',
      'submitted': '#059669',
      'retried': '#2563eb'
    }
    return colors[status] || '#6b7280'
  }

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A'
    
    // Handle string dates (autonomous runs format: "2026-02-01 15:16:08")
    if (typeof timestamp === 'string') {
      return new Date(timestamp).toLocaleString()
    } 
    // Handle Unix timestamps (application history format: 1769958968.0729868)
    else if (typeof timestamp === 'number') {
      return new Date(timestamp * 1000).toLocaleString()
    }
    
    return 'Invalid Date'
  }

  if (!isAuthenticated()) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center animate-fade-in-up">
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Please log in to view your dashboard</h2>
          <button 
            onClick={() => navigate('/login')}
            className="btn-primary"
          >
            Go to Login
          </button>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center animate-fade-in-up">
          <div className="spinner mx-auto mb-4"></div>
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">Loading Dashboard...</h2>
          <p className="text-gray-500">Preparing your workspace</p>
        </div>
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center animate-fade-in-up card max-w-md">
          <div className="text-6xl mb-6">🚀</div>
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Welcome to Your Dashboard</h2>
          <p className="text-gray-600 mb-8">Complete your profile to see AI job applications here.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={() => navigate('/upload-resume')}
              className="btn-primary"
            >
              📄 Upload Resume
            </button>
            <button 
              onClick={() => navigate('/jobs')}
              className="btn-success"
            >
              💼 Browse Jobs
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 pt-4">
      <div className="space-y-8 animate-fade-in-up max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gradient mb-4">
          Welcome back, {user?.email?.split('@')[0]}! 👋
        </h1>
        <p className="text-xl text-gray-600">
          Your AI-powered job application dashboard
        </p>
      </div>
      
      {/* Profile Summary Card */}
      <div className="card-gradient animate-slide-in-right">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold text-white flex items-center">
            <span className="mr-3">👤</span>
            Profile Summary
          </h3>
          <button
            onClick={() => navigate('/profile')}
            className="bg-white bg-opacity-20 hover:bg-opacity-30 text-gray-800 px-4 py-2 rounded-xl font-medium transition-all duration-300"
          >
            Edit Profile
          </button>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-200">
              {dashboardData.user_profile?.student_id ? '✅' : '❌'}
            </div>
            <div className="text-white opacity-90 text-sm mt-1">Profile Status</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-200">
              {dashboardData.user_profile?.profile_data?.skill_vocab?.length || 0}
            </div>
            <div className="text-white opacity-90 text-sm mt-1">Skills</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-200">
              {dashboardData.user_profile?.profile_data?.projects?.length || 0}
            </div>
            <div className="text-white opacity-90 text-sm mt-1">Projects</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-200">
              {dashboardData.user_profile?.profile_data?.education?.length || 0}
            </div>
            <div className="text-white opacity-90 text-sm mt-1">Education</div>
          </div>
        </div>
        
        {!dashboardData.user_profile && (
          <div className="mt-6 p-4 bg-yellow-100 bg-opacity-20 rounded-xl border border-yellow-200 border-opacity-30">
            <p className="text-yellow-100 text-center">
              <strong>📝 No Profile Found:</strong> Create your profile to start applying to jobs.
            </p>
          </div>
        )}
      </div>

      {/* Application Stats */}
      {dashboardData.application_stats && Object.keys(dashboardData.application_stats).length > 0 && (
        <div className="card">
          <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
            <span className="mr-3">📊</span>
            Application Statistics
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {Object.entries(dashboardData.application_stats).map(([status, count]) => (
              <div key={status} className="text-center p-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl">
                <div className="text-4xl font-bold mb-2" style={{ color: getStatusColor(status) }}>
                  {count}
                </div>
                <div className="text-gray-600 font-medium capitalize">
                  {status.replace('_', ' ')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Portal Status */}
      {portalStatus && (
        <div className={`card ${portalStatus.integration_status?.portal_available ? 'border-green-200 bg-green-50' : 'border-yellow-200 bg-yellow-50'}`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold flex items-center">
              <span className="mr-3">{portalStatus.integration_status?.portal_available ? '🌐✅' : '🌐⚠️'}</span>
              Sandbox Portal Status
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
              <strong>Available Jobs:</strong> {portalStatus.integration_status?.portal_jobs_count || 0}
            </div>
            <div>
              <strong>Mode:</strong> Portal Only
            </div>
            <div>
              <strong>AI Agent:</strong> {portalStatus.integration_status?.autonomous_agent_active ? '🤖 Active' : '⏸️ Inactive'}
            </div>
            <div>
              <strong>Status:</strong> {portalStatus.integration_status?.portal_available ? '🟢 Online' : '🔴 Offline'}
            </div>
          </div>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Recent Runs */}
        <div className="lg:col-span-1">
          <div className="card h-fit">
            <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
              <span className="mr-3">🤖</span>
              Recent AI Runs
            </h3>
            
            {dashboardData.recent_runs.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-6xl mb-4">🎯</div>
                <p className="text-gray-500 mb-4">No AI application runs yet</p>
                <button
                  onClick={() => navigate('/jobs')}
                  className="btn-primary"
                >
                  Browse Jobs
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {dashboardData.recent_runs.map((run) => (
                  <div
                    key={run.run_id}
                    onClick={() => handleRunSelect(run)}
                    className={`p-4 rounded-xl cursor-pointer transition-all duration-300 transform hover:scale-105 ${
                      selectedRun?.run_id === run.run_id 
                        ? 'bg-blue-50 border-2 border-blue-300 shadow-lg' 
                        : 'bg-gray-50 border border-gray-200 hover:shadow-md'
                    }`}
                  >
                    <div className="flex justify-between items-center mb-2">
                      <strong className="text-gray-800">Run #{run.run_id}</strong>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium text-white`}
                            style={{ backgroundColor: getStatusColor(run.status) }}>
                        {run.status.toUpperCase()}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 mb-2">
                      {formatTimestamp(run.started_at)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {run.job_ids.length} jobs processed
                    </div>
                    {run.summary_data && Object.keys(run.summary_data).length > 0 && (
                      <div className="text-xs text-gray-600 mt-2 flex flex-wrap gap-2">
                        {Object.entries(run.summary_data).map(([key, value]) => (
                          <span key={key} className="bg-white px-2 py-1 rounded">
                            {key}: {value}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Application History */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
              <h3 className="text-xl font-bold text-gray-800 flex items-center">
                <span className="mr-3">📋</span>
                Application History
              </h3>
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    loadDashboard()
                    loadApplicationHistory()
                  }}
                  className="btn-primary text-sm px-4 py-2"
                >
                  🔄 Refresh
                </button>
                <select
                  value={historyFilter}
                  onChange={(e) => {
                    const newFilter = e.target.value
                    setHistoryFilter(newFilter)
                    loadApplicationHistory(newFilter)
                  }}
                  className="input-modern text-sm"
                >
                  <option value="">All Status</option>
                  <option value="submitted">Submitted</option>
                  <option value="skipped">Skipped</option>
                  <option value="failed">Failed</option>
                  <option value="retried">Retried</option>
                </select>
              </div>
            </div>
            
            {applicationHistory.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📝</div>
                <p className="text-gray-500 mb-2">No application history found</p>
                {historyFilter && <p className="text-gray-400 text-sm">Try changing the filter or complete your profile first</p>}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <div className="max-h-96 overflow-y-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Company</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Role</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Time</th>
                        <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {applicationHistory.map((app) => (
                        <tr key={app.id} className="hover:bg-gray-50 transition-colors duration-200">
                          <td className="px-4 py-3 font-semibold text-gray-800">{app.company}</td>
                          <td className="px-4 py-3 text-gray-600">{app.role}</td>
                          <td className="px-4 py-3">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium text-white`}
                                  style={{ backgroundColor: getStatusColor(app.status) }}>
                              {app.status.toUpperCase()}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-500">
                            {formatTimestamp(app.timestamp)}
                          </td>
                          <td className="px-4 py-3">
                            <button
                              onClick={() => deleteHistoryEntry(app.id)}
                              className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg text-xs font-medium transition-colors duration-200"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center">
          <span className="mr-3">⚡</span>
          Quick Actions
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/upload-resume')}
            className="btn-primary flex items-center justify-center"
          >
            <span className="mr-2">📄</span>
            Upload New Resume
          </button>
          <button
            onClick={() => navigate('/profile')}
            className="btn-success flex items-center justify-center"
          >
            <span className="mr-2">✏️</span>
            Edit Profile
          </button>
          <button
            onClick={() => navigate('/jobs')}
            className="btn-secondary flex items-center justify-center"
          >
            <span className="mr-2">🔍</span>
            Browse Jobs
          </button>
        </div>
      </div>

      {message && (
        <div className={`p-4 rounded-xl font-medium ${
          message.includes('✅') 
            ? 'bg-green-100 text-green-800 border border-green-200' 
            : 'bg-red-100 text-red-800 border border-red-200'
        }`}>
          {message}
        </div>
      )}
      </div>
    </div>
  )
}

export default Dashboard