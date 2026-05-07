import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Auth from './pages/Auth'
import Dashboard from './pages/Dashboard'
import NewAnalysis from './pages/NewAnalysis'
import Result from './pages/Result'
import Profile from './pages/Profile'
import NotFound from './pages/NotFound'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'

export default function App(){
  return (
    <div>
      <Navbar />
      <main className="app-container">
        <Routes>
          <Route path="/" element={<Home/>} />
          <Route path="/auth" element={<Auth/>} />

          <Route path="/dashboard" element={<ProtectedRoute><Dashboard/></ProtectedRoute>} />
          <Route path="/analysis/new" element={<ProtectedRoute><NewAnalysis/></ProtectedRoute>} />
          <Route path="/analysis/:id/result" element={<ProtectedRoute><Result/></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile/></ProtectedRoute>} />

          <Route path="*" element={<NotFound/>} />
        </Routes>
      </main>
    </div>
  )
}
