/* The public guide stores no participant information and makes no network requests. */
document.documentElement.classList.add('js');
const topLink = document.querySelector('.to-top');
const updateTopLink = () => { if (topLink) topLink.dataset.visible = String(window.scrollY > 300); };
window.addEventListener('scroll', updateTopLink, { passive: true });
updateTopLink();
const allPages = document.querySelector('.all-pages');
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && allPages?.open) {
    allPages.open = false;
    allPages.querySelector('summary')?.focus();
  }
});
document.addEventListener('click', event => {
  if (allPages?.open && !allPages.contains(event.target)) allPages.open = false;
});
const filters = document.querySelector('[data-filters]');
const cards = [...document.querySelectorAll('[data-chapter-card]')];
const filterCount = document.querySelector('[data-filter-count]');
if (filters) {
  filters.hidden = false;
  filterCount.hidden = false;
  const update = chosen => {
    let count = 0;
    cards.forEach(card => { card.hidden = chosen !== 'All' && card.dataset.theme !== chosen; if (!card.hidden) count++; });
    filters.querySelectorAll('button').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === chosen)));
    filterCount.textContent = `${count} ${count === 1 ? 'chapter' : 'chapters'} shown`;
  };
  filters.addEventListener('click', event => { const button = event.target.closest('[data-filter]'); if (button) update(button.dataset.filter); });
  update('All');
}
const examples = {
  music: { title: 'Find what makes the music yours', before: 'Before: what kind of company, sound and setting would you enjoy?', after: 'After: what mattered most — the music, the people, the place or the chance to take part?', href: 'music-sport-culture-nature.html#p104', link: 'Read the music encounter ↗' },
  nature: { title: 'A quiet day can be enough', before: 'Before: would you like company, solitude, a gentle walk or simply somewhere to sit?', after: 'After: what restored your attention? What did the place ask of you, and what would you leave unrecorded?', href: 'music-sport-culture-nature.html#p139', link: 'Read the nature encounter ↗' },
  learning: { title: 'Have a go, with room to learn', before: 'Before: what skill interests you, what support would help and how much challenge would you choose?', after: 'After: what did an instructor notice, what did it feel like to you, and what would you practise next?', href: 'music-sport-culture-nature.html#p115', link: 'Read the sport encounter ↗' }
};
const output = document.querySelector('[data-pace-output]');
document.querySelectorAll('[data-pace]').forEach(button => button.addEventListener('click', () => {
  const example = examples[button.dataset.pace];
  document.querySelectorAll('[data-pace]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  output.replaceChildren();
  const heading = document.createElement('h3'); heading.textContent = example.title; output.append(heading);
  for (const text of [example.before, example.after]) { const paragraph = document.createElement('p'); paragraph.textContent = text; output.append(paragraph); }
  const link = document.createElement('a'); link.href = example.href; link.textContent = example.link; output.append(link);
}));
const sourceSearch = document.querySelector('[data-source-search]');
if (sourceSearch) {
  sourceSearch.hidden = false;
  const entries = [...document.querySelectorAll('[data-source-entry]')];
  const input = sourceSearch.querySelector('input');
  const status = sourceSearch.querySelector('[data-source-count]');
  const empty = document.querySelector('[data-source-empty]');
  const update = () => {
    const query = input.value.trim().toLocaleLowerCase();
    let count = 0;
    entries.forEach(entry => { entry.hidden = !entry.textContent.toLocaleLowerCase().includes(query); if (!entry.hidden) count++; });
    status.textContent = `${count} ${count === 1 ? 'reference' : 'references'} shown`;
    empty.hidden = count !== 0;
  };
  input.addEventListener('input', update); update();
}
