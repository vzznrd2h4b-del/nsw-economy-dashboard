// Loads the dashboard's data files and provides the small `dash` API the page uses:
// dash.data, dash.calc, dash.draw, dash.onData, dash.colors, dash.setLink.
(function () {
  const store = {};      // id -> {status, data, columns, meta}
  const calcs = {};      // id -> {inputs, fn, cache, key}
  const draws = [];      // [name, fn]
  const listeners = [];
  let manifest = null;

  const colors = ['var(--c1)', 'var(--c2)', 'var(--c3)', 'var(--c4)', 'var(--c5)', 'var(--c6)', 'var(--c7)', 'var(--c8)'];

  function calcData(id) {
    const c = calcs[id];
    const ins = c.inputs.map(i => data(i));
    if (ins.some(d => d.status === 'error' || d.status === 'missing')) return { status: 'error', data: [], columns: [], meta: [] };
    if (ins.some(d => d.status !== 'ok')) return { status: 'loading', data: [], columns: [], meta: [] };
    const key = ins.map(d => d.version || 0).join('|');
    if (c.key !== key) {
      try { const out = c.fn(...ins.map(d => d.data)); c.cache = { status: 'ok', data: out, columns: Array.isArray(out) && out.length ? Object.keys(out[0]) : [], meta: [], version: Date.now() }; }
      catch (e) { console.error('Calculation ' + id + ' failed', e); c.cache = { status: 'error', data: [], columns: [], meta: [] }; }
      c.key = key;
    }
    return c.cache;
  }
  function data(id) {
    if (calcs[id]) return calcData(id);
    return store[id] || { status: manifest ? 'missing' : 'loading', data: [], columns: [], meta: [] };
  }
  function isShown(el) { return !el.closest('[hidden]'); }
  function redraw() {
    listeners.forEach(fn => { try { fn(); } catch (e) { console.error(e); } });
    draws.forEach(([name, fn]) => document.querySelectorAll('[data-draw="' + name + '"]').forEach(el => {
      if (!isShown(el)) return;
      try { fn(el); } catch (e) { console.error('Drawing ' + name + ' failed', e); }
    }));
  }
  let queued = false;
  function schedule() { if (queued) return; queued = true; requestAnimationFrame(() => { queued = false; redraw(); }); }

  window.dash = {
    colors,
    data,
    calc: (id, o) => { calcs[id] = { inputs: o.inputs, fn: o.fn, title: o.title, description: o.description }; },
    loader: () => {},
    draw: (name, fn) => { if (typeof fn === 'function') draws.push([name, fn]); else schedule(); },
    onData: (fn) => { listeners.push(fn); },
    setLink: (name) => { try { history.replaceState(null, '', '#' + name); } catch (e) { /* ignore */ } },
    params: () => ({}), setParams: () => {}, resetParams: () => {}, refresh: () => {},
    manifest: () => manifest,
  };

  async function load() {
    try {
      const r = await fetch('data/manifest.json', { cache: 'no-cache' });
      manifest = await r.json();
    } catch (e) { console.error('Could not load manifest', e); manifest = { datasets: {} }; schedule(); return; }
    const v = encodeURIComponent(manifest.generated || '');
    await Promise.all(Object.keys(manifest.datasets).map(async (id) => {
      try {
        const r = await fetch('data/' + id + '.json?v=' + v);
        if (!r.ok) throw new Error(r.status);
        const j = await r.json(), rows = Array.isArray(j) ? j : (j.rows || j.data || []);
        store[id] = { status: 'ok', data: rows, columns: rows.length ? Object.keys(rows[0]) : [], meta: [], version: Date.now() };
      } catch (e) { console.error('Could not load ' + id, e); store[id] = { status: 'error', data: [], columns: [], meta: [] }; }
      schedule();
    }));
    schedule();
  }

  document.addEventListener('DOMContentLoaded', () => {
    schedule();
    new MutationObserver(schedule).observe(document.body, { attributes: true, attributeFilter: ['hidden'], subtree: true });
    let w = window.innerWidth;
    window.addEventListener('resize', () => { if (Math.abs(window.innerWidth - w) > 4) { w = window.innerWidth; schedule(); } });
    load();
  });
})();
