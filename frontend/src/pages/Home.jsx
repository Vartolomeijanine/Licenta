import React, { useState } from 'react'
import { Link } from 'react-router-dom'

const beforeAfterExamples = [
  {
    before: new URL('../../poze frontend/spr/spr1_before.jpg', import.meta.url).href,
    after: new URL('../../poze frontend/spr/spr1_after.webp', import.meta.url).href,
    season: 'Spring'
  },
  {
    before: new URL('../../poze frontend/win/win2_before.jpg', import.meta.url).href,
    after: new URL('../../poze frontend/win/win2_after.webp', import.meta.url).href,
    season: 'Winter'
  },
  {
    before: new URL('../../poze frontend/aut/aut3_before.jpg', import.meta.url).href,
    after: new URL('../../poze frontend/aut/aut3_after.jpg', import.meta.url).href,
    season: 'Autumn'
  },
  {
    before: new URL('../../poze frontend/sum/sum2_before.jpg', import.meta.url).href,
    after: new URL('../../poze frontend/sum/sum2_after.webp', import.meta.url).href,
    season: 'Summer'
  }
]

export default function Home(){
  const [currentSlide, setCurrentSlide] = useState(0)
  const startLink = typeof window !== 'undefined' && localStorage.getItem('access') ? '/analysis/new' : '/auth'
  const mockAnalysisFlow = [
    {
      key: 'initial',
      label: 'Initial Photo',
      note: 'Before analysis',
      tone: 'neutral',
      image: new URL('../../anne1.png', import.meta.url).href
    },
    {
      key: 'best',
      label: 'Best Colors',
      note: 'Brighter and more balanced',
      tone: 'best',
      image: new URL('../../anne2.png', import.meta.url).href,
      colorName: 'Berry',
      colorHex: '#BE185D'
    },
    {
      key: 'worst',
      label: 'Worst Colors',
      note: 'Can look washed out',
      tone: 'worst',
      image: new URL('../../anne3.png', import.meta.url).href,
      colorName: 'Warm Beige',
      colorHex: '#D9B382'
    }
  ]
  const seasonalCards = [
    {
      name: 'Spring',
      description: 'Warm, light, fresh, bright',
      paletteImage: new URL('../../Spring.png', import.meta.url).href,
      exampleImage: new URL('../../poze frontend/spr/spr2_after.webp', import.meta.url).href
    },
    {
      name: 'Summer',
      description: 'Cool, soft, muted, elegant',
      paletteImage: new URL('../../Summer.png', import.meta.url).href,
      exampleImage: new URL('../../poze frontend/sum/sum1_after.jpg', import.meta.url).href
    },
    {
      name: 'Autumn',
      description: 'Warm, earthy, rich, deep',
      paletteImage: new URL('../../Autumn.png', import.meta.url).href,
      exampleImage: new URL('../../poze frontend/aut/aut2_after.jpg', import.meta.url).href
    },
    {
      name: 'Winter',
      description: 'Cool, bold, high-contrast, vivid',
      paletteImage: new URL('../../Winter.png', import.meta.url).href,
      exampleImage: new URL('../../poze frontend/win/win1_after.webp', import.meta.url).href
    }
  ]

  const slideSize = 2
  const totalSlides = Math.max(1, Math.ceil(beforeAfterExamples.length / slideSize))
  const currentExamples = beforeAfterExamples.length
    ? [
        beforeAfterExamples[(currentSlide * slideSize) % beforeAfterExamples.length],
        beforeAfterExamples[(currentSlide * slideSize + 1) % beforeAfterExamples.length]
      ]
    : []

  const nextSlide = () => {
    if (totalSlides <= 1) return
    setCurrentSlide((slide) => (slide + 1) % totalSlides)
  }

  const prevSlide = () => {
    if (totalSlides <= 1) return
    setCurrentSlide((slide) => (slide - 1 + totalSlides) % totalSlides)
  }
  return (
    <div className="page home-landing">
      <section className="landing-hero">
        <div className="hero-copy">
          <h1>
            Discover Your Best
            Colors with{" "}
            <span className="hero-emphasis">AI Seasonal Analysis</span>
          </h1>
          <p>
            Our analysis identifies the colors that harmonize with your skin undertone,
            hair, and eyes so you can choose clothes and makeup with confidence.
          </p>
          <div className="hero-actions">
            <Link to={startLink} className="btn primary">Start Your Color Analysis</Link>
            <a href="#how-it-works" className="btn outline">Learn How It Works</a>
          </div>
          <div className="hero-badges">
            <div className="hero-badge"><span className="badge-dot" aria-hidden="true"></span>AI-Powered</div>
            <div className="hero-badge"><span className="badge-dot" aria-hidden="true"></span>Private &amp; Secure</div>
            <div className="hero-badge"><span className="badge-dot" aria-hidden="true"></span>Results in Minutes</div>
          </div>
        </div>
        <div className="hero-panel">
          <div className="upload-card">
            <div className="upload-header">
              <div className="upload-title">AI generates photos with colors that look best and worst on you</div>
            </div>

            <div className="mock-flow-grid" aria-label="Mock analysis preview">
              {mockAnalysisFlow.map((item) => (
                <div className={`mock-flow-card ${item.tone}`} key={item.key}>
                  <img className="mock-flow-photo" src={item.image} alt={item.label} />
                  <div className="mock-flow-label">{item.label}</div>
                  <div className="mock-flow-note">{item.note}</div>
                  {item.colorName && (
                    <div className="mock-flow-color-row">
                      <span
                        className="mock-flow-color-dot"
                        style={{ backgroundColor: item.colorHex }}
                        aria-hidden="true"
                      ></span>
                      <span className="mock-flow-color-name">{item.colorName}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="seasons" className="card info-intro">
        <h2>What is color analysis?</h2>
        <p className="info-intro-text">
          Color analysis helps you identify tones that naturally harmonize with your features so you can choose shades with confidence.
        </p>
        <div className="benefit-mini-grid">
          <div className="mini-card">
            <span className="mini-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <circle cx="12" cy="12" r="4"></circle>
                <path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1" strokeLinecap="round" strokeLinejoin="round"></path>
              </svg>
            </span>
            <span className="mini-title">Understand your undertone</span>
          </div>
          <div className="mini-card">
            <span className="mini-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <path d="M7 4l3 2h4l3-2 2 3-4 2v9H9v-9l-4-2 2-3z" strokeLinecap="round" strokeLinejoin="round"></path>
                <path d="M9 11h6"></path>
              </svg>
            </span>
            <span className="mini-title">Build a cohesive wardrobe</span>
          </div>
          <div className="mini-card">
            <span className="mini-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <path d="M9 4h6l-1 3H10L9 4z" strokeLinecap="round" strokeLinejoin="round"></path>
                <rect x="9" y="7" width="6" height="11" rx="2" ry="2"></rect>
                <path d="M8 20h8"></path>
              </svg>
            </span>
            <span className="mini-title">Choose flattering makeup shades</span>
          </div>
          <div className="mini-card">
            <span className="mini-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <path d="M6 8h12l-1 12H7L6 8z" strokeLinecap="round" strokeLinejoin="round"></path>
                <path d="M9 8a3 3 0 0 1 6 0" strokeLinecap="round" strokeLinejoin="round"></path>
              </svg>
            </span>
            <span className="mini-title">Shop with more confidence</span>
          </div>
        </div>

        <div className="before-after-section">
          <div className="before-after-card">
            <div className="before-after-header">
              <div>
                <h3>Before and After Color Analysis</h3>
                <p>
                  See how the right seasonal palette can make the face look brighter, more balanced and more harmonious.
                </p>
              </div>
            </div>

            <div className="before-after-carousel">
              <button
                className="carousel-btn carousel-btn-left"
                type="button"
                onClick={prevSlide}
                aria-label="Previous before and after examples"
              >
                <svg viewBox="0 0 24 24" role="img" focusable="false" aria-hidden="true">
                  <path d="M14.5 5.5L8 12l6.5 6.5" strokeLinecap="round" strokeLinejoin="round"></path>
                </svg>
              </button>

              <div className="before-after-grid">
                {currentExamples.map((example, index) => (
                  <article className="before-after-example" key={`${example.season}-${index}-${currentSlide}`}>
                    <span className="season-chip">{example.season}</span>
                    <div className="before-after-images">
                      <div className="before-after-image-box">
                        <span className="before-after-label">Before</span>
                        <img className="before-after-photo" src={example.before} alt={`${example.season} before color analysis`} />
                      </div>
                      <div className="before-after-arrow" aria-hidden="true">
                        <svg viewBox="0 0 48 24" role="img" focusable="false">
                          <path d="M2 12h34" strokeLinecap="round" strokeLinejoin="round"></path>
                          <path d="M28 4l8 8-8 8" strokeLinecap="round" strokeLinejoin="round"></path>
                        </svg>
                      </div>
                      <div className="before-after-image-box">
                        <span className="before-after-label">After</span>
                        <img className="before-after-photo" src={example.after} alt={`${example.season} after color analysis`} />
                      </div>
                    </div>
                  </article>
                ))}
              </div>

              <button
                className="carousel-btn carousel-btn-right"
                type="button"
                onClick={nextSlide}
                aria-label="Next before and after examples"
              >
                <svg viewBox="0 0 24 24" role="img" focusable="false" aria-hidden="true">
                  <path d="M9.5 5.5L16 12l-6.5 6.5" strokeLinecap="round" strokeLinejoin="round"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </section>

      <section className="card season-overview">
        <h2>The 4 seasonal palettes</h2>
        <div className="season-grid">
          {seasonalCards.map((season) => (
            <article className="season-card" key={season.name}>
              <h4>{season.name}</h4>
              <p>{season.description}</p>
              <img className="season-image" src={season.paletteImage} alt={`${season.name} palette`} />
              <div className="season-example-block">
                <span className="season-example-label">Example look</span>
                <img
                  className="season-example-image"
                  src={season.exampleImage}
                  alt={`${season.name} example look`}
                />
              </div>
            </article>
          ))}
        </div>
      </section>

      <section id="benefits" className="card benefits-section">
        <h2>Benefits</h2>
        <p className="info-intro-text">
          Discover the everyday advantages of knowing your seasonal palette and natural harmony.
        </p>
        <div className="benefit-grid">
          <div className="benefit-card">
            <span className="benefit-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <path d="M12 3c5 0 9 4 9 9 0 4.2-2.8 7.8-6.6 8.8L12 22l-2.4-1.2C5.8 19.8 3 16.2 3 12c0-5 4-9 9-9z" strokeLinecap="round" strokeLinejoin="round"></path>
                <path d="M9.5 10.5a2 2 0 1 1 4 0c0 1.4-2 1.7-2 3" strokeLinecap="round" strokeLinejoin="round"></path>
                <path d="M11.5 16h1" strokeLinecap="round" strokeLinejoin="round"></path>
              </svg>
            </span>
            <div className="benefit-content">
              <h4>Personalized color palette</h4>
              <p>Custom shades that suit your features.</p>
            </div>
          </div>
          <div className="benefit-card">
            <span className="benefit-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <path d="M4 20l6-6" strokeLinecap="round" strokeLinejoin="round"></path>
                <path d="M14 4l6 6" strokeLinecap="round" strokeLinejoin="round"></path>
                <path d="M8 8l8 8" strokeLinecap="round" strokeLinejoin="round"></path>
                <path d="M14 4l-4 4 6 6 4-4-6-6z" strokeLinecap="round" strokeLinejoin="round"></path>
              </svg>
            </span>
            <div className="benefit-content">
              <h4>Easier styling and makeup choices</h4>
              <p>Choose what looks best more easily.</p>
            </div>
          </div>
          <div className="benefit-card">
            <span className="benefit-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <path d="M6 8h12l-1 12H7L6 8z" strokeLinecap="round" strokeLinejoin="round"></path>
                <path d="M9 8a3 3 0 0 1 6 0" strokeLinecap="round" strokeLinejoin="round"></path>
              </svg>
            </span>
            <div className="benefit-content">
              <h4>Smarter shopping decisions</h4>
              <p>Shop with more clarity and less guesswork.</p>
            </div>
          </div>
          <div className="benefit-card">
            <span className="benefit-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <path d="M7 4h10a2 2 0 0 1 2 2v14l-7-4-7 4V6a2 2 0 0 1 2-2z" strokeLinecap="round" strokeLinejoin="round"></path>
              </svg>
            </span>
            <div className="benefit-content">
              <h4>Saved analysis history</h4>
              <p>Revisit your past results anytime.</p>
            </div>
          </div>
        </div>
      </section>

      <section id="how-it-works" className="card steps-section">
        <h2>How it works</h2>
        <p className="info-intro-text">
          A simple four-step flow that takes you from upload to personalized results.
        </p>
        <div className="steps-grid">
          <div className="step-card">
            <span className="step-badge">1</span>
            <span className="step-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <path d="M7 17a4 4 0 0 1 .4-8A5 5 0 0 1 17 8a4 4 0 1 1 1 7H7z" strokeLinecap="round" strokeLinejoin="round"></path>
                <path d="M12 12v6" strokeLinecap="round" strokeLinejoin="round"></path>
                <path d="M9.5 14.5L12 12l2.5 2.5" strokeLinecap="round" strokeLinejoin="round"></path>
              </svg>
            </span>
            <div className="step-content">
              <h4>Upload a selfie</h4>
              <p>Add a clear photo in natural light.</p>
            </div>
          </div>
          <div className="step-card">
            <span className="step-badge">2</span>
            <span className="step-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <rect x="4" y="4" width="16" height="16" rx="3" ry="3"></rect>
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M8 9h.01M16 9h.01M8 15h.01M16 15h.01" strokeLinecap="round" strokeLinejoin="round"></path>
              </svg>
            </span>
            <div className="step-content">
              <h4>Face detection</h4>
              <p>We detect your face and key regions.</p>
            </div>
          </div>
          <div className="step-card">
            <span className="step-badge">3</span>
            <span className="step-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <path d="M3 21l4-1 10-10-3-3L4 17l-1 4z" strokeLinecap="round" strokeLinejoin="round"></path>
                <path d="M14 7l3 3" strokeLinecap="round" strokeLinejoin="round"></path>
                <path d="M16 3l5 5" strokeLinecap="round" strokeLinejoin="round"></path>
              </svg>
            </span>
            <div className="step-content">
              <h4>Color feature extraction</h4>
              <p>We analyze skin, eyes, and hair.</p>
            </div>
          </div>
          <div className="step-card">
            <span className="step-badge">4</span>
            <span className="step-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" role="img" focusable="false">
                <path d="M12 3l1.7 4.2L18 9l-4.3 1.2L12 15l-1.7-4.8L6 9l4.3-1.8L12 3z" strokeLinecap="round" strokeLinejoin="round"></path>
                <path d="M19 14l.8 2 2.2.8-2.2.8L19 20l-.8-2.4L16 16.8l2.2-.8L19 14z" strokeLinecap="round" strokeLinejoin="round"></path>
              </svg>
            </span>
            <div className="step-content">
              <h4>AI season prediction and results</h4>
              <p>You receive your season and palette.</p>
            </div>
          </div>
        </div>
        <div className="note-bar">For best results, use natural light, keep your hair visible, and avoid strong filters.</div>
      </section>

      <section className="card landing-cta">
        <div>
          <h3>Ready to discover your best colors?</h3>
          <p>Start your AI color analysis in less than 2 minutes.</p>
        </div>
        <Link to={startLink} className="btn primary">Start Your Color Analysis</Link>
      </section>

      <footer className="landing-footer">
        <div className="footer-brand">ChromaticAI</div>
        <div className="footer-links">
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
          <a href="#">Contact</a>
        </div>
      </footer>
    </div>
  )
}
