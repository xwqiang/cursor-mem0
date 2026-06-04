from typing import Optional

from mem0.configs.llms.base import BaseLlmConfig


class CursorConfig(BaseLlmConfig):
    """LLM configuration for Cursor SDK (CURSOR_API_KEY)."""

    def __init__(
        self,
        model: Optional[str] = "composer-2.5",
        temperature: float = 0.1,
        api_key: Optional[str] = None,
        max_tokens: int = 8000,
        top_p: float = 0.1,
        top_k: int = 1,
        cwd: Optional[str] = None,
        mode: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            model=model,
            temperature=temperature,
            api_key=api_key,
            max_tokens=max_tokens,
            top_p=top_p,
            top_k=top_k,
            **kwargs,
        )
        self.cwd = cwd
        self.mode = mode
