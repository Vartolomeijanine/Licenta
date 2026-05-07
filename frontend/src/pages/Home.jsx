import React from 'react'
import { Link } from 'react-router-dom'

export default function Home(){
  const heroPalettes = [
    {
      name: 'Spring',
      emoji: '🌸',
      colors: ['#F6D58A', '#F2B07C', '#F07C63', '#B9D75B', '#8FD8B5', '#6EC7D6']
    },
    {
      name: 'Summer',
      emoji: '🍃',
      colors: ['#D9A4B5', '#C996B4', '#B07FA7', '#9AA0C4', '#6F8FAE', '#5B7C97']
    },
    {
      name: 'Autumn',
      emoji: '🍂',
      colors: ['#E3974C', '#D67A3E', '#B55A2A', '#9C7C39', '#7C8B4A', '#3F7A60']
    },
    {
      name: 'Winter',
      emoji: '❄️',
      colors: ['#E1165A', '#B20C58', '#6C2C7F', '#4E43A6', '#1D4E9D', '#2D2E3C']
    }
  ]

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
            <Link to="/auth" className="btn primary">Start Your Color Analysis</Link>
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
              <div className="upload-title">Upload a clear selfie</div>
              <div className="upload-subtitle">Use natural light for best results</div>
            </div>
            <div className="upload-preview">
              <img className="preview-face-image" src={new URL('../../emma.webp', import.meta.url).href} alt="preview face" />
            </div>
            <button className="btn outline" type="button">Upload Photo</button>
            <div className="upload-note">JPG, PNG - Max 10MB</div>
          </div>
          <div className="season-panel">
            <div className="season-panel-title">The 4 Seasonal Palettes</div>
            {heroPalettes.map((palette) => (
              <div className="season-panel-item" key={palette.name}>
                <div className="season-row">
                  <span className="season-emoji" aria-hidden="true">{palette.emoji}</span>
                  <span className="season-name">{palette.name}</span>
                </div>
                <div className="season-swatches">
                  {palette.colors.map((color) => (
                    <span
                      className="season-swatch"
                      style={{ background: color }}
                      key={color}
                      title={color}
                    ></span>
                  ))}
                  <span className="season-ellipsis" aria-hidden="true">...</span>
                </div>
              </div>
            ))}
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
      </section>

      <section className="card season-overview">
        <h2>The 4 seasonal palettes</h2>
        <div className="season-grid">
          <article className="season-card">
            <h4>Spring</h4>
            <p>Warm, light, fresh, bright</p>
            <img className="season-image" src={new URL('../../Spring.png', import.meta.url).href} alt="Spring palette" />
          </article>
          <article className="season-card">
            <h4>Summer</h4>
            <p>Cool, soft, muted, elegant</p>
            <img className="season-image" src={new URL('../../Summer.png', import.meta.url).href} alt="Summer palette" />
          </article>
          <article className="season-card">
            <h4>Autumn</h4>
            <p>Warm, earthy, rich, deep</p>
            <img className="season-image" src={new URL('../../Autumn.png', import.meta.url).href} alt="Autumn palette" />
          </article>
          <article className="season-card">
            <h4>Winter</h4>
            <p>Cool, bold, high-contrast, vivid</p>
            <img className="season-image" src={new URL('../../Winter.png', import.meta.url).href} alt="Winter palette" />
          </article>
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
        <Link to="/auth" className="btn primary">Start Your Color Analysis</Link>
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
