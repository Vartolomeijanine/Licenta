import React, { useEffect, useState } from 'react'
import { fetchProfile } from '../api/userApi'
import { getHistory } from '../api/analysisApi'

export default function Profile(){
  const [profile, setProfile] = useState(null)
  const [stats, setStats] = useState({ total:0, recent: null })

  useEffect(()=>{
    async function load(){
      const p = await fetchProfile()
      setProfile(p)
      const history = await getHistory()
      setStats({ total: history.length, recent: history[0] ?? null })
      if(history[0]){
        // store recent name/email for navbar
        localStorage.setItem('user_first_name', p.first_name)
        localStorage.setItem('user_email', p.email)
      }
    }
    load()
  },[])

  if(!profile) return <div className="page card">Loading...</div>

  return (
    <div className="page profile card">
      <h2>Profile</h2>
      <div><strong>Name:</strong> {profile.first_name} {profile.last_name}</div>
      <div><strong>Email:</strong> {profile.email}</div>
      <div><strong>Total analyses:</strong> {stats.total}</div>
      <div><strong>Most recent:</strong> {stats.recent ? `${stats.recent.season} — ${new Date(stats.recent.created_at).toLocaleString()}` : '—'}</div>
    </div>
  )
}
