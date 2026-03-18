"""
Simulates gateway payloads for each session turn from the dataset.
Reconstructs what the gateway receives at each turn and measures it.

BUG 1: build_history() slices messages wrong — uses messages[:turn] but
        turn is 1-indexed, so turn 1 gives messages[:1] which includes the
        current message, not the history before it. Should be messages[:turn-1].
BUG 2: calculate_overhead_ratio() divides by total_tokens but never guards
        against total_tokens being 0 — will throw ZeroDivisionError on empty payloads.
BUG 3: session_summary() computes average overhead as mean of per-turn overhead %,
        but this is wrong — it should be computed from total tokens, not averaged %s.
        (A 4-token turn at 99.9% and a 4500-token turn at 62% should NOT average to 80.95%)
"""

import json
from pathlib import Path

SESSIONS_FILE = Path(__file__).parent.parent / "sessions" / "all_sessions.json"


def build_history(all_messages: list, turn: int) -> list:
    """Return messages that appear in history at a given turn (1-indexed)."""
    return all_messages[:turn]  # BUG 1: should be [:turn-1] — off by one, includes current msg


def calculate_overhead_ratio(user_tokens: int, total_tokens: int) -> float:
    """Returns what fraction of tokens are NOT the user message."""
    return (total_tokens - user_tokens) / total_tokens  # BUG 2: no zero guard


def session_summary(turn_metrics: list) -> dict:
    """Aggregate per-turn metrics into session-level summary."""
    total_input = sum(t["total_input_tokens"] for t in turn_metrics)
    total_user = sum(t["user_payload_tokens"] for t in turn_metrics)
    total_invocations = sum(t["tools_invoked"] for t in turn_metrics)

    # BUG 3: wrong averaging — should be total_user/total_input, not mean of per-turn %s
    avg_overhead = sum(t["overhead_ratio_pct"] for t in turn_metrics) / len(turn_metrics)

    return {
        "total_input_tokens": total_input,
        "total_user_tokens": total_user,
        "total_tool_invocations": total_invocations,
        "average_overhead_pct": round(avg_overhead, 2),   # BUG 3 lives here
        "correct_overhead_pct": round((1 - total_user / total_input) * 100, 2) if total_input else 0,
        "turns": len(turn_metrics),
    }


def simulate_session(session: dict) -> list:
    """Walk through a session and produce per-turn gateway metrics."""
    results = []
    reconstructed_messages = []

    for turn_data in session["turns"]:
        turn_num = turn_data["turn"]
        user_input = turn_data["user_input"]
        analysis = turn_data.get("analysis", {})

        # Add user message to reconstructed history
        reconstructed_messages.append({"role": "user", "content": user_input})

        history = build_history(reconstructed_messages, turn_num)  # BUG 1 fires here

        metrics = {
            "session_id": session["session_id"],
            "session_type": session["session_type"],
            "turn": turn_num,
            "user_input_preview": user_input[:50],
            "user_payload_tokens": analysis.get("user_payload_tokens", 0),
            "system_tokens": analysis.get("system_tokens", 3100),
            "tool_schema_tokens": analysis.get("tool_schema_tokens", 4400),
            "history_tokens": analysis.get("history_tokens", 0),
            "total_input_tokens": analysis.get("total_input_tokens", 0),
            "overhead_ratio_pct": analysis.get("overhead_ratio_pct", 0),
            "tools_invoked": analysis.get("tools_invoked", 0),
            "thinking_used": analysis.get("thinking_used", False),
            "history_reconstructed_turns": len(history),
        }
        results.append(metrics)

        # Add assistant response to history for next turn
        llm_output = turn_data.get("llm_output", "")
        reconstructed_messages.append({"role": "assistant", "content": llm_output})

    return results


def run_all_sessions():
    with open(SESSIONS_FILE) as f:
        data = json.load(f)

    all_results = []
    for session in data["sessions"]:
        turn_metrics = simulate_session(session)
        summary = session_summary(turn_metrics)
        print(f"\n{'='*60}")
        print(f"Session {session['session_id']} — {session['session_type']}")
        print(f"  Turns: {summary['turns']}")
        print(f"  Total input tokens: {summary['total_input_tokens']:,}")
        print(f"  Total user tokens:  {summary['total_user_tokens']:,}")
        print(f"  Overhead (BUGGY avg of %s): {summary['average_overhead_pct']}%")
        print(f"  Overhead (correct):         {summary['correct_overhead_pct']}%")
        print(f"  Tool invocations: {summary['total_tool_invocations']}")
        all_results.extend(turn_metrics)

    return all_results


if __name__ == "__main__":
    results = run_all_sessions()
    print(f"\nTotal turns processed: {len(results)}")
