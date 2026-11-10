# AI 學習實驗室

給在台灣以中文修課的越南學生與 AI 初學者使用的學習工具。以中文筆記、中英越術語和六欄交辦練習，協助把「看懂講義」接到「交代清楚、查證成果」。`AGENTS.md` 維護內容、視覺與驗收方式，讓 AI 能接續新增文章及練習情境。

- **網站**：https://danghung2402.github.io/ai-study-lab/
- **原始碼**：https://github.com/danghung2402/ai-study-lab
- **AI 協作規則**：[AGENTS.md](AGENTS.md)
- **延伸驗證**：[docs/EXTENSION_DEMO.md](docs/EXTENSION_DEMO.md)
- **交辦練習室**：https://danghung2402.github.io/ai-study-lab/lab.html
- **規則與成果的對應**：https://danghung2402.github.io/ai-study-lab/evidence.html

## 可以做什麼

10 篇學習筆記、3 條學習路徑、關鍵字搜尋、分類與收藏的組合篩選、收藏、完成進度、可重試的三選一測驗、範例複製。文章皆含固定六節與來源。

交辦練習室有「讀懂中文講義」「新增一篇網站筆記」「準備專案交接」三個情境。使用者編輯目標、對象、來源、成果、限制與驗收六欄後，產生可複製及下載的文字；空白欄位會被指出，修改後必須重新產生，避免帶走舊輸出。草稿能跨重新載入保留。這是瀏覽器內的規則工具，沒有呼叫模型或自動翻譯。

專案驗證頁展示內容延伸、情境延伸、共用檔案雜湊比對與規則對應。進度、收藏及草稿只保存在目前瀏覽器，不會上傳或跨裝置同步。

內容範圍：提示設計、模型與 Harness 分工、專案規則、工具驗收、任務拆解、HTML/CSS/JS、GitHub Pages 及無障礙入門。網站以 AI 協助製作；學習內容依課堂講義與官方文件整理，不宣稱是教師原文。

## 本機執行

需要 Python 3.9 以上；建議 Python 3.12。建置不用安裝任何第三方套件。

```sh
python scripts/build.py
python scripts/check.py
node scripts/test_brief.cjs
python -m http.server 8099 --directory dist
```

開啟 `http://localhost:8099`。Node.js 用於互動邏輯檢查；`node --check static/assets/app.js` 和 `node --check static/assets/lab.js` 可檢查 JavaScript 語法。直接開啟 dist/index.html 可閱讀內容；建議以 HTTP 預覽，以正確測試跨頁儲存與剪貼簿功能。

## 目錄與內容延伸

```text
content/notes.json          唯一的筆記內容來源
content/example-note.json   可複製的新增筆記範例
content/scenarios.json      三個情境與六欄交辦範例
content/proof.json          程式實際執行產生的延伸證據
templates/                 首頁、文章、路徑、規則、關於的共用樣板
static/assets/             全站樣式、互動程式與圖示
scripts/build.py           資料驗證與靜態建置
scripts/check.py           產出、內部連結及文章結構檢查
scripts/prove_extension.py  重建延伸前後版本與情境擴充
scripts/test_brief.cjs      交辦稿生成與錯誤輸入測試
dist/                      可直接託管的產出；請勿手動修改
.github/workflows/         GitHub Pages 自動建置部署
```

新增內容前先讀 `AGENTS.md`，複製範例物件至 notes.json 並改用唯一 id。固定使用「核心概念、具體範例、動手練習、常見誤區、自我檢核、參考來源」六節。重新建置後，首頁、分類、搜尋、路徑、文章與相關筆記都會使用新資料；不需要另寫一頁 HTML。完整欄位規格與驗證流程在 AGENTS.md。

修改規則時，規則頁和公開的 AGENTS.md 會在下次建置同步更新。修改樣式或互動只需編輯 static/assets 中的共用檔案。

新增練習情境只需在 `content/scenarios.json` 加入符合規格的物件，不必另寫表單、下載功能或檢查程式。

## 重現延伸證據

```sh
python scripts/prove_extension.py
python scripts/build.py
python scripts/check.py
```

程式在忽略的 `verification/` 目錄重建 9 篇與 10 篇版本，檢查每頁與連結，再於隔離版本試加第四個情境。它確認 20 個共用檔案完全相同，拒絕重複 id、缺漏概念和無效測驗答案，並將真實結果記錄為 proof.json。正式網站保留三個情境。此為可重現程式與人工操作驗證，不聲稱獨立 AI 的盲測。

如果修改內容或共用程式，應重新執行以上命令。CI 的 `--check` 模式會重新驗證並拒絕過期證據；沒有執行的檢查不能標為通過。

## GitHub Pages

Repository 的 Settings → Pages → Source 設為 **GitHub Actions**。推送 main 後，工作流程建置、檢查並發佈 dist。內部資源使用相對路徑，可在專案子目錄正常運作。部署方式依 [GitHub Pages 官方文件](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

## 來源與隱私

- 主要課堂來源為使用者提供的《09 換你當老闆：Agentic Work 與 AI 工作現場》PDF；文章標明來源頁碼，不公開上傳原始講義。
- 網站實作內容連結 [MDN](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started)、[GitHub Docs](https://docs.github.com/en/pages) 及 [AGENTS.md 格式說明](https://agents.md/)。
- 無分析追蹤、外部字型、CDN 或付費服務。公開網站不包含學號、密碼或私人課堂檔案。
- 測驗答案保存在靜態 HTML，僅供自學，不能作為保密考試系統。

## 作業繳交

`SUBMISSION_ZH_TW.txt` 含專案簡介、Repository、網站、AGENTS.md 及延伸方式五項內容。先填寫繳交標題的學校、系級與姓名，再依課程平台要求提交。`HUONG_DAN_VI.txt` 提供越南文操作說明。
