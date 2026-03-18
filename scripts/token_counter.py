"""
Token counter for gateway payloads.
Counts tokens per component: system, tools, history, user message.
"""

import json
from utils import (
    count_tokens,
    count_json,
    system_tokens,
    tool_schema_tokens,
    history_tokens,
    analyze_payload,
)


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
