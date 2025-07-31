import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Container, Box, AppBar, Toolbar, Typography, Button } from '@mui/material'
import Dashboard from './pages/Dashboard'
import Brands from './pages/Brands'
import ContentGeneration from './pages/ContentGeneration'
import Campaigns from './pages/Campaigns'
import Login from './pages/Login'
import Register from './pages/Register'
import { useAuth } from './hooks/useAuth'

function App() {
  const { user, logout } = useAuth()

  const handleLogout = () => {
    logout()
  }

  if (!user) {
    return (
      <Container maxWidth="sm" sx={{ mt: 8 }}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Container>
    )
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AI Brand Content Generator
          </Typography>
          <Typography variant="body2" sx={{ mr: 2 }}>
            Welcome, {user.full_name || user.username}
          </Typography>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/brands" element={<Brands />} />
          <Route path="/content" element={<ContentGeneration />} />
          <Route path="/campaigns" element={<Campaigns />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Container>
    </Box>
  )
}

export default App