import React from 'react'

const PALETTES = {
  spring: ['#FFE8D6','#FFD6A5','#FFB4A2','#FFCDB2','#BDE0FE'],
  summer: ['#E0F2FE','#BFD7EA','#A8DADC','#C6E2FF','#F1F6F9'],
  autumn: ['#FFDAB9','#F4A261','#E76F51','#C1440E','#8B4513'],
  winter: ['#D0E8F2','#A7C5BD','#7FB5FF','#4D648D','#1B1F3B']
}

export default function SeasonSwatches({ season='spring' }){
  const list = PALETTES[season] || PALETTES.spring
  return (
    <div className="mini-palette">
      {list.map((c,i)=> (
        <div key={i} className="mini-swatch" style={{background:c}} title={c}></div>
      ))}
    </div>
  )
}
