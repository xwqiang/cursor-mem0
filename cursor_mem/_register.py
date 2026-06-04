"""Register Cursor LLM provider with mem0 factories (idempotent)."""

_registered = False


def register_cursor_provider() -> None:
    global _registered
    if _registered:
        return

    from mem0.utils.factory import LlmFactory

    from cursor_mem.configs.llms.cursor import CursorConfig

    if "cursor" not in LlmFactory.get_supported_providers():
        LlmFactory.register_provider(
            "cursor",
            "cursor_mem.llms.cursor.CursorLLM",
            CursorConfig,
        )
    _registered = True
