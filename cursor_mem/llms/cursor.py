import logging
import os
from typing import Dict, List, Optional, Union

from cursor_sdk import Agent, AgentOptions, CursorAgentError, LocalAgentOptions
from mem0.configs.llms.base import BaseLlmConfig
from mem0.llms.base import LLMBase

from cursor_mem.configs.llms.cursor import CursorConfig

logger = logging.getLogger(__name__)


def _format_messages(messages: List[Dict[str, str]], response_format=None) -> str:
    parts: List[str] = []
    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")
        if content is None:
            content = ""
        parts.append(f"[{role.upper()}]\n{content}")

    if response_format and response_format.get("type") == "json_object":
        parts.append(
            "[INSTRUCTION]\n"
            "Reply with a single valid JSON object only. "
            "No markdown fences, no commentary before or after the JSON."
        )
    return "\n\n".join(parts)


class CursorLLM(LLMBase):
    """LLM provider that routes all inference through cursor-sdk (CURSOR_API_KEY)."""

    def __init__(self, config: Optional[Union[BaseLlmConfig, CursorConfig, Dict]] = None):
        if config is None:
            config = CursorConfig()
        elif isinstance(config, dict):
            config = CursorConfig(**config)
        elif isinstance(config, BaseLlmConfig) and not isinstance(config, CursorConfig):
            config = CursorConfig(
                model=config.model,
                temperature=config.temperature,
                api_key=config.api_key,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                top_k=config.top_k,
            )
        super().__init__(config)
        if not self.config.model:
            self.config.model = "composer-2.5"

    def generate_response(
        self,
        messages: List[Dict[str, str]],
        response_format=None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        **kwargs,
    ):
        if tools:
            logger.warning("CursorLLM does not support tool calls; ignoring tools parameter.")

        prompt = _format_messages(messages, response_format=response_format)
        api_key = self.config.api_key or os.environ.get("CURSOR_API_KEY")
        if not api_key:
            raise ValueError(
                "CURSOR_API_KEY is required. Set the environment variable or pass api_key in config."
            )

        cwd = getattr(self.config, "cwd", None) or os.getcwd()
        opts: Dict[str, object] = {
            "api_key": api_key,
            "model": self.config.model,
            "local": LocalAgentOptions(cwd=cwd),
        }
        mode = getattr(self.config, "mode", None)
        if mode:
            opts["mode"] = mode
        options = AgentOptions(**opts)

        try:
            run_result = Agent.prompt(prompt, options)
        except CursorAgentError as err:
            logger.error("Cursor agent startup failed: %s", err.message)
            raise

        if run_result.status == "error":
            raise RuntimeError(f"Cursor agent run failed (run_id={run_result.id})")

        text = (run_result.result or "").strip()
        if response_format and response_format.get("type") == "json_object":
            return text
        return text
