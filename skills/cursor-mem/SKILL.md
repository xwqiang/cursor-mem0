---
name: cursor-mem
description: >-
  Manages long-term agent memory via the cursor-mem MCP server (add_memory,
  search_memories, list_memories, get_memory). Use when the user shares
  preferences, asks to remember something, starts a new chat or task that may
  depend on prior context, or mentions memory, mem0, MEMORY.md, or cross-session
  recall. Search before assuming missing context; store durable facts instead of
  growing markdown memory files.
---

# cursor-mem — Agent long-term memory

Use the **cursor-mem** MCP tools when this server is enabled in the project. Memory is scoped by `user_id` (default from `CURSOR_MEM_USER_ID` or `default_user`) and stored under `~/.cursor-mem/` unless overridden.

## When to write memory

Call `add_memory` when the user:

- States a **preference** (editor, language, style, tooling, workflow)
- Shares a **stable fact** about themselves or the project (names, conventions, constraints)
- Explicitly asks to **remember** or **don't forget**
- Corrects you on something that should persist across chats

| Situation | `infer` | Example |
|-----------|---------|---------|
| Natural-language preference or fact | `true` (default) | "I prefer tabs and dark mode" |
| Exact text to store verbatim | `false` | API endpoint template, legal wording |

Do **not** store: one-off task state, ephemeral file contents, secrets, or information already in the repo.

## When to read memory

At the **start** of a new task or when the user references past preferences:

1. `search_memories` with a short query (e.g. "editor preferences", "deployment setup")
2. Use `top_k` 3–5; only inject relevant hits into your reasoning
3. `list_memories` when you need a broad recent overview without a specific query
4. `get_memory` when you have a memory id from a prior tool result

Prefer **search + top_k** over reloading large `MEMORY.md` files into context.

## Tool reference

| Tool | Purpose |
|------|---------|
| `add_memory(text, user_id?, infer?)` | Save a memory; `infer=true` runs mem0 extraction via Cursor SDK |
| `search_memories(query, user_id?, top_k?)` | Hybrid semantic search (default `top_k=5`) |
| `list_memories(user_id?, top_k?)` | Recent memories without semantic ranking |
| `get_memory(memory_id)` | Fetch one record by id |

Pass `user_id` when working on behalf of a named user or multi-tenant project; otherwise omit to use the server default.

## Workflow

```
New chat / ambiguous context
        ↓
search_memories(relevant query, top_k=3)
        ↓
Use hits in plan or answer
        ↓
User shares durable preference or fact
        ↓
add_memory(text)  [infer=true unless verbatim]
```

## Errors and prerequisites

- **`CURSOR_API_KEY` missing** — tell the user to create a key at [Dashboard → Integrations](https://cursor.com/dashboard/integrations) and add it to project `.env` or shell env.
- **MCP server offline** — suggest enabling `cursor-mem` in Cursor Settings → MCP and reloading the window.
- **First `uvx` run slow** — normal; dependencies download once from PyPI (`cursor-mem0[mcp]`).

## Install pointer

Users can add the server from [cursor.directory/plugins/cursor-mem](https://cursor.directory/plugins/cursor-mem) or copy `mcp.json` to `.cursor/mcp.json`. Requires [uv](https://docs.astral.sh/uv/) on PATH.
