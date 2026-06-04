"""
MCP server for cursor-mem — exposes add / search / list to Cursor agents.

Run: python -m cursor_mem.mcp_server
Loads CURSOR_API_KEY from .env in the project cwd when present.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore[misc, assignment]

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:
    raise ImportError(
        "MCP dependencies missing. Install with: pip install -e \".[mcp]\""
    ) from exc

mcp = FastMCP("cursor-mem")

_memory = None
_default_user_id = os.environ.get("CURSOR_MEM_USER_ID", "default_user")


def _load_env() -> None:
    if load_dotenv is None:
        return
    root = Path(__file__).resolve().parents[1]
    # Package defaults first, then cwd (workspace) overrides — e.g. project:goldwin user_id
    load_dotenv(root / ".env")
    load_dotenv(override=True)


def _get_memory():
    global _memory
    if _memory is None:
        _load_env()
        if not os.environ.get("CURSOR_API_KEY"):
            raise RuntimeError(
                "CURSOR_API_KEY is not set. Add it to .env or export it in the shell."
            )
        from cursor_mem import Memory

        _memory = Memory()
        logger.info("cursor-mem Memory initialized")
    return _memory


@mcp.tool(
    description=(
        "Add a memory for the user. Call when the user shares preferences, facts, "
        "or asks you to remember something. Set infer=false to store text verbatim."
    )
)
def add_memory(text: str, user_id: str = "", infer: bool = True) -> str:
    uid = user_id.strip() or _default_user_id
    try:
        result = _get_memory().add(text, user_id=uid, infer=infer)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.exception("add_memory failed")
        return json.dumps({"error": str(e)})


@mcp.tool(description="Search stored memories by natural-language query.")
def search_memories(query: str, user_id: str = "", top_k: int = 5) -> str:
    uid = user_id.strip() or _default_user_id
    try:
        result = _get_memory().search(
            query=query,
            filters={"user_id": uid},
            top_k=top_k,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.exception("search_memories failed")
        return json.dumps({"error": str(e)})


@mcp.tool(description="List recent memories for a user (no semantic search).")
def list_memories(user_id: str = "", top_k: int = 20) -> str:
    uid = user_id.strip() or _default_user_id
    try:
        result = _get_memory().get_all(filters={"user_id": uid}, top_k=top_k)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.exception("list_memories failed")
        return json.dumps({"error": str(e)})


@mcp.tool(description="Get a single memory by id.")
def get_memory(memory_id: str) -> str:
    try:
        result = _get_memory().get(memory_id)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.exception("get_memory failed")
        return json.dumps({"error": str(e)})


def main() -> None:
    _load_env()
    mcp.run()


if __name__ == "__main__":
    main()
