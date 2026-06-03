css = """
/* Added for Market Stabilization Engine V2 */
.marker-hover {
  transition: r 0.2s ease, opacity 0.2s ease;
}
g:hover .marker-hover {
  r: 8px;
  opacity: 1 !important;
}
"""
with open(r'd:\2026\pangan-ai\panganai\frontend\src\index.css', 'a', encoding='utf-8') as f:
    f.write(css)
