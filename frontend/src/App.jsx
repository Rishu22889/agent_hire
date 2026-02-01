import React from 'react'
import { Routes, Route, Link, useLocation, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './components/AuthContext'
import Login from './pages/Login'
import Register from './pages/Register'
import UploadResume from './pages/UploadResume'
import EditProfile from './pages/EditProfile'
import JobListings from './pages/JobListings'
import SetPolicy from './pages/SetPolicy'
import Dashboard from './pages/Dashboard'

function Navigation() {
  const location = useLocation()
  const { user, logout, isAuthenticated } = useAuth()

  if (!isAuthenticated()) {
    return null
  }

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/upload-resume', label: 'Upload Resume', icon: '📄' },
    { path: '/profile', label: 'Edit Profile', icon: '👤' },
    { path: '/jobs', label: 'Job Listings', icon: '💼' }
  ]

  return (
    <nav className="gradient-primary shadow-large sticky top-0 z-50 mb-0">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <h1 className="text-2xl font-bold text-white flex items-center space-x-2">
                <span className="text-3xl">🤖</span>
                <span className="text-white font-bold">
                  AgentHire
                </span>
              </h1>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              {navItems.map(({ path, label, icon }) => (
                <Link
                  key={path}
                  to={path}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 transform hover:scale-105 ${
                    location.pathname === path
                      ? 'bg-white bg-opacity-25 text-gray-800 shadow-lg font-bold'
                      : 'text-gray-100 hover:bg-white hover:bg-opacity-15 hover:text-gray-800 font-semibold'
                  }`}
                >
                  <span className="mr-2">{icon}</span>
                  {label}
                </Link>
              ))}
            </div>
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            <div className="text-white text-sm font-medium">
              <span className="opacity-90">Welcome,</span>
              <span className="ml-1 font-bold text-white">{user?.name?.split('@')[0]}</span>
            </div>
            <button
              onClick={logout}
              className="bg-white bg-opacity-25 hover:bg-opacity-35 text-gray-800 px-4 py-2 rounded-xl text-sm font-bold transition-all duration-300 transform hover:scale-105 shadow-lg border border-white border-opacity-30"
            >
              Sign Out
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="md:hidden">
        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-black bg-opacity-10">
          {navItems.map(({ path, label, icon }) => (
            <Link
              key={path}
              to={path}
              className={`block px-3 py-2 rounded-xl text-base font-medium transition-all duration-300 ${
                location.pathname === path
                  ? 'bg-white bg-opacity-25 text-gray-800 font-bold'
                  : 'text-gray-100 hover:bg-white hover:bg-opacity-15 hover:text-gray-800 font-semibold'
              }`}
            >
              <span className="mr-2">{icon}</span>
              {label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  )
}

function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="text-center animate-fade-in-up">
          <div className="spinner mx-auto mb-4"></div>
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">Loading...</h2>
          <p className="text-gray-500">Preparing your workspace</p>
        </div>
      </div>
    )
  }
  
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }
  
  return children
}

function AppContent() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <Navigation />
      
      <main>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected routes */}
          <Route path="/upload-resume" element={
            <ProtectedRoute>
              <UploadResume />
            </ProtectedRoute>
          } />
          <Route path="/profile" element={
            <ProtectedRoute>
              <EditProfile />
            </ProtectedRoute>
          } />
          <Route path="/jobs" element={
            <ProtectedRoute>
              <JobListings />
            </ProtectedRoute>
          } />
          <Route path="/policy" element={
            <ProtectedRoute>
              <SetPolicy />
            </ProtectedRoute>
          } />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          
          {/* Default redirects */}
          <Route path="/" element={
            isAuthenticated() ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />
          } />
        </Routes>
      </main>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App