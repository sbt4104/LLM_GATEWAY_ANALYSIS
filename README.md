# cc-gateway-analysis

> What actually travels to the Claude API on every request — and how much of it is useful?

Dataset and analysis scripts for studying the token economics of Claude Code's gateway payloads. Built to answer: **how much of what Claude Code sends to the LLM is structural overhead vs actual user intent?**

## Structure

```
cc-gateway-analysis/
├── sessions/
│   └── all_sessions.json      # 10 sessions, 39 turns, full gateway payload breakdown
├── scripts/
│   ├── analyze.py             # Produces summary CSV from the dataset
│   ├── token_counter.py       # Counts tokens per payload component
│   └── session_simulator.py   # Reconstructs gateway payloads per turn and measures them
├── analysis/
│   ├── turns.csv              # Per-turn metrics (generated)
│   └── sessions.csv           # Per-session summary (generated)
└── README.md
```

## Quick start

```bash
pip install tiktoken
python scripts/analyze.py          # generates analysis/turns.csv and analysis/sessions.csv
python scripts/token_counter.py    # smoke test the token counter
python scripts/session_simulator.py  # simulate all sessions
```

## Sessions overview

| ID  | Type | Turns | Key insight |
|-----|------|-------|-------------|
| S01 | Pure small talk | 4 | Maximum overhead baseline — 99.95% waste |
| S02 | Factual Q&A | 3 | 0 tools used, all answers from training data |
| S03 | Single file read | 2 | 1/23 tools used — 22 schemas dead weight |
| S04 | Git workflow | 4 | History growth rate with shell tool results |
| S05 | Bug fix | 4 | First multi-tool session — 4 tools justified |
| S06 | Code review (200-line paste) | 3 | User payload reaches 19% — large input effect |
| S07 | Feature build | 6 | History becomes dominant by turn 6 |
| S08 | Mixed social + code | 4 | Amortization across realistic session |
| S09 | Huge input (500-line paste) | 2 | User payload reaches 37% — crossover approaches |
| S10 | Full agentic loop | 8 | History 3× tool schemas at peak — best justified |

## Key findings

- **Average user message = 1.68% of total tokens sent**
- **82.6% of tool schemas (19/23) are never invoked** across all 10 sessions
- **Overall tool utilization rate: 5.2%** (48 invocations / 920 schema transmissions)
- **History becomes the dominant cost** by turn 6-7 in long sessions (overtakes tool schemas)
- **A 500-line code paste** is needed for user payload to reach 37% of total — still not dominant
- **Thinking budget (31,999 tokens)** allocated on every request, used in ~30% of sessions

## Trimming opportunities

| Optimization | Tokens saved/turn | Complexity |
|---|---|---|
| Remove 19 never-used tool schemas | ~3,680 | Low — static list |
| Dynamic tool loading by query intent | ~3,000-4,000 | Medium — needs classifier |
| Compress system prompt per session type | ~800-1,200 | Medium |
| Enable thinking only for complex tasks | 0 tokens, latency savings | Low — heuristic |
| Summarize history after turn 5 | 1,000-10,000 | High |

## Note on the scripts

The scripts contain intentional bugs — see docstrings. Part of the point is to run these through Claude Code and watch it find and fix them.
