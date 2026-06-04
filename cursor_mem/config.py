import os
from typing import Any, Dict, Optional

from mem0.configs.base import MemoryConfig
from mem0.configs.vector_stores.qdrant import QdrantConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.llms.configs import LlmConfig
from mem0.vector_stores.configs import VectorStoreConfig

from cursor_mem._register import register_cursor_provider

FASTEMBED_MODEL = "thenlper/gte-large"
FASTEMBED_DIMS = 1024


def cursor_mem_dir() -> str:
    path = os.environ.get("CURSOR_MEM_DIR") or os.path.join(os.path.expanduser("~"), ".cursor-mem")
    os.makedirs(path, exist_ok=True)
    return path


def default_config(
    *,
    user_collection: str = "cursor_mem",
    model: str = "composer-2.5",
    cwd: Optional[str] = None,
    api_key: Optional[str] = None,
    embedder_model: str = FASTEMBED_MODEL,
    embedding_dims: int = FASTEMBED_DIMS,
) -> MemoryConfig:
    """
    Default MemoryConfig: Cursor SDK for LLM, local fastembed for vectors, local Qdrant.

    Only CURSOR_API_KEY is required for cloud LLM calls. Embeddings run locally (no API key).
    """
    register_cursor_provider()
    base = cursor_mem_dir()
    return MemoryConfig.model_construct(
        vector_store=VectorStoreConfig.model_construct(
            provider="qdrant",
            config=QdrantConfig(
                collection_name=user_collection,
                path=os.path.join(base, "qdrant"),
                embedding_model_dims=embedding_dims,
                on_disk=True,
            ),
        ),
        llm=LlmConfig.model_construct(
            provider="cursor",
            config={
                "api_key": api_key or os.environ.get("CURSOR_API_KEY"),
                "model": model,
                "cwd": cwd or os.getcwd(),
            },
        ),
        embedder=EmbedderConfig.model_construct(
            provider="fastembed",
            config={"model": embedder_model},
        ),
        history_db_path=os.path.join(base, "history.db"),
        version="v1.1",
    )


def merge_config_dict(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Apply cursor-mem defaults to a mem0-style config dict."""
    register_cursor_provider()
    data = dict(config_dict)
    llm = data.get("llm") or {}
    if isinstance(llm, dict):
        llm = dict(llm)
        llm.setdefault("provider", "cursor")
        data["llm"] = llm
    embedder = data.get("embedder") or {}
    if isinstance(embedder, dict):
        embedder = dict(embedder)
        embedder.setdefault("provider", "fastembed")
        embedder.setdefault("config", embedder.get("config") or {"model": FASTEMBED_MODEL})
        data["embedder"] = embedder
    return data
