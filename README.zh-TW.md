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

- **`anchorloop`** 放每一種任務都成立的做法：重述任務、選入口的 playbook、只把真正的工作項目放進 `todo`（第一次 create 會開啟一個 loop）、第一筆修改前寫出 `Reality anchor:`、以小步前進且先刪後加、依 anchor 驗證，並記下 friction note。Reflexive pass 會把 friction note 交給 `solid-loop`。`PRINCIPLES.md` 列出 playbook 引用的原則，使用者也可以用這些名稱中途修正方向。三本生命週期 playbook 處理無人看管的執行、乾淨的暫停，以及接手前一輪的工作。
- **入口 skill** 各自寫出這類任務的 anchor，並列出自己的 playbook。每本 playbook 先用一句話說明它負責什麼，接著是編號步驟，最後一行 `Reply:` 規定回報要包含什麼。
- **共用 skill** 由入口呼叫：`grilling` 處理使用者要做的決定，`domain-modeling` 處理術語和 ADR，`human-feedback` 處理對成品的反應，`agent-terse` 處理只給 agent 讀的文字：任務 brief、回報、agent 之間的訊息。

## Extension

| 檔案 | 作用 |
| --- | --- |
| `pi/book.ts` | Loop book。第一次 `todo` create 會開啟一個 loop；agent 用 `anchorloop_stage` 工具宣告 loop 的種類（`quick`、`inline`、`reviewed`、`durable`）和每個階段，extension 附上證據：相對各 repo base `HEAD` 的 diff 統計、執行過 anchor 指令的那次 bash 的 exit code 與最後一行、reviewer 的 `Blocking: P0=<n> P1=<m>` 數字，以及 `docs/specs/*/` 產出物每次編輯後的摘要。它也記錄每個 todo 的 `anchor`、`ref`（`<path>#<heading>`，解析成行號範圍）和 `followup` metadata。每個開啟中的 loop 有一份 YAML book，放在 `~/.pi/agent/anchorloop/books/`（可用 `ANCHORLOOP_BOOKS_DIR` 覆寫），subagent 的 book 放在 `agents/`；`session_start` 會清掉 session 已不存在的 book。`close` 要手動做，只要還有 pending 或 in-progress 的 todo 沒有 `metadata.followup`（票號、`memory` 或 `drop — <原因>`）就拒絕；漏掉的階段只警告。 |
| `pi/anchor-gate.ts` | 只在開啟的 loop 內：`write` 或 `edit` 在 loop 還沒有 `anchor` 階段、assistant 也沒寫出 `Reality anchor:` 就執行時，每則使用者訊息顯示一次警告；durable loop 在記錄的 spec 還不是 `Status: approved` 時做 production 修改，每個 loop 警告一次，但都不擋下呼叫。沒有 loop 或是 `quick` loop 時保持安靜。`.md`、`.txt`、`.html` 檔、`scratch/`、`docs/specs/` 和專案外的暫存檔不警告。透過 `bash` 改檔不在檢查範圍內。 |
| `pi/decision-tool.ts` | `anchorloop_decision` 工具把一筆決策寫進 TSV 決策軌跡，每筆只佔一行，用試算表開啟也安全；接手別人的軌跡時寫一筆 `start`。 |
| `pi/second-thought.ts` | 只在開啟的 loop 內：一次執行結束且 book 自上次判斷後多了條目時，以及宣告 `close` 時，透過 pi 的 classifier registry 問 Jev（TypeSafe 的型別化決策模型）下一步該做什麼。Jev 只看到 book 裡的東西：種類、intent、anchor、diff 摘要（≤1200 字元）、verify 狀態（階段、review 輪次、子 agent 的檢查）、未完成 todo 數與任務清單。主要輸出是下一階段建議（`continue`、`verify`、`review`、`fix`、`close`、`ask-user`），以 `next → <階段>` 和 book 裡的依據開頭的提醒顯示；同時還問 `done`（證據是否涵蓋 intent）、還需要哪一級 review 與品質。只有當建議是 `verify`、`review` 或 `fix`，而 book 顯示最後一次 `act` 之後缺了該階段時，才讓 agent 多跑一輪；最後一次 `act` 之後已有無 blocking 發現的 review 時，`full` 評等只顯示備註、不要求複查。呼叫過 `MonitorCreate`、`LoopCreate`、`goal_wait` 或 `subagent` 工具的執行在等待中，不被判斷。沒有 TypeSafe key 時什麼都不做，沒有 loop 時不會執行。subagent session（pi-herdr-agents 的 `PI_SUBAGENT_ID`，或 pi-subagents 的 `PI_SUBAGENT_CHILD`）不註冊任何東西，因為由派它的 agent 判斷結果。 |
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
