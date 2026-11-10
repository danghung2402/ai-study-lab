# AI 學習實驗室

給 AI 初學者的繁體中文學習網站，附中、英、越術語。以一份可執行的 `AGENTS.md` 維護內容與視覺規則，讓 AI 能在下一次協作中沿用同一套方法新增文章。

- **網站**：https://danghung2402.github.io/ai-study-lab/
- **原始碼**：https://github.com/danghung2402/ai-study-lab
- **AI 協作規則**：[AGENTS.md](AGENTS.md)
- **延伸驗證**：[docs/EXTENSION_DEMO.md](docs/EXTENSION_DEMO.md)

## 可以做什麼

9 篇學習筆記、3 條學習路徑、關鍵字搜尋、分類與收藏的組合篩選、收藏、完成進度、可重試的三選一測驗、範例複製。文章皆含固定六節與來源。進度和收藏只保存在目前瀏覽器，沒有伺服器同步、登入或模型 API。

內容範圍：提示設計、模型與 Harness 分工、專案規則、工具驗收、任務拆解、HTML/CSS/JS、GitHub Pages 及無障礙入門。網站以 AI 協助製作；學習內容依課堂講義與官方文件整理，不宣稱是教師原文。

## 本機執行

需要 Python 3.9 以上；建議 Python 3.12。建置不用安裝任何第三方套件。

```sh
python scripts/build.py
python scripts/check.py
python -m http.server 8099 --directory dist
```

開啟 `http://localhost:8099`。`node --check static/assets/app.js` 可額外檢查 JavaScript 語法，需要 Node.js。直接開啟 dist/index.html 可閱讀內容；建議以 HTTP 預覽，以正確測試跨頁儲存與剪貼簿功能。

## 目錄與內容延伸

```text
content/notes.json          唯一的筆記內容來源
content/example-note.json   可複製的新增筆記範例
templates/                 首頁、文章、路徑、規則、關於的共用樣板
static/assets/             全站樣式、互動程式與圖示
scripts/build.py           資料驗證與靜態建置
scripts/check.py           產出、內部連結及文章結構檢查
dist/                      可直接託管的產出；請勿手動修改
.github/workflows/         GitHub Pages 自動建置部署
```

新增內容前先讀 `AGENTS.md`，複製範例物件至 notes.json 並改用唯一 id。固定使用「核心概念、具體範例、動手練習、常見誤區、自我檢核、參考來源」六節。重新建置後，首頁、分類、搜尋、路徑、文章與相關筆記都會使用新資料；不需要另寫一頁 HTML。完整欄位規格與驗證流程在 AGENTS.md。

修改規則時，規則頁和公開的 AGENTS.md 會在下次建置同步更新。修改樣式或互動只需編輯 static/assets 中的共用檔案。

## GitHub Pages

Repository 的 Settings → Pages → Source 設為 **GitHub Actions**。推送 main 後，工作流程建置、檢查並發佈 dist。內部資源使用相對路徑，可在專案子目錄正常運作。部署方式依 [GitHub Pages 官方文件](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

## 來源與隱私

- 主要課堂來源為使用者提供的《09 換你當老闆：Agentic Work 與 AI 工作現場》PDF；文章標明來源頁碼，不公開上傳原始講義。
- 網站實作內容連結 [MDN](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started)、[GitHub Docs](https://docs.github.com/en/pages) 及 [AGENTS.md 格式說明](https://agents.md/)。
- 無分析追蹤、外部字型、CDN 或付費服務。公開網站不包含學號、密碼或私人課堂檔案。
- 測驗答案保存在靜態 HTML，僅供自學，不能作為保密考試系統。

## 作業繳交

`SUBMISSION_ZH_TW.txt` 含專案簡介、Repository、網站、AGENTS.md 及延伸方式五項內容。先填寫繳交標題的學校、系級與姓名，再依課程平台要求提交。`HUONG_DAN_VI.txt` 提供越南文操作說明。
