import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { deleteAnalysis, getHistory } from '../api/analysisApi'
import { getConfidenceLabel } from '../utils/confidence'
import { resolveMediaUrl } from '../utils/media'
import LoadingSpinner from '../components/LoadingSpinner'

const PALETTE_IMAGES = {
  spring: new URL('../../Spring.png', import.meta.url).href,
  summer: new URL('../../Summer.png', import.meta.url).href,
  autumn: new URL('../../Autumn.png', import.meta.url).href,
  winter: new URL('../../Winter.png', import.meta.url).href
}

const TRYON_TEXTS = {
  spring: {
    good: '✓ Bright, light, fresh, harmonious',
    bad: '✕ Too dark and cool, overpowers features'
  },
  summer: {
    good: '✓ Soft, balanced, harmonious',
    bad: '✕ Too warm, overpowers features'
  },
  autumn: {
    good: '✓ Earthy, rich, warm, harmonious',
    bad: '✕ Too cool and dusty, reduces natural warmth'
  },
  winter: {
    good: '✓ Bright, cool, high-contrast, harmonious',
    bad: '✕ Too light and muted, washes out features'
  }
}

export default function Result() {
  const { id } = useParams()
  const [item, setItem] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    async function load() {
      setLoading(true)
      const data = await getHistory()
      const found = data.find(x => String(x.id) === String(id))
      setItem(found)
      setLoading(false)
    }

    load()
  }, [id])

  if (loading) {
    return (
      <div className="page card">
        <div className="row" style={{ gap: 12, alignItems: 'center' }}>
          <LoadingSpinner />
          <div className="muted">Loading your analysis result...</div>
        </div>
      </div>
    )
  }

  if (!item) {
    return <div className="page card">Result not found.</div>
  }

  const confidenceLabel = getConfidenceLabel(item.confidence)
  const imageSrc = resolveMediaUrl(item.originalImageUrl || item.image)

  const seasonKey = (item.season || 'spring').toLowerCase()
  const paletteSrc = PALETTE_IMAGES[seasonKey] || PALETTE_IMAGES.spring
  const seasonTexts = TRYON_TEXTS[seasonKey] || TRYON_TEXTS.spring

  const goodImages = item.tryOnImages?.good || []
  const badImages = item.tryOnImages?.bad || []

  const selectedGood = goodImages[0]
  const selectedBad = badImages[0]

  const selectedGoodSrc = selectedGood ? resolveMediaUrl(selectedGood.imageUrl) : ''
  const selectedBadSrc = selectedBad ? resolveMediaUrl(selectedBad.imageUrl) : ''

  const hasTryOn = Boolean(selectedGood && selectedBad)

  async function handleDelete() {
    const ok = window.confirm('Ștergi această analiză?')
    if (!ok) return

    await deleteAnalysis(item.id)
    navigate('/dashboard')
  }

  return (
    <div className="analysis-page">
      <div className="analysis-result-card">
        <h1 className="result-title">Analysis Result</h1>

        <div className="tryon-heading">
          <h2>✨ Virtual Color Try-On</h2>
          <p>See how recommended vs. less flattering shades look near your face.</p>
        </div>

        {!hasTryOn && (
          <div className="result-warning">
            Virtual try-on previews could not be generated, but your analysis result is ready.
          </div>
        )}

        {hasTryOn ? (
          <div className="result-main-grid">
            <div className="result-photo-column original-column">
              <div className="tryon-card">
                <div className="tryon-card-header">
                  <h3 className="tryon-card-title">Original Photo</h3>
                </div>

                <div className="tryon-image-frame">
                  {imageSrc && <img src={imageSrc} alt="uploaded person" />}
                </div>
              </div>
            </div>

            <div className="result-photo-column best-column">
              <div className="tryon-card">
                <div className="tryon-card-header">
                  <h3 className="tryon-card-title">Best Match</h3>
                </div>

                <div className="tryon-image-frame">
                  {selectedGoodSrc && (
                    <img src={selectedGoodSrc} alt="best match try-on" />
                  )}
                </div>

                {selectedGood && (
                  <div className="single-swatch-preview">
                    <span
                      className="single-swatch-circle good"
                      style={{ backgroundColor: selectedGood.hex }}
                    />
                    <span className="single-swatch-label">
                      {selectedGood.name}
                    </span>
                  </div>
                )}

                <div className="tryon-note good">{seasonTexts.good}</div>
              </div>
            </div>

            <div className="result-photo-column bad-column">
              <div className="tryon-card">
                <div className="tryon-card-header">
                  <h3 className="tryon-card-title">Less Flattering</h3>
                </div>

                <div className="tryon-image-frame">
                  {selectedBadSrc && (
                    <img src={selectedBadSrc} alt="less flattering try-on" />
                  )}
                </div>

                {selectedBad && (
                  <div className="single-swatch-preview">
                    <span
                      className="single-swatch-circle bad"
                      style={{ backgroundColor: selectedBad.hex }}
                    />
                    <span className="single-swatch-label">
                      {selectedBad.name}
                    </span>
                  </div>
                )}

                <div className="tryon-note bad">{seasonTexts.bad}</div>
              </div>
            </div>

            <aside className="result-summary-column">
              <div className="summary-card">
                <h3>{item.season?.toUpperCase()}</h3>

                <div className="result-confidence">
                  AI confidence: {confidenceLabel}
                </div>

                <div className="result-warning">
                  AI result may be affected by lighting, makeup, hair dye, filters, and image quality.
                </div>

                <div className="palette-title">Recommended Palette</div>

                <img
                  className="palette-image"
                  src={paletteSrc}
                  alt={`${item.season || 'Season'} palette`}
                />
              </div>
            </aside>
          </div>
        ) : (
          <div className="result-layout">
            <div className="result-image">
              <div className="image-preview">
                {imageSrc && <img src={imageSrc} alt="uploaded person" />}
              </div>
            </div>

            <div className="result-info">
              <h3>{item.season?.toUpperCase()}</h3>

              <div className="muted">AI confidence: {confidenceLabel}</div>

              <p className="disclaimer">
                AI result may be affected by lighting, makeup, hair dye, filters, and image quality.
              </p>

              <div className="result-palette">
                <h4>Recommended Palette</h4>
                <img
                  src={paletteSrc}
                  alt={`${item.season || 'Season'} palette`}
                />
              </div>
            </div>
          </div>
        )}

        <div className="result-actions">
          <button className="btn danger" onClick={handleDelete}>
            Delete
          </button>

          <button className="btn" onClick={() => navigate('/dashboard')}>
            Back to Dashboard
          </button>

          <button
            className="btn primary"
            onClick={() => navigate('/analysis/new')}
          >
            Start Another Analysis
          </button>
        </div>
      </div>
    </div>
  )
}