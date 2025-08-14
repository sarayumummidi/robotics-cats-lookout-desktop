import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

export function useAuth() {
  return useContext(AuthContext)
}

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already authenticated
    const checkAuth = async () => {
      try {
        const response = await axios.get('/api/instances')
        if (response.status === 200) {
          setIsAuthenticated(true)
        }
      } catch (error) {
        // Don't set loading to false on auth error, just set not authenticated
        if (error.response?.status === 401) {
          setIsAuthenticated(false)
        }
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [])

  const login = async (password) => {
    try {
      const response = await axios.post('/login', { password }, {
        headers: {
          'Content-Type': 'application/json'
        }
      })
      if (response.status === 200) {
        setIsAuthenticated(true)
        return { success: true }
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Login failed',
      }
    }
  }

  const logout = async () => {
    try {
      await axios.get('/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setIsAuthenticated(false)
    }
  }

  const value = {
    isAuthenticated,
    loading,
    login,
    logout,
  }

  if (loading) {
    return <div>Loading...</div>
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
