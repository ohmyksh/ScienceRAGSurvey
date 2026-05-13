// Browse page: load papers.json and apply client-side filters.
(async () => {
  const cardsEl = document.getElementById('cards');
  const emptyEl = document.getElementById('empty');
  const countEl = document.getElementById('result-count');
  const q = document.getElementById('q');
  const fCell = document.getElementById('f-cell');
  const fDomain = document.getElementById('f-domain');
  const fType = document.getElementById('f-type');
  const fYear = document.getElementById('f-year');
  const fReset = document.getElementById('f-reset');

  const DOMAIN_LABELS = {bio:'Biology', chem:'Chemistry', medical:'Medicine', material:'Materials Science', physics:'Physics', earth:'Earth Science', astronomy:'Astronomy', Quantum:'Quantum', general:'General Science'};
  const DOMAIN_EMOJI  = {bio:'🧬', chem:'⚗️', medical:'🩺', material:'🪨', physics:'⚛️', earth:'🌍', astronomy:'🔭', Quantum:'🌀', general:'📚'};
  const TYPE_LABELS = {Method:'Methods', benchmark:'Benchmarks', dataset:'Datasets', summary:'Surveys'};

  const esc = s => (s == null ? '' : String(s).replace(/[&<>"']/g, c => ({
    '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
  }[c])));

  function paperCard(p) {
    const title = esc(p.title || p.bib_key || '?');
    const url = p.paper_link || '';
    const titleHtml = url
      ? `<a href="${esc(url)}" target="_blank" rel="noopener">${title} ↗</a>`
      : title;

    const metaParts = [];
    if (p.method && p.method !== p.title) metaParts.push(`<span class="meta-method">${esc(p.method)}</span>`);
    if (p.venue) metaParts.push(`<span class="meta-venue">${esc(p.venue)}</span>`);
    if (p.year) metaParts.push(`<span class="meta-year">${esc(p.year)}</span>`);
    const meta = metaParts.join(' · ');

    let note = (p.note || p.ko_note || '').trim();
    if (note.length > 280) note = note.slice(0, 277) + '…';

    const tags = [];
    (p.ko_cells || []).forEach(c => tags.push(`<a href="cell/${c}.html" class="tag tag-cell">${esc(c)}</a>`));
    (p.domain || []).forEach(d => tags.push(`<a href="domain/${d}.html" class="tag tag-domain">${DOMAIN_EMOJI[d] || ''}${esc(DOMAIN_LABELS[d] || d)}</a>`));
    if (p.type && p.type !== 'unknown') tags.push(`<a href="topics/${p.type.toLowerCase()}.html" class="tag tag-type">${esc(TYPE_LABELS[p.type] || p.type)}</a>`);
    (p.modality || []).forEach(m => { if (m && m !== 'Text') tags.push(`<span class="tag tag-mod">${esc(m)}</span>`); });
    if (p.cross_source) tags.push('<span class="tag tag-xs">★ cross-source</span>');

    return `<article class="card">
      <h3 class="card-title">${titleHtml}</h3>
      ${meta ? `<div class="card-meta">${meta}</div>` : ''}
      ${note ? `<p class="card-note">${esc(note)}</p>` : ''}
      <div class="card-tags">${tags.join('')}</div>
    </article>`;
  }

  let allPapers = [];
  try {
    const res = await fetch('data/papers.json');
    allPapers = await res.json();
  } catch (e) {
    cardsEl.innerHTML = `<p class="empty">Failed to load papers.json: ${esc(e.message)}</p>`;
    return;
  }

  function yearKey(p) {
    const y = parseInt(p.year);
    return Number.isFinite(y) ? -y : 0;
  }

  function applyFilters() {
    const query = (q.value || '').trim().toLowerCase();
    const cell = fCell.value;
    const dom = fDomain.value;
    const typ = fType.value;
    const yr = fYear.value;

    const out = allPapers.filter(p => {
      if (cell && !(p.ko_cells || []).includes(cell)) return false;
      if (dom && !(p.domain || []).includes(dom)) return false;
      if (typ && p.type !== typ) return false;
      if (yr) {
        const py = parseInt(p.year);
        if (yr === '<2023') {
          if (!Number.isFinite(py) || py >= 2023) return false;
        } else {
          if (String(py) !== yr) return false;
        }
      }
      if (query) {
        const hay = [
          p.title, p.method, p.note, p.ko_note, p.venue, p.bib_key,
          p.db_name, p.retriever, p.generator,
          (p.ko_cells || []).join(' '),
          (p.domain || []).map(d => DOMAIN_LABELS[d] || d).join(' '),
          (p.modality || []).join(' '),
        ].filter(Boolean).join(' ').toLowerCase();
        for (const tok of query.split(/\s+/).filter(Boolean)) {
          if (!hay.includes(tok)) return false;
        }
      }
      return true;
    });
    out.sort((a, b) => yearKey(a) - yearKey(b));

    countEl.textContent = `${out.length} / ${allPapers.length}`;
    if (out.length === 0) {
      cardsEl.innerHTML = '';
      emptyEl.hidden = false;
    } else {
      emptyEl.hidden = true;
      cardsEl.innerHTML = out.map(paperCard).join('');
    }

    // sync URL
    const params = new URLSearchParams();
    if (query) params.set('q', q.value);
    if (cell) params.set('cell', cell);
    if (dom) params.set('domain', dom);
    if (typ) params.set('type', typ);
    if (yr) params.set('year', yr);
    const qs = params.toString();
    history.replaceState(null, '', qs ? '?' + qs : window.location.pathname);
  }

  // Initialize from URL params
  const params = new URLSearchParams(window.location.search);
  if (params.get('q')) q.value = params.get('q');
  if (params.get('cell')) fCell.value = params.get('cell');
  if (params.get('domain')) fDomain.value = params.get('domain');
  if (params.get('type')) fType.value = params.get('type');
  if (params.get('year')) fYear.value = params.get('year');

  [q, fCell, fDomain, fType, fYear].forEach(el => el.addEventListener('input', applyFilters));
  fReset.addEventListener('click', () => {
    q.value = ''; fCell.value = ''; fDomain.value = ''; fType.value = ''; fYear.value = '';
    applyFilters();
  });

  applyFilters();
})();
