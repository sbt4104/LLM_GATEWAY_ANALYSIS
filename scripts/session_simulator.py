"""
Simulates gateway payloads for each session turn from the dataset.
Reconstructs what the gateway receives at each turn and measures it.
"""

import json
from pathlib import Path

SESSIONS_FILE = Path(__file__).parent.parent / "sessions" / "all_sessions.json"


def build_history(all_messages: list, turn: int) -> list:
    """Return messages that appear in history at a given turn (1-indexed)."""
    return all_messages[:turn-1]  # turn-1 excludes the current message


def calculate_overhead_ratio(user_tokens: int, total_tokens: int) -> float:
    """Returns what fraction of tokens are NOT the user message."""
    if total_tokens == 0:
        return 0.0
    return (total_tokens - user_tokens) / total_tokens


def session_summary(turn_metrics: list) -> dict:
    """Aggregate per-turn metrics into session-level summary."""
    total_input = sum(t["total_input_tokens"] for t in turn_metrics)
    total_user = sum(t["user_payload_tokens"] for t in turn_metrics)
    total_invocations = sum(t["tools_invoked"] for t in turn_metrics)

    # Calculate overhead as weighted average from totals, not mean of percentages
    overhead_pct = round((1 - total_user / total_input) * 100, 2) if total_input else 0

    return {
        "total_input_tokens": total_input,
        "total_user_tokens": total_user,
        "total_tool_invocations": total_invocations,
        "overhead_pct": overhead_pct,
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
        print(f"  Overhead: {summary['overhead_pct']}%")
        print(f"  Tool invocations: {summary['total_tool_invocations']}")
        all_results.extend(turn_metrics)

    return all_results


if __name__ == "__main__":
    results = run_all_sessions()
    print(f"\nTotal turns processed: {len(results)}")
