import os
from unittest.mock import MagicMock, patch

import pytest

from cursor_mem.llms.cursor import CursorLLM, _format_messages


def test_format_messages_json_instruction():
    prompt = _format_messages(
        [{"role": "system", "content": "Extract"}, {"role": "user", "content": "Hello"}],
        response_format={"type": "json_object"},
    )
    assert "[SYSTEM]" in prompt
    assert "valid JSON object" in prompt


def test_cursor_llm_requires_api_key():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("CURSOR_API_KEY", None)
        llm = CursorLLM({"api_key": None})
        with pytest.raises(ValueError, match="CURSOR_API_KEY"):
            llm.generate_response([{"role": "user", "content": "hi"}])


@patch("cursor_mem.llms.cursor.Agent.prompt")
def test_cursor_llm_returns_text(mock_prompt):
    mock_prompt.return_value = MagicMock(status="finished", result='{"memory": []}', id="run-1")
    llm = CursorLLM({"api_key": "cursor_test"})
    out = llm.generate_response(
        [{"role": "user", "content": "test"}],
        response_format={"type": "json_object"},
    )
    assert "memory" in out
    mock_prompt.assert_called_once()
