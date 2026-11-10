# 延伸驗證：只新增一筆內容，網站就接著生長

驗證日期：2026-11-10。本紀錄說明本次實際操作，不代表另一個獨立 AI 在全新對話中完成了測試。

## 基準

最初版本有 8 篇筆記及 12 個 HTML 頁面。執行建置與檢查，結果為：

```text
BUILD OK: 8 notes, 12 HTML pages
CHECK OK: 12 pages, 267 local links/assets
```

## 依規則新增

依 `AGENTS.md` 的格式，使用 `content/example-note.json` 中的「把大任務拆成小步驟」物件，加入 `content/notes.json` 的代理工作流類別。此步驟只修改內容來源，未編輯任何 HTML 樣板、CSS、JavaScript 或建置器。

新增文章 id 為 `task-planning`。它具備兩個學習目標、兩段概念、具體示例、四步練習、兩項誤區、三選一測驗、課堂來源與越南文術語。

## 產出與實際檢查

```text
EXTENSION: 8 -> 9 notes; changed only content/notes.json; inserted task-planning
BUILD OK: 9 notes, 13 HTML pages
CHECK OK: 13 pages, 293 local links/assets,
          all 6 sections per note, published rules match source
```

瀏覽器實際操作確認：

- 首頁總數變成 9，代理工作流分類變成 4 篇。
- 搜尋「大任務」顯示 1 / 9 篇，並能開啟 `notes/task-planning.html`。
- 選擇代理工作流顯示 4 / 9 篇；與只看收藏組合後顯示收藏的該篇。
- 新文章出現在學習路徑中；其六節內容與其他文章相同。
- 收藏後重新載入仍顯示已收藏；完成標記重新載入仍保留。
- 測驗未作答時提示選擇；錯誤答案提供解釋，正確答案顯示確認；測驗不會自動標記完成。

互動驗證過程曾發現分類選擇器同時選到文章卡片，已將其限制為分類按鈕；修正後重新操作驗證。這項修正屬於互動驗收，不是新增內容所需的額外結構修改。

## 下一次交辦

```text
請先讀 AGENTS.md。新增一篇「如何檢查 AI 回答的來源」，分類為提示設計。
沿用固定六節格式及視覺設計，附可執行練習、測驗與官方來源。
建置並檢查，確認新文章能在首頁、搜尋和學習路徑找到。
回報修改檔案、檢查結果與任何尚未確認的資訊。
```

預期修改為一個新的資料物件與重新產生的 dist 檔案。若新主題需要第四種分類或不同頁型，則需同步修改規則、範例、建置驗證和導覽，不能只讓某一頁例外。
