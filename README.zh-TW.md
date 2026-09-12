# aaaav-loop-boot

精簡化的 AAAAV Agent 工作流程插件，支援 Antigravity、Claude Code 與 Codex。

## 概念

當前基底模型已具備成熟的代碼理解與協作能力，不再需要累積瑣碎的錯誤紀錄或拉設無窮無盡的防禦性「紅線」。本插件建立高密度且具備高可操作性的工作流，圍繞兩大精簡技能：

1. **`aaaav-do`**（AAAAV 開發循環）：
   - **Align（對齊）**：用使用者語言重述需求，劃分 **Inline**（局部快速修改）或 **Durable**（持久性架構決策）。
   - **Advance（推進）**：Durable 任務依循 `Decision → Spec → Design` 推進；專注於合約、接縫與決策收斂，Advance 階段不再預先建立或腳手架 skill。
   - **Anchor（定錨）**：在第一筆生產代碼修改前宣告 Reality Anchor（真實反饋錨點）與 Checkpoint。
   - **Act（實作）**：遵循目標專案原生規範，微小且精準地實作；若遇較大摩擦可順手記錄於 `design.md`（`## Friction Notes`），Inline 模式則記於額外暫存檔（如 `scratch/friction.md`）。
   - **Verify（驗證）**：執行錨點並以 `Requirement | Evidence | Result` 三欄表記錄觀察事實。接著進行 **Reflexive（反思）** 流程，檢查摩擦記錄；無摩擦時直接早退，不造成額外系統負擔。
2. **`solid-loop`**（Agent System 反思審計與固化）：
   - 於 Verify 的 Reflexive 流程中調用，檢討本次任務實際使用到的技能與系統指令。
   - 核心審計標準：檢討該技能究竟是「幫助我們節省任務時間與 token，還是反而讀取了不必要的檔案和繞遠路？」
   - 以反思核心提問引導：「如果我早就知道什麼，就會在這次工作中減少摩擦和繞路？」
   - 依重要性將核心參考規範內嵌於 Skill 主文，維持單次可讀性，並遵循官方建議放寬上限至 300 行。

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
# 1. decision.md     (收斂事實，確認核心規則準備度)
# 2. spec.md         (宣告 Reality Anchor，需待使用者核准)
# 3. design.md       (最小架構設計與介面邊界)
# 4. verification.md (填寫三欄客觀驗證表與 Reflexive 反思檢討)
```

### 3. 工作流與技能驗證

執行驗證以確保技能與規則符合精簡與非防禦性標準：

```bash
# 執行工作區驗證與自動化測試套件
bash scripts/validate.sh
```
