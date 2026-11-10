/* Browser-only state; reading content never depends on JavaScript. */
(() => {
  'use strict';
  const storageKey = 'ai-study-lab-v1';
  const validIds = new Set();
  document.querySelectorAll('[data-bookmark], [data-complete], [data-path-note]').forEach(el => {
    validIds.add(el.dataset.bookmark || el.dataset.complete || el.dataset.pathNote);
  });
  let state = { saved: [], completed: [] };
  let canPersist = true;
  const toastEl = document.querySelector('.toast');
  let toastTimer;
  function toast(message) {
    if (!toastEl) return;
    clearTimeout(toastTimer);
    toastEl.textContent = message;
    toastEl.classList.add('show');
    toastTimer = setTimeout(() => toastEl.classList.remove('show'), 3500);
  }
  function readState(raw) {
    try {
      const parsed = JSON.parse(raw);
      return {
        saved: Array.isArray(parsed?.saved) ? [...new Set(parsed.saved.filter(x => typeof x === 'string'))] : [],
        completed: Array.isArray(parsed?.completed) ? [...new Set(parsed.completed.filter(x => typeof x === 'string'))] : []
      };
    } catch (_) { return { saved: [], completed: [] }; }
  }
  try { state = readState(localStorage.getItem(storageKey)); }
  catch (_) { canPersist = false; }
  function persist() {
    if (canPersist) {
      try { localStorage.setItem(storageKey, JSON.stringify(state)); return true; }
      catch (_) { canPersist = false; }
    }
    return false;
  }
  function updateStateUI() {
    document.querySelectorAll('.saved-count').forEach(el => { el.textContent = state.saved.length; });
    document.querySelectorAll('[data-bookmark]').forEach(button => {
      const saved = state.saved.includes(button.dataset.bookmark);
      button.setAttribute('aria-pressed', String(saved));
      if (button.classList.contains('card-bookmark')) {
        button.textContent = saved ? '★' : '☆';
        button.setAttribute('aria-label', `${saved ? '取消收藏' : '收藏'}：${button.dataset.title}`);
      } else { button.textContent = saved ? '★ 已收藏・按此取消' : '☆ 收藏筆記'; }
    });
    document.querySelectorAll('[data-complete]').forEach(button => {
      const done = state.completed.includes(button.dataset.complete);
      button.setAttribute('aria-pressed', String(done));
      button.textContent = done ? '✓ 已完成・按此取消' : '標記為已完成 ✓';
    });
    document.querySelectorAll('[data-card]').forEach(card => {
      const status = card.querySelector('.card-status');
      const done = state.completed.includes(card.dataset.id);
      status.hidden = !done;
      status.textContent = done ? '✓ 已完成這篇筆記' : '';
    });
    document.querySelectorAll('[data-path-note]').forEach(item => {
      item.querySelector('.path-note-status').textContent = state.completed.includes(item.dataset.pathNote) ? '✓ 已完成' : '待探索';
    });
    // Home renders every note, so only current content IDs count toward its total.
    const count = state.completed.filter(id => validIds.has(id)).length;
    const total = Number(document.body.dataset.total) || 1;
    document.querySelectorAll('.done-count').forEach(el => { el.textContent = count; });
    document.querySelectorAll('.progress-track').forEach(el => {
      el.setAttribute('aria-valuenow', String(count));
      el.firstElementChild.style.width = `${Math.min(100, count / total * 100)}%`;
    });
  }
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.main-nav');
  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('open', open);
  });
  nav?.addEventListener('click', event => {
    if (event.target.closest('a')) { menu?.setAttribute('aria-expanded', 'false'); nav.classList.remove('open'); }
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu?.getAttribute('aria-expanded') === 'true') {
      menu.setAttribute('aria-expanded', 'false'); nav.classList.remove('open'); menu.focus();
    }
  });

  const cards = [...document.querySelectorAll('[data-card]')];
  const search = document.querySelector('#note-search');
  const tabs = [...document.querySelectorAll('.category-tab[data-category]')];
  const savedFilter = document.querySelector('#saved-filter');
  const query = new URLSearchParams(location.search);
  let category = tabs.some(tab => tab.dataset.category === query.get('category')) ? query.get('category') : 'all';
  let savedOnly = query.get('saved') === '1';
  function filterCards() {
    if (!search) return;
    const term = search.value.trim().toLocaleLowerCase();
    let shown = 0;
    cards.forEach(card => {
      const visible = (category === 'all' || card.dataset.category === category)
        && (!savedOnly || state.saved.includes(card.dataset.id))
        && (!term || card.dataset.search.toLocaleLowerCase().includes(term));
      card.hidden = !visible;
      if (visible) shown++;
    });
    tabs.forEach(tab => {
      const active = tab.dataset.category === category;
      tab.classList.toggle('active', active);
      tab.setAttribute('aria-pressed', String(active));
    });
    savedFilter.setAttribute('aria-pressed', String(savedOnly));
    savedFilter.textContent = savedOnly ? '★ 只看收藏' : '☆ 只看收藏';
    document.querySelector('#results-count').textContent = `顯示 ${shown} / ${cards.length} 篇筆記`;
    document.querySelector('#empty-state').hidden = shown !== 0;
  }
  search?.addEventListener('input', filterCards);
  tabs.forEach(tab => tab.addEventListener('click', () => { category = tab.dataset.category; filterCards(); }));
  savedFilter?.addEventListener('click', () => { savedOnly = !savedOnly; filterCards(); });
  document.querySelector('#reset-filters')?.addEventListener('click', () => {
    category = 'all'; savedOnly = false; search.value = ''; filterCards(); search.focus();
  });

  document.addEventListener('click', async event => {
    const bookmark = event.target.closest('[data-bookmark]');
    const complete = event.target.closest('[data-complete]');
    if (bookmark || complete) {
      const button = bookmark || complete;
      const key = bookmark ? 'saved' : 'completed';
      const id = bookmark ? button.dataset.bookmark : button.dataset.complete;
      const active = !state[key].includes(id);
      state[key] = active ? [...state[key], id] : state[key].filter(x => x !== id);
      const persisted = persist();
      updateStateUI(); filterCards();
      toast((bookmark ? (active ? '已加入收藏' : '已取消收藏') : (active ? '已記錄完成進度，繼續前進！' : '已取消完成標記'))
        + (persisted ? '' : '。瀏覽器無法儲存，重新載入後將不保留。'));
    }
    const check = event.target.closest('.check-answer');
    if (check) {
      const box = check.closest('.quiz-box');
      const selected = box.querySelector('input:checked');
      const feedback = box.querySelector('.quiz-feedback');
      if (!selected) { feedback.textContent = '請先選擇一個答案。'; feedback.className = 'quiz-feedback incorrect'; return; }
      const correct = Number(selected.value) === Number(box.dataset.answer);
      feedback.className = `quiz-feedback ${correct ? 'correct' : 'incorrect'}`;
      feedback.textContent = `${correct ? '✓ 答對了！' : '再想一想，可以換個答案重試。'} ${box.dataset.explanation}`;
    }
    const copy = event.target.closest('.copy-code');
    if (copy) {
      const text = copy.closest('.code-block').querySelector('code').textContent;
      try { await navigator.clipboard.writeText(text); toast('已複製範例'); }
      catch (_) {
        const range = document.createRange();
        range.selectNodeContents(copy.closest('.code-block').querySelector('code'));
        const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
        toast('無法自動複製，已選取範例，請使用複製快捷鍵。');
      }
    }
  });
  window.addEventListener('storage', event => {
    if (event.key === storageKey || event.key === null) { state = readState(event.newValue); updateStateUI(); filterCards(); }
  });
  updateStateUI(); filterCards();
  if (!canPersist) toast('瀏覽器無法儲存，收藏和進度只保留於本次頁面。');
})();
