import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for existing session on app load
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('auth_user')
    
    if (savedToken && savedUser) {
      setToken(savedToken)
      setUser(JSON.parse(savedUser))
    }
    
    setLoading(false)
  }, [])

  const login = (authData) => {
    const userData = {
      id: authData.user_id,
      email: authData.email
    }
    
    setUser(userData)
    setToken(authData.token)
    
    localStorage.setItem('auth_token', authData.token)
    localStorage.setItem('auth_user', JSON.stringify(userData))
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
    localStorage.removeItem('resumeHash')
    localStorage.removeItem('resumeText')
  }

  const isAuthenticated = () => {
    return !!(user && token)
  }

  const getAuthHeaders = () => {
    return token ? { Authorization: `Bearer ${token}` } : {}
  }

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    isAuthenticated,
    getAuthHeaders
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}