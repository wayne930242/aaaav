# pi-anchorloop

[English](README.md)

給 [pi](https://github.com/earendil-works/pi) 用的 agent 工作流程 skill 和循環 extension。每一種主要任務都從自己的 skill 進來，選一本 playbook，然後跑同一個循環：**Align → Anchor → Act → Verify**。

## Skill

```text
anchorloop            核心循環 · 原則 · playbook：autonomous-run、pause、pickup
├─ answering     explain · compare
├─ investigating research · diagnose
├─ inspecting    diff-review · qa-release
├─ coding        bug-fix · feature · refactoring · perf · prototype（+ Mini SDD）
├─ writing       draft · tighten · comments
└─ solid-loop    apply-friction · author-skill · bootstrap
共用             grilling · domain-modeling · human-feedback · agent-terse
```

- **`anchorloop`** 放每一種任務都成立的做法：重述任務、選入口的 playbook、只把真正的工作項目放進 `todo`（第一次 create 會開啟一個 loop）、第一筆修改前用 `anchorloop_stage` 宣告 loop（種類、intent、anchor 指令）、以小步前進且先刪後加、依 anchor 驗證，並把 friction 記在 loop book。Reflexive pass 會把已 reflect 的 friction 交給 `solid-loop`。`PRINCIPLES.md` 列出 playbook 引用的原則，使用者也可以用這些名稱中途修正方向。三本生命週期 playbook 處理無人看管的執行、乾淨的暫停，以及接手前一輪的工作。
- **入口 skill** 各自寫出這類任務的 anchor，並列出自己的 playbook。每本 playbook 先用一句話說明它負責什麼，接著是編號步驟，最後一行 `Reply:` 規定回報要包含什麼。
- **共用 skill** 由入口呼叫：`grilling` 處理使用者要做的決定，`domain-modeling` 處理術語和 ADR，`human-feedback` 處理對成品的反應，`agent-terse` 處理只給 agent 讀的文字：任務 brief、回報、agent 之間的訊息。

## Extension

| 檔案 | 作用 |
| --- | --- |
| `pi/book.ts` | Loop book。第一次 `todo` create 會開啟一個 loop，所以需要 [`@juicesharp/rpiv-todo`](https://github.com/juicesharp/rpiv-mono/tree/main/packages/rpiv-todo#readme) 的 `todo` 工具（它的 `tool_result` details `{tasks, nextId}` 和 `rpiv-todo-state` 條目）；沒有它就不會開啟 loop。agent 只用 `anchorloop_stage` 宣告 extension 看不到的事：`kind`（`quick`、`inline`、`reviewed`、`durable`，附 intent 和 anchor 指令）、`verify`（不是指令的檢查）、`fresh-read`、`friction`（`tried`、`found`、`led_by`）、`reflect`、`skip`、`back`、`close`，以及查詢用的 `read`。其餘都從證據讀出：production 的修改、執行過 anchor 指令的那次 bash 的 exit code（失敗後又通過的執行會成為 retry pair）、reviewer 的 `Blocking: P0=<n> P1=<m>` 數字、`docs/specs/*/` 產出物每次編輯後的摘要，以及 Jev 判定為「全新 context 讀過 spec」的 subagent 回報。階段機依這些證據給每種 loop 固定的階段順序（`quick` 為 act → check；`inline` 為 anchor → act → verify；`reviewed` 加 review；`durable` 再加 decide → grill → spec → read → approve → design；每一種都以 reflect → close 結尾），`read` 顯示 `<種類> · phase <目前> ✓ → <下一個>（缺：…）· 已跳過：…`。前一個階段還沒完成就開始下一個階段，會用一行警告一次並指出 `skip` 的出口；證據改變或用 `back` 時階段會退回。book 也記錄每個 todo 的 `anchor`、`ref`（`<path>#<heading>`，解析成行號範圍）和 `followup` metadata。每個開啟中的 loop 有一份 YAML book，放在 `~/.pi/agent/anchorloop/books/`（可用 `ANCHORLOOP_BOOKS_DIR` 覆寫），subagent 的 book 放在 `agents/`（subagent 自己 close 時 book 留給主 session）；`session_start` 會清掉 session 已不存在的 book。`close` 不會因為階段或 friction 而拒絕，只在還有 pending 或 in-progress 的 todo 沒有 `metadata.followup`（票號、`memory` 或 `drop — <原因>`）時拒絕。 |
| `pi/anchor-gate.ts` | 只在開啟的 loop 內：`write` 或 `edit` 開始 `act` 階段、而這種 loop 前面的階段還沒完成時，顯示一行警告：沒有 anchor（kind 呼叫的 `anchor`、`Reality anchor:` 這一行，或已跳過），`durable` loop 則還缺決策、spec、全新 context 的閱讀、核准或設計（從 `docs/specs/<資料夾>/` 的檔案判斷，資料夾由 book、intent 或 todo 的 `ref` 找出）。只有新缺了一個階段時才會再警告；呼叫仍會放行。沒有 loop 或是 `quick` loop 時保持安靜。`.md`、`.txt`、`.html` 檔、`scratch/`、`docs/specs/` 和專案外的暫存檔不會觸發。透過 `bash` 做的修改不檢查。 |
| `pi/decision-tool.ts` | `anchorloop_decision` 工具把一筆決策寫進 TSV 決策軌跡，每筆只佔一行，用試算表開啟也安全；接手別人的軌跡時寫一筆 `start`。 |
| `pi/second-thought.ts` | 只在開啟的 loop 內：一次執行結束且 book 自上次判斷後多了條目時，以及宣告 `close` 時，透過 pi 的 classifier registry 請 Jev（TypeSafe 的型別化決策模型）複核階段機。下一個階段由程式從 book 算出；Jev 看到種類、intent、anchor、diff 摘要（≤1200 字元）、`phase`（目前、下一個、缺什麼）、verify 狀態、未完成 todo、任務清單和 friction（子 agent 的以它的名字列出），只判斷目前階段的完成條件是否真的達到（`complete`），以及要 `advance`、退回（`back`）還是 `ask-user`，另外還問 `done`、還需要哪一級 review 與品質。一行提醒以 `next → <階段>` 開頭；有 retry pair 卻沒有 friction 條目時，附上 `friction` 提示。只有 Jev 同意前進、而下一個階段是 verify、review 或 fix 時，才讓 agent 多跑一輪；與上一則相同的提醒不重複，最後一次修改之後已有無 blocking 發現的 review 時，`full` 評等只顯示備註、不要求複查。呼叫過 `MonitorCreate`、`LoopCreate`、`goal_wait` 或 `subagent` 工具的執行在等待中，不被判斷。沒有 TypeSafe key 時什麼都不做，沒有 loop 時不會執行。subagent session（pi-herdr-agents 的 `PI_SUBAGENT_ID`，或 pi-subagents 的 `PI_SUBAGENT_CHILD`）不註冊任何東西，因為由派它的 agent 判斷結果。 |
| `pi/validate-tool-use.ts` | 每次 `write` 或 `edit` 後在行程內驗證該檔（`pi/support/validators.ts`，移植自 `hooks/validators/`），替 `SKILL.md`、指令檔（`AGENTS.md`、`CLAUDE.md`、`GEMINI.md`、`rules/`）和 `docs/specs/` 產出物附上建議。不需要 Python；`hooks/` 的 Python 驗證器仍供 `validate_all.py` 和對照測試使用。 |
| `pi/ttsr.ts` | 移植自 oh-my-pi 的 Time Traveling Stream Rules。`~/.pi/agent/rules/` 或 `<專案>/.pi/rules/` 裡 frontmatter 帶有 `condition` regex 的 Markdown 規則，會在執行過程中被監看。assistant 串流文字命中時，中斷回應、丟棄那段輸出，並注入規則後重試；工具參數命中時（`bash` 看指令，`write`／`edit` 看新寫入的文字），直接擋下呼叫，以規則內容作為理由。frontmatter 欄位沿用 oh-my-pi：`condition`、`scope`（`text`、`thinking`、`tool`、`tool:bash`、`tool:edit(*.ts)`）、`globs`、`interruptMode`（`always`、`prose-only`、`tool-only`、`never`），另加 `repeatMode`（`once` 或 `after-gap`）與 `repeatGap`。預設每條規則每個 session 只觸發一次。不支援 `astCondition`、`question`、`agents`，用到的規則會被跳過並回報。`/ttsr` 列出已載入的規則。 |

## 安裝

建議安裝 npm 套件 `pi-anchorloop` 來使用 anchorloop：

```bash
pi install npm:pi-anchorloop
```

本機 checkout 會直接載入，改完 `/reload` 就生效：

```bash
pi install /path/to/anchorloop
```

## 開發

```bash
uv run python hooks/validate_all.py .   # 檢查 skill、規則與 durable spec
uv run --with pytest pytest -q          # 驗證器與 pi extension 的測試（需要 node）
```

## 致謝

- Lauren Tan 的 [pstack](https://github.com/backnotprop/pstack)（MIT），鏡像 repo 的版本 `e44668c`，上游是 [cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack)；以及 Michael Denyer 的移植版 [pstack-claude](https://github.com/michael-denyer/pstack-claude)（MIT）：依任務類型分的 playbook、具名原則、生命週期 playbook、決策軌跡、獨立審查前不放行的關卡、交接給新 subagent，以及證據分級。
- [google-research/harness2](https://github.com/google-research/harness2)（Apache-2.0），版本 `1cfe254`：solid-loop 的放置判斷、最便宜機制的順序，以及沒有前後對照就不寫成教訓。
- [mattpocock/skills](https://github.com/mattpocock/skills)（MIT）：grilling、domain-modeling、diff review、prototype playbook，以及 feature playbook 的介面檢查。
- [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)（Apache-2.0），revision `bad48a0`：`agent-terse` 的精簡寫法。
- HumanLayer 的 [show-me](https://github.com/humanlayer/skills/tree/main/plugins/show-me)（MIT）：`answering` 的呈現方式。
- [oh-my-pi](https://github.com/can1357/oh-my-pi)：Time Traveling Stream Rules。

移植來的檔案在各自的頁尾註明出處。
