"""
Claude Code Gateway Dataset — Analyzer
Produces per-turn metrics CSV and summary statistics.
"""
import json
import csv
from pathlib import Path
from utils import calculate_overhead_pct

ROOT = Path(__file__).parent.parent
DATA = ROOT / "sessions" / "all_sessions.json"
OUT_TURNS = ROOT / "analysis" / "turns.csv"
OUT_SESSIONS = ROOT / "analysis" / "sessions.csv"
ROOT.joinpath("analysis").mkdir(exist_ok=True)

with open(DATA) as f:
    data = json.load(f)

turn_rows = []
session_rows = []

for session in data["sessions"]:
    sid = session["session_id"]
    stype = session["session_type"]

    session_totals = {
        "session_id": sid,
        "session_type": stype,
        "turns": len(session["turns"]),
        "total_input_tokens": 0,
        "total_user_tokens": 0,
        "total_tool_invocations": 0,
        "peak_history_tokens": 0,
    }

    for turn in session["turns"]:
        a = turn.get("analysis", {})
        user_tok = a.get("user_payload_tokens", 0)
        sys_tok = a.get("system_tokens", 3100)
        tool_tok = a.get("tool_schema_tokens", 4400)
        hist_tok = a.get("history_tokens", 0)
        total = a.get("total_input_tokens", sys_tok + tool_tok + hist_tok + user_tok)
        overhead = calculate_overhead_pct(user_tok, total)
        invoked = a.get("tools_invoked", 0)

        row = {
            "session_id": sid,
            "session_type": stype,
            "turn": turn["turn"],
            "user_input_preview": turn["user_input"][:60],
            "user_payload_tokens": user_tok,
            "system_tokens": sys_tok,
            "tool_schema_tokens": tool_tok,
            "history_tokens": hist_tok,
            "total_input_tokens": total,
            "overhead_ratio_pct": overhead,
            "user_payload_pct": round(100 - overhead, 2),
            "tools_sent": 23,
            "tools_invoked": invoked,
            "tool_utilization_pct": round(invoked / 23 * 100, 1),
            "thinking_used": int(a.get("thinking_used", False)),
            "history_dominant": int(hist_tok > tool_tok),
        }
        turn_rows.append(row)

        session_totals["total_input_tokens"] += total
        session_totals["total_user_tokens"] += user_tok
        session_totals["total_tool_invocations"] += invoked
        session_totals["peak_history_tokens"] = max(session_totals["peak_history_tokens"], hist_tok)

    # session-level metrics
    total = session_totals["total_input_tokens"]
    session_totals["overall_overhead_pct"] = calculate_overhead_pct(session_totals["total_user_tokens"], total)
    session_totals["overall_user_pct"] = round(100 - session_totals["overall_overhead_pct"], 2)
    session_totals["avg_tool_utilization_pct"] = round(
        session_totals["total_tool_invocations"] / (23 * session_totals["turns"]) * 100, 1
    )
    session_rows.append(session_totals)

with open(OUT_TURNS, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=turn_rows[0].keys())
    w.writeheader()
    w.writerows(turn_rows)

with open(OUT_SESSIONS, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=session_rows[0].keys())
    w.writeheader()
    w.writerows(session_rows)

print("=== PER-SESSION SUMMARY ===")
for r in session_rows:
    print(f"{r['session_id']} ({r['session_type']:<30}) | "
          f"{r['turns']} turns | "
          f"{r['total_input_tokens']:>7} total tok | "
          f"user: {r['overall_user_pct']:>5}% | "
          f"overhead: {r['overall_overhead_pct']:>5}% | "
          f"tool util: {r['avg_tool_utilization_pct']:>4}% | "
          f"peak hist: {r['peak_history_tokens']:>6}")

print("\n=== AGGREGATE ===")
total_input = sum(r["total_input_tokens"] for r in session_rows)
total_user = sum(r["total_user_tokens"] for r in session_rows)
total_invocations = sum(r["total_tool_invocations"] for r in session_rows)
total_turns = sum(r["turns"] for r in session_rows)
print(f"Total input tokens:        {total_input:>10,}")
print(f"Total user message tokens: {total_user:>10,}")
print(f"User payload %:            {total_user/total_input*100:>9.2f}%")
print(f"Structural overhead %:     {(1-total_user/total_input)*100:>9.2f}%")
print(f"Total tool invocations:    {total_invocations:>10}")
print(f"Total tool schema sends:   {23*total_turns:>10}")
print(f"Overall tool util rate:    {total_invocations/(23*total_turns)*100:>9.1f}%")
print(f"\nOutput: {OUT_TURNS}")
print(f"Output: {OUT_SESSIONS}")
