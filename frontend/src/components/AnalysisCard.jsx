import React from 'react'
import { Link } from 'react-router-dom'
import { getConfidenceLabel } from '../utils/confidence'
import { resolveMediaUrl } from '../utils/media'

const SEASON_COLOR = {
  spring: '#FFD6A5',
  summer: '#BFD7EA',
  autumn: '#F4A261',
  winter: '#7FB5FF'
}

export default function AnalysisCard({ item }){
  const season = item.season
  const color = SEASON_COLOR[season] || '#E6E9EE'
  const confidenceLabel = getConfidenceLabel(item.confidence)
  const imageSrc = resolveMediaUrl(item.image)

  return (
    <div className="card analysis-card">
      <div className="card-img">
        {imageSrc ? <img src={imageSrc} alt="analysis"/> : <div className="placeholder">No image</div>}
      </div>
      <div className="card-body">
        <div className="muted">{new Date(item.created_at).toLocaleString()}</div>
        <h4 style={{display:'flex',alignItems:'center',gap:8, margin: '10px 0 4px', fontSize: '1.2rem', letterSpacing: '-0.3px'}}>
          <span style={{width:14,height:14,background:color,borderRadius:'50%',display:'inline-block',boxShadow:'0 2px 6px rgba(0,0,0,0.1)'}}></span>
          {season ? season.toUpperCase() : 'Unknown'}
        </h4>
        <div className="muted">AI confidence: {confidenceLabel}</div>
        <div className="card-actions">
          <Link to={`/analysis/${item.id}/result`} className="btn">View Result</Link>
        </div>
      </div>
    </div>
  )
}
