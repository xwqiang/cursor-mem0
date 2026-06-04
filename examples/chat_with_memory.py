#!/usr/bin/env python3
"""
Chat loop with long-term memory — mem0-style API, Cursor SDK for LLM.

Requires:
  export CURSOR_API_KEY="cursor_..."
  pip install -e ".[nlp]"   # optional: spacy for BM25/entity boosting
"""

from __future__ import annotations

import os
import sys

from cursor_mem import Memory


def format_memories(results: list) -> str:
    lines = []
    for entry in results:
        text = entry.get("memory") or entry.get("data") or ""
        if text:
            lines.append(f"- {text}")
    return "\n".join(lines) if lines else "(no relevant memories)"


def main() -> None:
    if not os.environ.get("CURSOR_API_KEY"):
        print("Set CURSOR_API_KEY before running.", file=sys.stderr)
        sys.exit(1)

    user_id = os.environ.get("CURSOR_MEM_USER_ID", "default_user")
    memory = Memory()

    print("Chat with memory (type 'exit' to quit)")
    print(f"user_id={user_id}\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        search_result = memory.search(
            query=user_input,
            filters={"user_id": user_id},
            top_k=5,
        )
        memories_str = format_memories(search_result.get("results", []))

        from cursor_sdk import Agent, AgentOptions, LocalAgentOptions

        system = (
            "You are a helpful assistant. Answer using the conversation and user memories.\n"
            f"User memories:\n{memories_str}"
        )
        prompt = f"[SYSTEM]\n{system}\n\n[USER]\n{user_input}"

        result = Agent.prompt(
            prompt,
            AgentOptions(
                api_key=os.environ["CURSOR_API_KEY"],
                model="composer-2.5",
                local=LocalAgentOptions(cwd=os.getcwd()),
            ),
        )
        if result.status == "error":
            print("AI: (run failed)")
            continue

        assistant_response = (result.result or "").strip()
        print(f"AI: {assistant_response}\n")

        memory.add(
            [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": assistant_response},
            ],
            user_id=user_id,
        )


if __name__ == "__main__":
    main()
