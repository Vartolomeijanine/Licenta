import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, register, getProfile } from '../api/authApi'

export default function Auth(){
  const [tab, setTab] = useState('login')
  const [form, setForm] = useState({})
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  function onChange(e){
    setForm({...form, [e.target.name]: e.target.value})
  }

  async function handleLogin(e){
    e.preventDefault(); setError(null)
    try{
      const data = await login(form.email, form.password)
      localStorage.setItem('access', data.access)
      localStorage.setItem('refresh', data.refresh)
      try{
        const profile = await getProfile()
        localStorage.setItem('user_first_name', profile.first_name)
        localStorage.setItem('user_email', profile.email)
      }catch(e){/* ignore */}
      navigate('/dashboard')
    }catch(err){
      setError(err.response?.data?.detail || 'Login failed')
    }
  }

  async function handleRegister(e){
    e.preventDefault(); setError(null)
    try{
      const payload = {
        first_name: form.first_name,
        last_name: form.last_name,
        email: form.email,
        password: form.password,
        password_confirmation: form.confirm
      }
      const data = await register(payload)
      // backend returns tokens inside response.data.tokens
      const tokens = data.tokens
      if(tokens){
        localStorage.setItem('access', tokens.access)
        localStorage.setItem('refresh', tokens.refresh)
      }
      try{
        const profile = await getProfile()
        localStorage.setItem('user_first_name', profile.first_name)
        localStorage.setItem('user_email', profile.email)
      }catch(e){}
      navigate('/dashboard')
    }catch(err){
      setError(err.response?.data || 'Register failed')
    }
  }

  return (
    <div className="page auth card">
      <div className="auth-tabs" role="tablist" aria-label="Authentication">
        <button
          type="button"
          className={`auth-tab ${tab==='login' ? 'active' : ''}`}
          onClick={()=>setTab('login')}
          role="tab"
          aria-selected={tab==='login'}
        >
          Login
        </button>
        <button
          type="button"
          className={`auth-tab ${tab==='register' ? 'active' : ''}`}
          onClick={()=>setTab('register')}
          role="tab"
          aria-selected={tab==='register'}
        >
          Register
        </button>
      </div>

      {tab==='login' && (
        <form onSubmit={handleLogin} className="form">
          <label>Email<input type="email" name="email" onChange={onChange} required/></label>
          <label>Password<input type="password" name="password" onChange={onChange} required/></label>
          {error && <div className="error">{String(error)}</div>}
          <button className="btn primary" style={{marginTop: '12px', width: '100%'}}>Login</button>
        </form>
      )}

      {tab==='register' && (
        <form onSubmit={handleRegister} className="form">
          <label>First name<input type="text" name="first_name" onChange={onChange} required/></label>
          <label>Last name<input type="text" name="last_name" onChange={onChange} required/></label>
          <label>Email<input type="email" name="email" onChange={onChange} required/></label>
          <label>Password<input type="password" name="password" onChange={onChange} required/></label>
          <label>Confirm password<input type="password" name="confirm" onChange={onChange} required/></label>
          {error && <div className="error">{String(error)}</div>}
          <button className="btn primary" style={{marginTop: '12px', width: '100%'}}>Register</button>
        </form>
      )}
    </div>
  )
}
