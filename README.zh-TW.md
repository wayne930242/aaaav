# aaaav-loop-boot

精簡化的 AAAAV Agent 工作流程插件，支援 Antigravity、Claude Code 與 Codex。

## 概念

當前基底模型已具備成熟的代碼理解與協作能力，不再需要累積瑣碎的錯誤紀錄或拉設無窮無盡的防禦性「紅線」。本插件建立高密度且具備高可操作性的工作流，圍繞兩大精簡技能：

1. **`aaaav-do`**（AAAAV 開發循環）：
   - **Align（對齊）**：用使用者語言重述需求，劃分 **Inline**（局部快速修改）或 **Durable**（持久性架構決策）。
   - **Advance（推進）**：Durable 任務依循 `Decision → Spec → Design` 推進；指派任務歸屬 Worker 與使用者，自行承接的迴圈以 Inline 執行。
   - **Anchor（定錨）**：在第一筆生產代碼修改前宣告 Reality Anchor（真實反饋錨點）與 Checkpoint。
   - **Act（實作）**：遵循目標專案原生規範，微小且精準地實作。
   - **Verify（驗證）**：執行錨點並以 `Requirement | Evidence | Result` 三欄表記錄觀察事實。在驗證階段檢討新規則與技能，目的在於「調校與校準」，而非增設防禦性紅線。
2. **`solid-loop`**（技能精簡與標準化）：
   - 消除防禦性贅詞與禁止性條文，直接陳述期望行為。
   - 標準化所有技能的報告能力（三欄驗證表）、溝通能力（透明推理、主動通報）與文件能力（單次可讀、連結優先）。
   - 透過 Progressive Disclosure 將細節下放 `references/`，使 Skill 主文保持在 120 行以內。

## 用法

### 1. 安裝方式

一鍵安裝至 Antigravity、Claude Code 與 Codex：

```bash
# 同步安裝至所有支援平台
bash scripts/install.sh --target all

# 或安裝至指定平台
bash scripts/install.sh --target agy
bash scripts/install.sh --target claude
bash scripts/install.sh --target codex
```

### 2. 呼叫開發循環 (`aaaav-do`)

任何涉及代碼修改的工作均透過 `aaaav-do` 驅動：

```text
# Inline 模式（局部小修改）
Alignment: 為電子郵件欄位加入格式驗證
Inline — Contract: 在 API 入口處拒絕無效電子郵件並回傳 HTTP 400
Authorization: 使用者請求加入電子郵件驗證
Reality anchor: pytest tests/test_email.py

# Durable 模式（涉及架構或跨會話之變更）
Alignment: 實作多租戶認證機制
# 依序推進產出 docs/specs/YYYY-MM-DD-<slug>/:
# 1. decision.md  (收斂事實，工作前確認核心規則與專門技能準備度)
# 2. spec.md      (宣告 Reality Anchor，需待使用者核准)
# 3. design.md    (最小架構設計與介面邊界)
# 4. verification.md (填寫三欄客觀驗證表，並進行微調導向檢討)
```

### 3. 工作流與技能驗證

執行驗證以確保技能與規則符合精簡與非防禦性標準：

```bash
# 執行工作區驗證與自動化測試套件
bash scripts/validate.sh
```
