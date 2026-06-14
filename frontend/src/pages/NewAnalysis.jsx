import React, { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createAnalysis } from '../api/analysisApi'
import LoadingSpinner from '../components/LoadingSpinner'

export default function NewAnalysis(){
  const [file, setFile] = useState(null)
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [warning, setWarning] = useState(null)
  const fileInputRef = useRef(null)
  const navigate = useNavigate()

  const hairColorOptions = [
    'black',
    'dark brown',
    'medium brown',
    'light brown',
    'red',
    'blonde',
    'gray',
    'white'
  ]

  const showNaturalHairQuestion = answers.hair_visible === 'yes'
  const showNaturalHairColorQuestion =
    answers.hair_visible === 'no' || (answers.hair_visible === 'yes' && answers.natural_hair === 'no')

  function onFile(e){ setFile(e.target.files[0]) }
  function onAns(e){
    const { name, value } = e.target
    setAnswers((prev)=>({ ...prev, [name]: value }))

    if(name === 'makeup' && value === 'yes'){
      setWarning('makeup')
    }
    if(name === 'natural_light' && value === 'no'){
      setWarning('natural_light')
    }
    if(name === 'colored_clothes' && value === 'yes'){
      setWarning('colored_clothes')
    }
  }

  function handleChooseAnotherPhoto(){
    setWarning(null)
    if(fileInputRef.current){
      fileInputRef.current.click()
    }
  }

  async function handleSubmit(e){
    e.preventDefault(); setError(null)
    if(!file){ setError('Please select a selfie'); return }
    setLoading(true)
    try{
      const fd = new FormData()
      fd.append('image', file)
      if(showNaturalHairColorQuestion && answers.natural_hair_color){
        fd.append('naturalHairColor', answers.natural_hair_color)
      }
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
          <input ref={fileInputRef} type="file" accept="image/*" onChange={onFile} />
        </label>

        <div className="instructions">
          <p>Tips: face visible, natural light, no heavy filters.</p>
        </div>

        <div className="questions">
          <label>Is your hair visible?
            <select name="hair_visible" onChange={onAns}><option value="">—</option><option>yes</option><option>no</option></select>
          </label>
          {showNaturalHairQuestion && (
            <label>Is it your natural hair color?
              <select name="natural_hair" onChange={onAns}><option value="">—</option><option>yes</option><option>no</option></select>
            </label>
          )}
          {showNaturalHairColorQuestion && (
            <label>What is your natural hair color?
              <select name="natural_hair_color" onChange={onAns} value={answers.natural_hair_color || ''}>
                <option value="">—</option>
                {hairColorOptions.map((color)=>(
                  <option key={color} value={color}>{color}</option>
                ))}
              </select>
            </label>
          )}
          <label>Wearing a lot of makeup?
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
        {loading && (
          <div className="loading-message">
            Generating your virtual color try-on previews with Google Nano Banana...
          </div>
        )}
      </form>

      {warning && (
        <div className="modal-backdrop" role="dialog" aria-modal="true">
          <div className="modal warning-modal">
            <h4>Heads up</h4>
            {warning === 'makeup' && (
              <p>For better results, please choose another photo without heavy makeup.</p>
            )}
            {warning === 'natural_light' && (
              <p>For better results, please choose another photo taken in natural light.</p>
            )}
            {warning === 'colored_clothes' && (
              <p>For better results, please choose another photo without strongly colored clothes near your face.</p>
            )}
            <div className="modal-actions">
              <button className="btn" onClick={()=>setWarning(null)}>I understand</button>
              <button className="btn outline" onClick={handleChooseAnotherPhoto}>Choose another photo</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
