# pi-aaaav

[English](README.md)

給 [pi](https://github.com/earendil-works/pi) 用的 agent 工作流程 skill 和循環 extension。每一種主要任務都從自己的 skill 進來，選一本 playbook，然後跑同一個循環：**Align → Anchor → Act → Verify**。

## Skill

```text
aaaav            核心循環 · 原則 · playbook：autonomous-run、pause、pickup
├─ answering     explain · compare
├─ investigating research · diagnose
├─ inspecting    diff-review · qa-release
├─ coding        bug-fix · feature · refactoring · perf · prototype（+ Mini SDD）
├─ writing       draft · tighten · comments
└─ solid-loop    apply-friction · author-skill · bootstrap
共用             grilling · domain-modeling · human-feedback · agent-terse
```

- **`aaaav`** 放每一種任務都成立的做法：重述任務、選入口的 playbook 並把步驟抄進 `todo`、第一筆修改前寫出 `Reality anchor:`、以小步前進且先刪後加、依 anchor 驗證，並記下 friction note。Reflexive pass 會把 friction note 交給 `solid-loop`。`PRINCIPLES.md` 列出 playbook 引用的原則，使用者也可以用這些名稱中途修正方向。三本生命週期 playbook 處理無人看管的執行、乾淨的暫停，以及接手前一輪的工作。
- **入口 skill** 各自寫出這類任務的 anchor，並列出自己的 playbook。每本 playbook 先用一句話說明它負責什麼，接著是編號步驟，最後一行 `Reply:` 規定回報要包含什麼。
- **共用 skill** 由入口呼叫：`grilling` 處理使用者要做的決定，`domain-modeling` 處理術語和 ADR，`human-feedback` 處理對成品的反應，`agent-terse` 處理只給 agent 讀的文字：任務 brief、回報、agent 之間的訊息。

## Extension

| 檔案 | 作用 |
| --- | --- |
| `pi/anchor-gate.ts` | 使用者最新一則訊息之後，assistant 還沒寫出 `Reality anchor:` 就執行 `write` 或 `edit` 時，每則訊息顯示一次警告，但不擋下呼叫。`.md`、`.txt`、`.html` 檔、`scratch/`、`docs/specs/` 和專案外的暫存檔不警告。透過 `bash` 改檔不在檢查範圍內。 |
| `pi/decision-tool.ts` | `aaaav_decision` 工具把一筆決策寫進 TSV 決策軌跡，每筆只佔一行，用試算表開啟也安全；接手別人的軌跡時寫一筆 `start`。 |
| `pi/second-thought.ts` | 呼叫過 `write`、`edit` 或 `bash` 的執行結束前，透過 pi 的 classifier registry 問 Jev（TypeSafe 的型別化決策模型）：最後的回覆有沒有證明需求已達成、需要哪一級 review、品質如何。Jev 也會判斷這則回覆是不是提醒點，也就是把工作交回給使用者的地方；只是確認收到、回報進度或等待中的回覆不提醒。在提醒點上，quality < 1.5 或 review 是 `full` 時，加一則看得到的提醒並讓 agent 多跑一輪，每輪最多一次；agent 可以不同意，直接結束。只有 done < 0.25 時，只顯示提醒，不多跑一輪。需求是使用者最新打的訊息；extension 送進來的訊息（intercom、monitor 喚醒）不會取代它。由這類訊息開始的那一輪，會連同 `trigger: wake` 和那則訊息一起送出，依那則訊息要求的事評估。呼叫過 `MonitorCreate`、`LoopCreate`、`goal_wait` 或 `subagent` 類工具的執行是在等喚醒，不評估。只送出需求、trigger、喚醒訊息和最後的回覆。沒有 TypeSafe key 時記為 `unknown`，不做任何事。在 subagent session 裡（pi-herdr-agents 的 `PI_SUBAGENT_ID`，或 pi-subagents 的 `PI_SUBAGENT_CHILD`）完全不啟用，結果交給派出它的 agent 判斷。 |
| `pi/validate-tool-use.ts` | 每次 `write` 或 `edit` 後對該檔執行 `hooks/validate_tool_use.py`，替 `SKILL.md`、指令檔（`AGENTS.md`、`CLAUDE.md`、`GEMINI.md`、`rules/`）和 `docs/specs/` 產出物附上建議。需要 `PATH` 上有 `python3`。 |
| `pi/ttsr.ts` | 移植自 oh-my-pi 的 Time Traveling Stream Rules。`~/.pi/agent/rules/` 或 `<專案>/.pi/rules/` 裡 frontmatter 帶有 `condition` regex 的 Markdown 規則，會在執行過程中被監看。assistant 串流文字命中時，中斷回應、丟棄那段輸出，並注入規則後重試；工具參數命中時（`bash` 看指令，`write`／`edit` 看新寫入的文字），直接擋下呼叫，以規則內容作為理由。frontmatter 欄位沿用 oh-my-pi：`condition`、`scope`（`text`、`thinking`、`tool`、`tool:bash`、`tool:edit(*.ts)`）、`globs`、`interruptMode`（`always`、`prose-only`、`tool-only`、`never`），另加 `repeatMode`（`once` 或 `after-gap`）與 `repeatGap`。預設每條規則每個 session 只觸發一次。不支援 `astCondition`、`question`、`agents`，用到的規則會被跳過並回報。`/ttsr` 列出已載入的規則。 |

## 安裝

建議安裝 npm 套件 `pi-aaaav` 來使用 aaaav：

```bash
pi install npm:pi-aaaav
```

本機 checkout 會直接載入，改完 `/reload` 就生效：

```bash
pi install /path/to/aaaav
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
