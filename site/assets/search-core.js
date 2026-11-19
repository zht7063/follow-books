// Pure matching logic shared with the offline Node tests.
export function normalize(value) {
  return String(value).normalize('NFKC').toLocaleLowerCase('en').trim();
}

export function searchEntries(entries, query) {
  const terms = normalize(query).split(/\s+/u).filter(Boolean);
  if (!terms.length) return [];
  return entries.filter((entry) => {
    const haystack = normalize([entry.title, entry.text, ...entry.tags].join(' '));
    return terms.every((term) => haystack.includes(term));
  });
}
