import axios from 'axios'

const API_BASE = '/api'

// Helper to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export const api = {
  // ==================== AUTHENTICATION ====================
  
  // Register user
  register: async (userData) => {
    const response = await axios.post(`${API_BASE}/auth/register`, userData)
    return response.data
  },

  // Login user
  login: async (credentials) => {
    const response = await axios.post(`${API_BASE}/auth/login`, credentials)
    return response.data
  },

  // Logout user
  logout: async () => {
    const response = await axios.post(`${API_BASE}/auth/logout`, {}, {
      headers: getAuthHeaders()
    })
    return response.data
  },

  // ==================== PROFILE & RESUME ====================

  // Upload resume
  uploadResume: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await axios.post(`${API_BASE}/profile/upload-resume`, formData, {
      headers: { 
        'Content-Type': 'multipart/form-data',
        ...getAuthHeaders()
      }
    })
    return response.data
  },

  // Generate draft profile
  generateDraftProfile: async (resumeText, userId) => {
    const response = await axios.post(`${API_BASE}/profile/generate-draft`, {
      resume_text: resumeText,
      user_id: userId
    }, {
      headers: getAuthHeaders()
    })
    return response.data
  },

  // Validate profile
  validateProfile: async (userId, profileData) => {
    const response = await axios.post(`${API_BASE}/profile/validate`, {
      user_id: userId,
      profile_data: profileData
    }, {
      headers: getAuthHeaders()
    })
    return response.data
  },

  // Save profile
  saveProfile: async (userId, profileData) => {
    const response = await axios.post(`${API_BASE}/profile/save`, {
      user_id: userId,
      profile_data: profileData
    }, {
      headers: getAuthHeaders()
    })
    return response.data
  },

  // Get user profile
  getUserProfile: async () => {
    const response = await axios.get(`${API_BASE}/profile/get`, {
      headers: getAuthHeaders()
    })
    return response.data
  },

  // ==================== JOB LISTINGS ====================

  // Get job listings
  getJobListings: async (limit = 50) => {
    const response = await axios.get(`${API_BASE}/jobs/list?limit=${limit}`)
    return response.data
  },

  // Get AI-ranked jobs based on user profile
  getAIRankedJobs: async () => {
    const response = await axios.get(`${API_BASE}/jobs/ai-ranked`, {
      headers: getAuthHeaders()
    })
    return response.data
  },

  // Add job listing (admin)
  addJobListing: async (jobData) => {
    const response = await axios.post(`${API_BASE}/jobs/add`, jobData)
    return response.data
  },

  // ==================== AUTOPILOT ====================

  // Start autopilot (AI-driven job applications)
  startAutopilot: async () => {
    const response = await axios.post(`${API_BASE}/autopilot/start`, {}, {
      headers: getAuthHeaders()
    })
    return response.data
  },

  // Run autopilot (legacy method)
  runAutopilot: async (userId, jobIds = null) => {
    const response = await axios.post(`${API_BASE}/autopilot/run`, {
      user_id: userId,
      job_ids: jobIds
    }, {
      headers: getAuthHeaders()
    })
    return response.data
  },

  // Get autopilot status
  getAutopilotStatus: async (runId) => {
    const response = await axios.get(`${API_BASE}/autopilot/status/${runId}`, {
      headers: getAuthHeaders()
    })
    return response.data
  },

  // ==================== APPLICATION HISTORY ====================

  // Get application history
  getApplicationHistory: async (limit = 100, statusFilter = null) => {
    let url = `${API_BASE}/history/applications?limit=${limit}`
    if (statusFilter) {
      url += `&status_filter=${statusFilter}`
    }
    const response = await axios.get(url, {
      headers: getAuthHeaders()
    })
    return response.data
  },

  // Delete history entry
  deleteHistoryEntry: async (userId, historyId) => {
    const response = await axios.delete(`${API_BASE}/history/delete`, {
      data: { user_id: userId, history_id: historyId },
      headers: getAuthHeaders()
    })
    return response.data
  },

  // ==================== DASHBOARD ====================

  // Get dashboard data
  getDashboard: async () => {
    const response = await axios.get(`${API_BASE}/dashboard`, {
      headers: getAuthHeaders()
    })
    return response.data
  }
}