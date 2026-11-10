/* Pure formatting rules shared by the browser and Node checks. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.StudyBrief = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const fields = Object.freeze([
    { key: 'goal', label: '任務目標', vi: 'Mục tiêu', help: '你希望 AI 幫你完成什麼？' },
    { key: 'audience', label: '使用對象', vi: 'Đối tượng', help: '誰會閱讀或使用這份成果？' },
    { key: 'sources', label: '輸入與資料來源', vi: 'Tài liệu đầu vào', help: '指出檔案、頁碼、網址或已提供的內容。' },
    { key: 'deliverable', label: '交付成果', vi: 'Sản phẩm cần nhận', help: '說明格式、結構與數量，讓成果看得見。' },
    { key: 'constraints', label: '限制與規則', vi: 'Giới hạn và quy tắc', help: '例如語言、來源範圍與禁止編造。每點一行。' },
    { key: 'acceptance', label: '驗收標準', vi: 'Tiêu chí kiểm tra', help: '完成後，你會怎麼確認做對了？每點一行。' }
  ]);
  function inspect(input) {
    const missing = fields.filter(field => typeof input?.[field.key] !== 'string' || !input[field.key].trim());
    return { valid: missing.length === 0, filled: fields.length - missing.length, missing: missing.map(field => ({ ...field })) };
  }
  function lines(text) { return text.split(/\r?\n/).map(line => line.trim()).filter(Boolean); }
  function format(input) {
    if (!inspect(input).valid) throw new Error('請先填好六個欄位。');
    const blocks = fields.map(field => {
      const text = input[field.key].trim();
      let content = text;
      if (field.key === 'constraints') content = lines(text).map(line => `- ${line}`).join('\n');
      if (field.key === 'acceptance') content = lines(text).map((line, index) => `${index + 1}. ${line}`).join('\n');
      return `【${field.label}】\n${content}`;
    });
    return '請依下列資訊完成工作。\n\n' + blocks.join('\n\n')
      + '\n\n【執行與回報】\n先確認能取得指定資料；不足之處請明確列出。\n完成後依驗收標準逐項回報，區分已驗證、未驗證與待確認事項。\n';
  }
  return Object.freeze({ fields, inspect, format });
});
