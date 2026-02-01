import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'
import { api } from '../api'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!email || !password) {
      setMessage('Please fill in all fields')
      return
    }

    setLoading(true)
    setMessage('')

    try {
      const result = await api.login({ email, password })
      
      if (result.success) {
        login(result)
        setMessage('✅ Login successful!')
        
        // Redirect to dashboard after successful login
        setTimeout(() => {
          navigate('/dashboard')
        }, 1000)
      } else {
        setMessage(`❌ ${result.message}`)
      }
    } catch (error) {
      setMessage(`❌ Login failed: ${error.response?.data?.detail || error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 px-4">
      <div className="w-full max-w-md">
        {/* Main Login Card */}
        <div className="card animate-fade-in-up">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">🤖</div>
            <h1 className="text-3xl font-bold text-gradient mb-2">
              AI Job Engine
            </h1>
            <p className="text-gray-600">
              Sign in to your account
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                className="input-modern"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="input-modern"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 px-4 rounded-xl font-semibold text-white transition-all duration-300 transform ${
                loading 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'btn-primary hover:scale-105'
              }`}
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <div className="spinner mr-2"></div>
                  Signing In...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="my-8 border-t border-gray-200"></div>

          {/* Sign Up Link */}
          <div className="text-center">
            <p className="text-gray-600 mb-4">
              Don't have an account?
            </p>
            <Link
              to="/register"
              className="inline-flex items-center px-6 py-3 border-2 border-blue-500 text-blue-500 font-semibold rounded-xl hover:bg-blue-500 hover:text-white transition-all duration-300 transform hover:scale-105"
            >
              Create Account →
            </Link>
          </div>

          {/* Message */}
          {message && (
            <div className={`mt-6 p-4 rounded-xl font-medium text-center ${
              message.includes('✅') 
                ? 'bg-green-100 text-green-800 border border-green-200' 
                : 'bg-red-100 text-red-800 border border-red-200'
            }`}>
              {message}
            </div>
          )}
        </div>

        {/* Features Card */}
        <div className="card mt-6 animate-slide-in-right">
          <h4 className="text-lg font-bold text-gray-800 mb-4 flex items-center">
            <span className="mr-2">🚀</span>
            What's Next?
          </h4>
          <div className="space-y-3">
            <div className="flex items-center text-gray-700">
              <span className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">1</span>
              Upload your resume and create your profile
            </div>
            <div className="flex items-center text-gray-700">
              <span className="w-6 h-6 bg-green-100 text-green-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">2</span>
              Browse AI-ranked job listings
            </div>
            <div className="flex items-center text-gray-700">
              <span className="w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">3</span>
              Set your application preferences
            </div>
            <div className="flex items-center text-gray-700">
              <span className="w-6 h-6 bg-yellow-100 text-yellow-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">4</span>
              Run autonomous job applications
            </div>
            <div className="flex items-center text-gray-700">
              <span className="w-6 h-6 bg-red-100 text-red-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">5</span>
              Track your application history
            </div>
          </div>
        </div>

        {/* Demo Credentials */}
        <div className="card mt-6 bg-gray-50 border border-gray-200">
          <h4 className="text-sm font-bold text-gray-700 mb-3 flex items-center">
            <span className="mr-2">🔑</span>
            Demo Credentials
          </h4>
          <div className="text-xs text-gray-600 space-y-1">
            <div><strong>Email:</strong> demo@example.com</div>
            <div><strong>Password:</strong> demo123</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login