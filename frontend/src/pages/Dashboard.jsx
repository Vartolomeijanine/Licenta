import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getHistory } from '../api/analysisApi'
import AnalysisCard from '../components/AnalysisCard'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Dashboard(){
  const [history, setHistory] = useState(null)
  const [loading, setLoading] = useState(false)

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
          <h2>Welcome</h2>
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
          {history && history.map(item=> (
            <AnalysisCard key={item.id} item={item} />
          ))}
        </div>
      </div>
    </div>
  )
}
