"""
Token counter for gateway payloads.
Counts tokens per component: system, tools, history, user message.
"""

import json

# Claude uses a custom tokenizer. As an approximation, we'll use character-based estimation
# since tiktoken's cl100k_base (GPT-4) is not accurate for Claude.
# Rule of thumb: ~4 characters per token for English text
CHARS_PER_TOKEN = 4

def count_tokens(text: str) -> int:
    """
    Estimate token count for Claude.
    Note: This is an approximation. For production use, integrate with Anthropic's
    official token counting API or SDK.
    """
    return len(text) // CHARS_PER_TOKEN

def count_json(obj) -> int:
    try:
        return count_tokens(json.dumps(obj, default=str))
    except (TypeError, ValueError):
        # Fallback: estimate based on repr if serialization fails
        return count_tokens(repr(obj))

def system_tokens(payload: dict) -> dict:
    """Break down system prompt token usage by block."""
    results = {}
    for i, block in enumerate(payload.get("system", [])):
        text = block.get("text", "")
        label = f"system_block_{i}"
        if "billing" in text.lower():
            label = "billing_header"
        elif "you are claude code" in text.lower():
            label = "identity"
        else:
            label = "instructions"
        results[label] = count_tokens(text)
    return results

def tool_schema_tokens(payload: dict) -> dict:
    """Count tokens per tool schema."""
    tools = payload.get("tools", [])
    if isinstance(tools, str):
        # placeholder string in our dataset — estimate
        return {"_estimated": 4400}
    return {t["name"]: count_json(t) for t in tools}

def history_tokens(messages: list) -> dict:
    """Count tokens broken down by role and content type."""
    totals = {"user": 0, "assistant_text": 0, "assistant_thinking": 0, "tool_results": 0}

    for msg in messages[:-1]:  # exclude current turn
        role = msg.get("role", "")
        content = msg.get("content", "")

        if isinstance(content, str):
            totals["user"] += count_tokens(content)
        elif isinstance(content, list):
            for block in content:
                btype = block.get("type", "")
                if btype == "thinking":
                    totals["assistant_thinking"] += count_tokens(block.get("thinking", ""))
                elif btype == "text":
                    totals["assistant_text"] += count_tokens(block.get("text", ""))
                elif btype == "tool_result":
                    totals["tool_results"] += count_json(block)

    return totals

def analyze_payload(payload: dict, label: str = "") -> dict:
    messages = payload.get("messages", [])
    current_user = messages[-1] if messages else {}
    user_text = current_user.get("content", "")
    if isinstance(user_text, list):
        user_text = " ".join(b.get("text", "") for b in user_text)

    sys_tok = system_tokens(payload)
    tool_tok = tool_schema_tokens(payload)
    hist_tok = history_tokens(messages)

    user_tokens = count_tokens(user_text)
    system_total = sum(sys_tok.values())
    tool_total = sum(tool_tok.values())
    history_total = sum(hist_tok.values())
    grand_total = user_tokens + system_total + tool_total + history_total

    return {
        "label": label,
        "user_tokens": user_tokens,
        "system_tokens": system_total,
        "system_breakdown": sys_tok,
        "tool_tokens": tool_total,
        "history_tokens": history_total,
        "history_breakdown": hist_tok,
        "grand_total": grand_total,
        "overhead_pct": round((1 - user_tokens / max(grand_total, 1)) * 100, 2),
        "user_pct": round(user_tokens / max(grand_total, 1) * 100, 2),
    }


if __name__ == "__main__":
    # Quick smoke test with a minimal payload
    test_payload = {
        "system": [
            {"text": "x-anthropic-billing-header: cc_version=2.1"},
            {"text": "You are Claude Code, Anthropic's official CLI."},
            {"text": "You are an interactive CLI agent. " * 100},  # simulate large instruction block
        ],
        "tools": [
            {"name": "Bash", "description": "Execute bash commands", "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}}},
            {"name": "Read", "description": "Read a file", "input_schema": {"type": "object", "properties": {"file_path": {"type": "string"}}}},
        ],
        "messages": [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": [
                {"type": "thinking", "thinking": "The user said hi. I should greet them back."},
                {"type": "text", "text": "Hi! I'm Claude Code. What would you like to work on?"}
            ]},
            {"role": "user", "content": "how are you", "cache_control": {"type": "ephemeral"}}
        ]
    }

    result = analyze_payload(test_payload, label="test_turn_2")
    print(json.dumps(result, indent=2))
