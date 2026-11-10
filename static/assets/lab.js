(() => {
  'use strict';
  const form = document.querySelector('#brief-form');
  if (!form || !window.StudyBrief) return;
  const core = window.StudyBrief;
  const scenarios = JSON.parse(document.querySelector('#scenario-data').textContent);
  const draftKey = 'ai-study-lab-brief-v1';
  const output = document.querySelector('#brief-output');
  const copyButton = document.querySelector('#copy-brief');
  const downloadButton = document.querySelector('#download-brief');
  const outputStatus = document.querySelector('#output-status');
  const draftStatus = document.querySelector('#draft-status');
  const errorStatus = document.querySelector('#brief-errors');
  const feedback = document.querySelector('#output-feedback');
  const buttons = [...document.querySelectorAll('[data-scenario]')];
  let scenarioId = scenarios[0].id;
  let storageAvailable = true;
  const read = () => Object.fromEntries(core.fields.map(field => [field.key, form.elements.namedItem(field.key).value]));
  function update() {
    const result = core.inspect(read());
    document.querySelector('#field-count').textContent = `已填 ${result.filled} / 6 項`;
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.scenario === scenarioId)));
    copyButton.disabled = true;
    downloadButton.disabled = true;
    outputStatus.textContent = output.value ? '內容已修改・請重新產生' : '尚未產生';
    feedback.textContent = '';
  }
  function persist() {
    if (storageAvailable) {
      try {
        localStorage.setItem(draftKey, JSON.stringify({ scenarioId, fields: read() }));
        draftStatus.textContent = '✓ 草稿已儲存在這個瀏覽器，不會上傳。';
        return;
      } catch (_) { storageAvailable = false; }
    }
    draftStatus.textContent = '瀏覽器無法儲存；本次仍可操作，重新載入後草稿不保留。';
  }
  function fillFields(values) {
    core.fields.forEach(field => {
      const control = form.elements.namedItem(field.key);
      control.value = typeof values[field.key] === 'string' ? values[field.key] : '';
      control.removeAttribute('aria-invalid');
    });
    errorStatus.textContent = '';
    update();
  }
  function loadScenario(id) {
    const scenario = scenarios.find(item => item.id === id);
    if (!scenario) return;
    scenarioId = id;
    fillFields(scenario.fields);
    persist();
  }
  fillFields(scenarios[0].fields);
  try {
    const draft = JSON.parse(localStorage.getItem(draftKey));
    if (draft && scenarios.some(item => item.id === draft.scenarioId) && draft.fields && typeof draft.fields === 'object') {
      scenarioId = draft.scenarioId;
      fillFields(draft.fields);
      draftStatus.textContent = '已恢復這個瀏覽器先前的草稿。';
    }
  } catch (_) { storageAvailable = false; persist(); }
  buttons.forEach(button => button.addEventListener('click', () => loadScenario(button.dataset.scenario)));
  document.querySelector('#reload-scenario').addEventListener('click', () => loadScenario(scenarioId));
  form.addEventListener('input', event => {
    event.target.removeAttribute('aria-invalid');
    errorStatus.textContent = '';
    update(); persist();
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    const data = read();
    const result = core.inspect(data);
    core.fields.forEach(field => form.elements.namedItem(field.key).removeAttribute('aria-invalid'));
    if (!result.valid) {
      result.missing.forEach(field => form.elements.namedItem(field.key).setAttribute('aria-invalid', 'true'));
      errorStatus.textContent = '請補上：' + result.missing.map(field => field.label).join('、') + '。';
      form.elements.namedItem(result.missing[0].key).focus();
      return;
    }
    errorStatus.textContent = '';
    output.value = core.format(data);
    outputStatus.textContent = '已產生・可複製或下載';
    copyButton.disabled = false;
    downloadButton.disabled = false;
    feedback.textContent = '交辦稿已產生。請先確認資料可取得，再交給你選用的 AI。';
  });
  copyButton.addEventListener('click', async () => {
    if (copyButton.disabled) return;
    try { await navigator.clipboard.writeText(output.value); feedback.textContent = '✓ 已複製交辦稿。'; }
    catch (_) { output.focus(); output.select(); feedback.textContent = '無法自動複製，已選取內容，請按 Ctrl+C 或使用複製功能。'; }
  });
  downloadButton.addEventListener('click', () => {
    if (downloadButton.disabled) return;
    const blob = new Blob([output.value], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url; link.download = `ai-brief-${scenarioId}.txt`;
    document.body.appendChild(link); link.click(); link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    feedback.textContent = '已建立文字檔下載，請查看瀏覽器下載項目。';
  });
})();
