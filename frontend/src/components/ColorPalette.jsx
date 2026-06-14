import React from 'react'

const PALETTES = {
  spring: ['#F4A6B8', '#E74C40', '#F17D49', '#F9C95D', '#9EC97A'],
  summer: ['#E77995', '#F19CA7', '#F1DBE5', '#87A9C7', '#62589D'],
  autumn: ['#AA372B', '#CA5E2A', '#D49D34', '#556D38', '#AD7545'],
  winter: ['#E12C63', '#49377C', '#F4F5F8', '#385786', '#121216']
}

export default function ColorPalette({ season='spring' }){
  const list = PALETTES[season] || PALETTES.spring
  const seasonTitle = season.charAt(0).toUpperCase() + season.slice(1)
  
  return (
    <div className="compact-palette">
      <div className="compact-left">
        <span className={`compact-icon ${season}`} aria-hidden="true"></span>
        <span className="compact-title">{seasonTitle}</span>
      </div>
      <div className="compact-right">
        {list.map((c,i)=> (
          <div key={i} className="compact-swatch" style={{background:c}} title={c}></div>
        ))}
      </div>
    </div>
  )
}
