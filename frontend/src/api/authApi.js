import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' }
})

// Attach Authorization header from localStorage on each request if available
api.interceptors.request.use((config)=>{
  try{
    const token = localStorage.getItem('access')
    if(token){
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }
  }catch(e){}
  return config
})

export async function login(email, password){
  const res = await api.post('/api/token/', { email, password })
  // returns { access, refresh }
  return res.data
}

export async function register(payload){
  // payload: { first_name, last_name, email, password, password_confirmation }
  const res = await api.post('/api/auth/register/', payload)
  return res.data
}

export async function getProfile(){
  const res = await api.get('/api/auth/profile/')
  return res.data
}

export default api
