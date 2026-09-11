# weihung-loop-boot

精簡化的 AAAAV Agent 工作流程插件，同時支援 Google Antigravity (`agy`)、Claude Code (`claude`) 與 OpenAI Codex (`codex`)。

## 設計哲學

當前的基底模型能力已非常成熟，不再需要鉅細靡遺地紀錄所有瑣碎問題，也不需要拉設無窮無盡的防禦性「紅線」。本專案的核心目標在於：

1. **精簡化 Skill**：保持 Skill 簡練且具備高可操作性，直接陳述期望行為。透過 Progressive Disclosure 將詳細流程下放至 `references/`。
2. **標準化核心能力**：統一 Skill 的報告能力（`Requirement | Evidence | Result` 驗證表）、溝通能力（公開推理過程、主動通報問題）以及文件能力（連結優先、單次可讀）。
3. **在 Durable 意義下檢討**：避免規則無限擴張。在工作開始前檢查核心規則與關鍵技能缺漏並先行補齊；在驗證階段對新增的規則與技能進行檢討，檢討的核心在於**調整與校準**，而非發明防禦性詞彙。

## AAAAV 循環

本專案落實 AAAAV 工作流程：

```text
Align (對齊) ──► Advance (推進) ──► Anchor (定錨) ──► Act (實作) ──► Verify (驗證)
```

- **Align**：用使用者的語言重述需求與目標，並將工作分類為 **Inline** 或 **Durable**。
  - *Inline*：需求明確、影響局部、無需長期留存。宣告 Contract 與授權，不產生規範文件。
  - *Durable*：涉及架構決策、外部介面或跨階段延續。在開始前檢查技能與核心規則準備度，並於 `docs/specs/` 留存決策與規格。
- **Advance**：Durable 工作依照 `Decision → Spec → Design` 推進。一旦任務指派出去，即歸屬於 Worker 與使用者；由自己承接的 Bounded Loop 則以 Inline 執行。
- **Anchor**：在第一次編輯生產代碼前，明確宣告 Reality Anchor（真實反饋錨點）與 Checkpoint。
- **Act**：遵循目標專案的原生開發規範，以微小且完整的增量實作。
- **Verify**：執行 Reality Anchor 並在標準驗證表中記錄所觀察到的事實證據。對新增的規則與技能進行檢討與微調。

## 保護 Hook

參考 `reflexive-claude-code` 設計，透過 `hooks.json` 與 Python 驗證腳本提供非阻塞式的品質輔助：

- **SKILL.md 驗證器**：檢查 Frontmatter、偵測損壞的 Markdown 連結與孤立文件、確保內容精簡（建議不超過 120 行），並提醒避免防禦性反模式語句。
- **Rule 驗證器**：檢查 `AGENTS.md`、`CLAUDE.md` 及 `rules/*.md`，避免微規則無限堆疊與防禦性用語。
- **Durable 規格驗證器**：檢查 `decision.md` 中的事前技能準備度、`spec.md` 的核准狀態，以及 `verification.md` 的標準三欄驗證表。

## 專案結構

```text
weihung-loop-boot/
├── plugin.json                    # Antigravity 插件清單
├── .claude-plugin/
│   ├── plugin.json                # Claude Code 插件清單
│   └── marketplace.json           # Claude Code 市集清單
├── .codex-plugin/
│   └── plugin.json                # OpenAI Codex 插件清單
├── hooks.json                     # Antigravity Hook 配置
├── hooks/
│   ├── hooks.json                 # Claude Code Hook 配置
│   ├── validate_tool_use.py       # PostToolUse Hook 入口
│   ├── validate_all.py            # 全專案驗證 CLI
│   └── validators/                # 模組化驗證邏輯
├── skills/
│   ├── leveraging-aaaav/          # 核心 AAAAV 執行技能
│   │   ├── SKILL.md
│   │   └── references/            # 報告、溝通、文件、Durable 檢討標準
│   └── streamlining-skills/       # Skill 精簡與標準化技能
│       ├── SKILL.md
│       └── references/            # 防禦性模式對照、Skill 模板
├── scripts/
│   ├── install.sh                 # 多平台安裝腳本 (agy, claude, codex)
│   └── validate.sh                # 測試與驗證執行器
└── tests/                         # 完整自動化測試套件 (pytest / unittest)
```

## 安裝方式

透過統一的安裝腳本部署至各平台：

```bash
# 安裝至所有支援平台 (Antigravity, Claude Code, Codex)
bash scripts/install.sh --target all

# 或安裝至指定平台
bash scripts/install.sh --target agy
bash scripts/install.sh --target claude
bash scripts/install.sh --target codex
```

## 驗證與測試

執行完整測試套件與全工作區驗證：

```bash
bash scripts/validate.sh
```
