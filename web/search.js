import { searchEntries } from './search-core.js';

const form = document.querySelector('#search-form');
const input = document.querySelector('#query');
const clear = document.querySelector('#clear-search');
const status = document.querySelector('#search-status');
const results = document.querySelector('#search-results');
const browse = document.querySelector('#browse-sources');
let composing = false;

try {
  const response = await fetch('search-index.json');
  if (!response.ok) throw new Error('Search index unavailable');
  const entries = await response.json();
  form.hidden = false;

  function render() {
    const query = input.value.trim();
    clear.hidden = !query;
    results.replaceChildren();
    results.hidden = !query;
    browse.hidden = Boolean(query);
    if (!query) {
      status.textContent = `${entries.filter((entry) => entry.kind === 'source').length} sources. Browse by section below.`;
      return;
    }
    const matches = searchEntries(entries, query);
    status.textContent = matches.length ? `${matches.length} results for “${query}”.` : `No results for “${query}”. Try a broader term or clear search.`;
    for (const entry of matches) {
      const item = document.createElement('article');
      item.className = 'source';
      const heading = document.createElement('h2');
      const link = document.createElement('a');
      link.href = entry.href;
      link.textContent = entry.title;
      heading.append(link);
      const description = document.createElement('p');
      description.textContent = [entry.provenance, entry.status_label, entry.tags.join(' / ')].filter(Boolean).join(' · ');
      item.append(heading, description);
      results.append(item);
    }
  }

  function commit() {
    const url = new URL(window.location.href);
    if (input.value.trim()) url.searchParams.set('q', input.value.trim());
    else url.searchParams.delete('q');
    history.replaceState(null, '', url);
    render();
  }

  input.value = new URLSearchParams(location.search).get('q') || '';
  input.addEventListener('compositionstart', () => { composing = true; });
  input.addEventListener('compositionend', () => { composing = false; commit(); });
  input.addEventListener('input', () => { if (!composing) commit(); });
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!composing) commit();
  });
  clear.addEventListener('click', () => {
    input.value = '';
    composing = false;
    commit();
    input.focus();
  });
  window.addEventListener('popstate', () => {
    input.value = new URLSearchParams(location.search).get('q') || '';
    render();
  });
  clear.disabled = false;
  render();
} catch {
  form.hidden = true;
  status.textContent = 'Search could not load. Browse all sources below, or reload to try again.';
  browse.hidden = false;
}
