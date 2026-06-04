"""Cursor-powered memory layer for AI agents (mem0-compatible API)."""

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from cursor_mem.memory import Memory
from cursor_mem.config import default_config, cursor_mem_dir

__all__ = ["Memory", "default_config", "cursor_mem_dir"]
