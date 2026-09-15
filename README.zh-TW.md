# aaaav

精簡化的 AAAAV Agent 工作流程插件，支援 Antigravity、Claude Code 與 Codex。

## 概念

AAAAV 為 agent 提供一套簡短、可重複的工作流程，由三個 skill 組成：

1. **`aaaav-do`**（開發循環）：
   - **Align（對齊）**：用使用者的話重述需求，將變更歸類為 **Inline**（範圍局部、需求明確）或 **Durable**（決策需要延續到這次執行之後）。
   - **Advance（推進）**：Durable 任務依 `Decision → Spec → Design` 推進，收斂合約、介面邊界與決策。
   - **Anchor（定錨）**：在第一筆 production 修改前，宣告 reality anchor 與 checkpoint。
   - **Act（實作）**：依目標專案的原生慣例實作。每次嘗試錯誤後發現的事，都記成一筆摩擦記錄（`Tried` / `Found` / `Led by`）；Durable 寫在 `design.md` 的 `## Friction Notes`，Inline 寫在 `scratch/friction.md`。
   - **Verify（驗證）**：執行錨點，以 `Requirement | Evidence | Result` 表記錄觀察結果。**Reflexive（反思）** 將每筆摩擦記錄歸類為 **misdirection**（skill 或指令把嘗試帶錯方向）或 **gap**（沒有 skill 或指令涵蓋，只好繞路找答案）；沒有記錄就標記為 clean run。
2. **`solid-loop`**（修正 agent 系統）：
   - 套用已分類的摩擦記錄：修正誤導的那一行，或把缺少的事實放進唯一負責的位置。
   - 防止 skill 膨脹：新增前先找是否已有相同陳述，對每個改過的段落做 no-op 檢查，並讓每個 `SKILL.md` 維持在 300 行以內。
3. **`boot-loop`**（建立 agent 系統）：
   - 派出數個獨立 worker，透過 `aaaav-do` 執行調查任務。
   - 合併 worker 回傳的摩擦記錄，執行一次 `solid-loop`，建立或精煉 `AGENTS.md`、`CLAUDE.md` 與專案 skill。

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

驗證 skill、規則與 Durable 產出物：

```bash
# 執行工作區驗證與自動化測試套件
bash scripts/validate.sh
```
