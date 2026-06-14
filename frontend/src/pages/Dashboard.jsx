import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getHistory } from '../api/analysisApi'
import LoadingSpinner from '../components/LoadingSpinner'
import { getConfidenceLabel } from '../utils/confidence'
import { resolveMediaUrl } from '../utils/media'

const SEASON_COLOR = {
  spring: '#FFD6A5',
  summer: '#BFD7EA',
  autumn: '#F4A261',
  winter: '#7FB5FF'
}

export default function Dashboard(){
  const [history, setHistory] = useState(null)
  const [loading, setLoading] = useState(false)
  const firstName = localStorage.getItem('user_first_name')

  function formatHistoryDate(value){
    if(!value){
      return 'Unknown date'
    }
    return new Date(value).toLocaleString('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  useEffect(()=>{
    async function load(){
      setLoading(true)
      try{
        const data = await getHistory()
        // backend serializer returns list of analyses
        // Note: image field may be relative; the create endpoint returns absolute url on creation.
        setHistory(data)
      }catch(e){
        console.error(e)
        setHistory([])
      }finally{setLoading(false)}
    }
    load()
  },[])

  return (
    <div className="page dashboard">
      <div className="card">
        <div className="row between">
          <h2>Welcome{firstName ? `, ${firstName}` : ''}</h2>
          <Link to="/analysis/new" className="btn primary">Start New Analysis</Link>
        </div>
      </div>

      <div className="card">
        <h3>Your Analysis History</h3>
        {loading && <LoadingSpinner />}
        {!loading && history && history.length===0 && (
          <div className="empty">No analyses yet. Start your first analysis.</div>
        )}
        <div className="history-grid">
          {history && history.map(item=> {
            const season = item.season
            const color = SEASON_COLOR[season] || '#E6E9EE'
            const confidenceLabel = getConfidenceLabel(item.confidence)
            const imageSrc = resolveMediaUrl(item.image)

            return (
              <div key={item.id} className="card analysis-card">
                <div className="card-img">
                  {imageSrc ? <img src={imageSrc} alt="analysis"/> : <div className="placeholder">No image</div>}
                </div>
                <div className="card-body">
                  <div className="muted">{formatHistoryDate(item.created_at)}</div>
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
          })}
        </div>
      </div>
    </div>
  )
}
