# Changelog

All notable changes to **cursor-mem0** are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.2] - 2026-06-09

### Added

- Agent skill at `skills/cursor-mem/SKILL.md` for MCP memory workflows (cursor.directory / Open Plugins).
- Expanded discovery keywords in plugin manifest and PyPI metadata.
- This changelog.

### Fixed

- Pin `uvx` to Python 3.12 in MCP configs so `onnxruntime` / fastembed wheels install on systems where Python 3.10 lacks compatible builds.
- Document Python 3.11+ requirement for the library; MCP via `uvx` uses 3.12 explicitly.

### Changed

- Cursor plugin manifest description aligned with Marketplace listing copy.
- Marketplace logotype (`assets/logo.png`).

## [0.1.1] - 2026-06-04

### Added

- GitHub topics and repo discoverability tooling (`scripts/github-repo-setup.sh`).
- README demo GIF and Chinese README (`README.zh-CN.md`).

### Changed

- Public documentation refactor; user-focused install and MCP guides.

## [0.1.0] - 2026-06-04

### Added

- Initial PyPI release: `cursor-mem0` mem0-compatible memory layer using Cursor SDK (`CURSOR_API_KEY`).
- Local embeddings (fastembed) and on-disk Qdrant vector store.
- MCP server with `add_memory`, `search_memories`, `list_memories`, `get_memory`.
- Cursor plugin manifest (`.cursor-plugin/plugin.json`) and MCP discovery configs (`mcp.json`, `.mcp.json`).
- GitHub Actions test workflow; publish workflow for PyPI on release.

[0.1.2]: https://github.com/xwqiang/cursor-mem0/releases/tag/v0.1.2
