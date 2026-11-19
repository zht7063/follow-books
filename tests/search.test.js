import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { normalize, searchEntries } from '../web/search-core.js';

const entries = JSON.parse(readFileSync(new URL('../site/search-index.json', import.meta.url), 'utf8'));
test('search includes chapter editorial, titles and tags', () => {
  assert(searchEntries(entries, 'learning').some((e) => e.kind === 'chapter'));
  assert(searchEntries(entries, 'Kortex').some((e) => e.kind === 'source'));
  assert(searchEntries(entries, 'generalist').some((e) => e.id === 'writing-and-attention'));
});
test('empty and no-results queries return an empty list', () => {
  assert.deepEqual(searchEntries(entries, ' '), []);
  assert.deepEqual(searchEntries(entries, 'there-is-no-such-article-3586'), []);
});
test('matching normalizes case and fullwidth text, ANDs terms, and handles Chinese', () => {
  assert.equal(normalize(' ＡＩ '), 'ai');
  assert(searchEntries(entries, ' ＫＯＲＴＥＸ ').length > 0);
  assert(searchEntries(entries, 'AI work').every((e) => /ai/i.test([e.title, e.text, ...e.tags].join(' '))));
  assert(searchEntries(entries, '写作').length > 0);
});
test('query markup is treated as plain text', () => {
  assert.deepEqual(searchEntries(entries, '<script>alert(1)</script>'), []);
});

// Minimal offline DOM fixture: exercises the shipped controller without a browser.
class Element {
  constructor() { this.hidden = true; this.value = ''; this.textContent = ''; this.children = []; this.listeners = {}; this.disabled = true; }
  addEventListener(type, callback) { this.listeners[type] = callback; }
  append(...children) { this.children.push(...children); }
  replaceChildren() { this.children = []; }
  focus() { this.focused = true; }
  fire(type) { this.listeners[type]?.({ preventDefault() {} }); }
}

async function controllerFixture(query = '', fail = false) {
  const elements = Object.fromEntries(['search-form', 'query', 'clear-search', 'search-status', 'search-results', 'browse-sources'].map((id) => [id, new Element()]));
  globalThis.document = { querySelector: (selector) => elements[selector.slice(1)], createElement: () => new Element() };
  const location = new URL(`http://localhost/catalog.html${query}`);
  globalThis.location = location;
  globalThis.window = { location, addEventListener() {} };
  globalThis.history = { replaceState: (_, __, url) => { location.href = url.href; } };
  globalThis.fetch = async () => ({ ok: !fail, json: async () => entries });
  await import(`../web/search.js?fixture=${query}&fail=${fail}`);
  return { elements, location };
}

test('controller restores URL query, reports results, and clear restores browse and focus', async () => {
  const { elements: e, location } = await controllerFixture('?q=Kortex');
  assert.equal(e['search-form'].hidden, false);
  assert.equal(e.query.value, 'Kortex');
  assert.equal(e['clear-search'].disabled, false);
  assert.equal(e['browse-sources'].hidden, true);
  assert(e['search-results'].children.length > 0);
  e['clear-search'].fire('click');
  assert.equal(e.query.value, '');
  assert.equal(e['browse-sources'].hidden, false);
  assert.equal(e.query.focused, true);
  assert.equal(location.search, '');
});

test('controller defers IME composition and reports a no-results state on completion', async () => {
  const { elements: e, location } = await controllerFixture('?q=writing');
  e.query.fire('compositionstart');
  e.query.value = 'no-such-article-3586';
  e.query.fire('input');
  assert.equal(location.searchParams.get('q'), 'writing');
  e.query.fire('compositionend');
  assert.equal(location.searchParams.get('q'), 'no-such-article-3586');
  assert.match(e['search-status'].textContent, /No results/);
  assert.equal(e['search-results'].children.length, 0);
});

test('controller leaves browsing available if search index fails', async () => {
  const { elements: e } = await controllerFixture('?q=AI', true);
  assert.equal(e['search-form'].hidden, true);
  assert.equal(e['browse-sources'].hidden, false);
  assert.match(e['search-status'].textContent, /Search could not load/);
});
