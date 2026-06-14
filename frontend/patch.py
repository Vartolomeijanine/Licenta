import sys

content = open('src/pages/Home.jsx', 'r', encoding='utf-8').read()
old = '''        <div className="hero-preview">
            <div className="preview-uploader">
              <div className="preview-title">Upload a clear selfie</div>
              <div style={{height:12}} />
              <img className="preview-face-image" src={new URL('../../emma.webp', import.meta.url).href} alt="preview face" />
              <button className="btn outline" type="button">Upload Photo</button>
            </div>
          <div className="preview-season-list">
            <div className="preview-season-heading">The 4 Seasonal Palettes</div>
            <div className="preview-season-item"><ColorPalette season="spring" /></div>
            <div className="preview-season-item"><ColorPalette season="summer" /></div>
            <div className="preview-season-item"><ColorPalette season="autumn" /></div>
            <div className="preview-season-item"><ColorPalette season="winter" /></div>
          </div>
        </div>'''

new = '''        <div className="hero-preview">
          <img className="preview-face-image" src={new URL('../../emma.webp', import.meta.url).href} alt="preview face" />
          <div className="preview-season-list">
            <ColorPalette season="spring" />
            <ColorPalette season="summer" />
            <ColorPalette season="autumn" />
            <ColorPalette season="winter" />
          </div>
        </div>'''
old = old.replace('\r\n', '\n')
content = content.replace('\r\n', '\n')
if old in content:
    content = content.replace(old, new)
    open('src/pages/Home.jsx', 'w', encoding='utf-8').write(content)
    print('replaced hero-preview')
else:
    print('hero-preview not found')

import re
old_h1 = '''        <div className="hero-copy">
          
          <h1>
            Discover Your Best Colors with
            <span> AI Seasonal Analysis</span>
          </h1>'''
new_h1 = '''        <div className="hero-copy">
          <h1>
            Discover Your Best Colors
          </h1>'''
if old_h1 in content:
    content = content.replace(old_h1, new_h1)
    open('src/pages/Home.jsx', 'w', encoding='utf-8').write(content)
    print('replaced h1')

if '<p>Warm, light, fresh, bright</p>' in content:
    content = re.sub(r'<p>([^<]+)</p><ColorPalette', r'<ColorPalette', content)
    open('src/pages/Home.jsx', 'w', encoding='utf-8').write(content)
    print('replaced season para')

