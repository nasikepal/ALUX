// Runs in Figma Desktop, where locally installed fonts are visible (the remote MCP can't see them).
// Swaps every ALUX/* text style and every Figtree text on "ALUX —" pages to Gilroy.
const FAMILY = 'Gilroy';
const MAP = { Thin: 'Light', ExtraLight: 'Light', Light: 'Light', Regular: 'Regular', Medium: 'Medium',
              SemiBold: 'Bold', Bold: 'Bold', ExtraBold: 'Heavy', Black: 'Heavy' };
const target = (style) => ({ family: FAMILY, style: MAP[style.replace(/\s+/g, '')] || 'Regular' });

async function main() {
  const available = (await figma.listAvailableFontsAsync()).filter(f => f.fontName.family === FAMILY).map(f => f.fontName.style);
  const needed = [...new Set(Object.values(MAP))];
  const missing = needed.filter(s => !available.includes(s));
  if (missing.length) {
    figma.closePlugin(`Gilroy belum terbaca Figma (kurang: ${missing.join(', ')}). Install font Gilroy_fixed, restart Figma, jalankan lagi.`);
    return;
  }
  for (const s of needed) await figma.loadFontAsync({ family: FAMILY, style: s });

  let styles = 0;
  for (const st of await figma.getLocalTextStylesAsync()) {
    if (!st.name.startsWith('ALUX/') || st.fontName.family === FAMILY) continue;
    await figma.loadFontAsync(st.fontName);
    st.fontName = target(st.fontName.style);
    st.description = 'ALUX video graphics · 3840×2160 · Gilroy';
    styles++;
  }

  let nodes = 0;
  for (const page of figma.root.children.filter(p => p.name.startsWith('ALUX —'))) {
    await page.loadAsync();
    for (const t of page.findAllWithCriteria({ types: ['TEXT'] })) {
      if (t.textStyleId && typeof t.textStyleId === 'string') continue; // follows its style
      const segs = t.getStyledTextSegments(['fontName']);
      if (!segs.some(s => s.fontName.family === 'Figtree')) continue;
      for (const s of segs) await figma.loadFontAsync(s.fontName);
      for (const s of segs) if (s.fontName.family === 'Figtree') t.setRangeFontName(s.start, s.end, target(s.fontName.style));
      nodes++;
    }
  }
  figma.closePlugin(`ALUX font: ${styles} text style + ${nodes} teks diganti ke Gilroy.`);
}
main().catch(e => figma.closePlugin('Gagal: ' + e.message));
