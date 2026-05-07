import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { deleteAnalysis, getHistory } from '../api/analysisApi'
import ColorPalette from '../components/ColorPalette'
import { getConfidenceLabel } from '../utils/confidence'
import { resolveMediaUrl } from '../utils/media'

export default function Result(){
  const { id } = useParams()
  const [item, setItem] = useState(null)
  const navigate = useNavigate()

  useEffect(()=>{
    async function load(){
      const data = await getHistory()
      const found = data.find(x=>String(x.id)===String(id))
      setItem(found)
    }
    load()
  },[id])

  if(!item) return <div className="page card">Result not found.</div>

  const confidenceLabel = getConfidenceLabel(item.confidence)
  const imageSrc = resolveMediaUrl(item.image)

  async function handleDelete(){
    const ok = window.confirm('Ștergi această analiză?')
    if(!ok) return

    await deleteAnalysis(item.id)
    navigate('/dashboard')
  }

  return (
    <div className="page result card">
      <h2>Analysis Result</h2>
      <div className="row">
        <div className="result-main">
          <div className="image-preview">
            {imageSrc && <img src={imageSrc} alt="preview"/>}
          </div>
          <h3>{item.season?.toUpperCase()}</h3>
          <div className="muted">AI confidence: {confidenceLabel}</div>
          <p className="disclaimer">AI result may be affected by lighting, makeup, hair dye, filters, and image quality.</p>
          <div className="row">
            <button className="btn danger" onClick={handleDelete}>Delete</button>
            <button className="btn" onClick={()=>navigate('/dashboard')}>Back to Dashboard</button>
            <button className="btn primary" onClick={()=>navigate('/analysis/new')}>Start Another Analysis</button>
          </div>
        </div>

        <aside className="sidebar card">
          <h4>Recommended Palette</h4>
          <ColorPalette season={item.season} />
          <h4>Style Advice</h4>
          <p>Best colors: use the palette above. Avoid extremes in contrast if your season is muted.</p>
        </aside>
      </div>
    </div>
  )
}
