from typing import Any, Dict, Optional

from mem0 import Memory as Mem0Memory
from mem0.configs.base import MemoryConfig
from mem0.configs.vector_stores.qdrant import QdrantConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.llms.configs import LlmConfig
from mem0.vector_stores.configs import VectorStoreConfig

from cursor_mem._register import register_cursor_provider
from cursor_mem.config import default_config, merge_config_dict


def _memory_config_from_dict(config_dict: Dict[str, Any]) -> MemoryConfig:
    """Build MemoryConfig from dict, allowing provider=cursor without pydantic rejection."""
    data = merge_config_dict(config_dict)
    vs = data.get("vector_store") or {}
    vs_provider = vs.get("provider", "qdrant")
    vs_config = vs.get("config") or {}
    if vs_provider == "qdrant" and isinstance(vs_config, dict):
        vs_config_obj = QdrantConfig(**vs_config)
    else:
        vs_config_obj = vs_config

    llm = data.get("llm") or {}
    embedder = data.get("embedder") or {}

    return MemoryConfig.model_construct(
        vector_store=VectorStoreConfig.model_construct(
            provider=vs_provider,
            config=vs_config_obj,
        ),
        llm=LlmConfig.model_construct(
            provider=llm.get("provider", "cursor"),
            config=llm.get("config") or {},
        ),
        embedder=EmbedderConfig.model_construct(
            provider=embedder.get("provider", "fastembed"),
            config=embedder.get("config") or {},
        ),
        history_db_path=data.get("history_db_path"),
        version=data.get("version", "v1.1"),
        custom_instructions=data.get("custom_instructions"),
        reranker=data.get("reranker"),
    )


class Memory(Mem0Memory):
    """
    mem0-compatible memory layer using Cursor SDK for LLM inference.

    All add/search/update/delete logic is inherited from mem0 unchanged.
    LLM calls use CURSOR_API_KEY via cursor-sdk; embeddings use local fastembed.
    """

    def __init__(self, config: Optional[MemoryConfig] = None):
        register_cursor_provider()
        super().__init__(config or default_config())

    @classmethod
    def from_config(cls, config_dict: Dict[str, Any]) -> "Memory":
        register_cursor_provider()
        return cls(_memory_config_from_dict(config_dict))
