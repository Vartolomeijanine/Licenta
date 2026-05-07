import React from 'react'
import { Link, useNavigate } from 'react-router-dom'

function Navbar(){
  const navigate = useNavigate()
  const token = localStorage.getItem('access')
  const userName = localStorage.getItem('user_first_name')

  function handleLogout(){
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')
    localStorage.removeItem('user_email')
    localStorage.removeItem('user_first_name')
    navigate('/auth')
  }

  return (
    <nav className="nav">
      <div className="nav-left">
        <Link to="/" className="brand">ChromaticAI</Link>
      </div>
      <div className="nav-right">
        {!token && (
          <>
            <a className="nav-link" href="/#how-it-works">How it works</a>
            <a className="nav-link" href="/#seasons">Seasons</a>
            <a className="nav-link" href="/#benefits">Benefits</a>
            <Link to="/dashboard" className="btn ghost">Dashboard</Link>
            <Link to="/auth" className="btn primary">Start Analysis</Link>
          </>
        )}
        {token && (
          <>
            <Link to="/dashboard" className="nav-link">Dashboard</Link>
            <Link to="/profile" className="nav-link">{userName || 'Profile'}</Link>
            <button onClick={handleLogout} className="btn outline">Logout</button>
          </>
        )}
      </div>
    </nav>
  )
}

export default Navbar
