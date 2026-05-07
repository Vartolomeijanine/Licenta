import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createAnalysis } from '../api/analysisApi'
import LoadingSpinner from '../components/LoadingSpinner'

export default function NewAnalysis(){
  const [file, setFile] = useState(null)
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  function onFile(e){ setFile(e.target.files[0]) }
  function onAns(e){ setAnswers({...answers, [e.target.name]: e.target.value}) }

  async function handleSubmit(e){
    e.preventDefault(); setError(null)
    if(!file){ setError('Please select a selfie'); return }
    setLoading(true)
    try{
      const fd = new FormData()
      fd.append('image', file)
      // TODO: Backend serializer currently only expects `image`.
      // If you extend the serializer to accept extra fields, uncomment these.
      // fd.append('hair_visible', answers.hair_visible)
      // fd.append('natural_hair', answers.natural_hair)
      // fd.append('makeup', answers.makeup)
      // fd.append('natural_light', answers.natural_light)
      // fd.append('colored_clothes', answers.colored_clothes)

      const res = await createAnalysis(fd)
      // creation returns an object with id — redirect to result
      navigate(`/analysis/${res.id}/result`)
    }catch(err){
      console.error(err); setError('Analysis failed')
    }finally{ setLoading(false) }
  }

  return (
    <div className="page new-analysis card">
      <h2>New Analysis</h2>
      <form onSubmit={handleSubmit} className="form">
        <label>Selfie (front-facing, natural light)
          <input type="file" accept="image/*" onChange={onFile} />
        </label>

        <div className="instructions">
          <p>Tips: face visible, natural light, no heavy filters.</p>
        </div>

        <div className="questions">
          <label>Is your hair visible?
            <select name="hair_visible" onChange={onAns}><option value="">—</option><option>yes</option><option>no</option></select>
          </label>
          <label>Is it your natural hair color?
            <select name="natural_hair" onChange={onAns}><option value="">—</option><option>yes</option><option>no</option></select>
          </label>
          <label>Wearing makeup?
            <select name="makeup" onChange={onAns}><option value="">—</option><option>yes</option><option>no</option></select>
          </label>
          <label>Taken in natural light?
            <select name="natural_light" onChange={onAns}><option value="">—</option><option>yes</option><option>no</option></select>
          </label>
          <label>Wearing strongly colored clothes near face?
            <select name="colored_clothes" onChange={onAns}><option value="">—</option><option>yes</option><option>no</option></select>
          </label>
        </div>

        {error && <div className="error">{error}</div>}
        <div className="row">
          <button className="btn primary">Analyze</button>
          {loading && <LoadingSpinner />}
        </div>
      </form>
    </div>
  )
}
