import { useState, useEffect } from 'react'
import axios from 'axios'

interface User {
  id: number
  username: string
  email: string
  full_name?: string
  role: string
  is_active: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  loading: boolean
}

export const useAuth = () => {
  const [auth, setAuth] = useState<AuthState>({
    user: null,
    token: localStorage.getItem('token'),
    loading: true
  })

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      // Set default authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      
      // Verify token and get user info
      axios.get('/api/v1/auth/me')
        .then(response => {
          setAuth({
            user: response.data,
            token,
            loading: false
          })
        })
        .catch(() => {
          // Token is invalid
          localStorage.removeItem('token')
          delete axios.defaults.headers.common['Authorization']
          setAuth({
            user: null,
            token: null,
            loading: false
          })
        })
    } else {
      setAuth(prev => ({ ...prev, loading: false }))
    }
  }, [])

  const login = async (username: string, password: string) => {
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)

      const response = await axios.post('/api/v1/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      const { access_token, user } = response.data
      
      localStorage.setItem('token', access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      setAuth({
        user,
        token: access_token,
        loading: false
      })

      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      }
    }
  }

  const register = async (userData: {
    username: string
    email: string
    password: string
    full_name?: string
  }) => {
    try {
      await axios.post('/api/v1/auth/register', userData)
      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed'
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
    setAuth({
      user: null,
      token: null,
      loading: false
    })
  }

  return {
    user: auth.user,
    token: auth.token,
    loading: auth.loading,
    login,
    register,
    logout
  }
}