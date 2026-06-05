# Publishing to PyPI

Package name on PyPI: **`cursor-mem0`** (Python import: `cursor_mem`).

## One-time setup

1. Create a [PyPI](https://pypi.org/account/register/) account.
2. Create an API token at [pypi.org/manage/account/token/](https://pypi.org/manage/account/token/) (scope: entire account or project `cursor-mem0`).
3. Configure credentials locally (do not commit):

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmcC...
```

Or add to `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-...
```

## Release a version

1. Bump `version` in `pyproject.toml`.
2. Build and verify:

```bash
pip install build twine
rm -rf dist/
python -m build
twine check dist/*
```

3. Upload:

```bash
twine upload dist/*
```

4. Tag on GitHub (optional, for CI publish):

```bash
git tag v0.1.0
git push origin v0.1.0
# Create a GitHub Release from the tag to trigger .github/workflows/publish.yml
```

## GitHub Actions

- **Test:** runs on push/PR (`.github/workflows/test.yml`).
- **Publish:** runs on GitHub Release `published` or manual `workflow_dispatch`. Add repository secret or environment **`pypi`** with trusted publishing, or use OIDC on PyPI project settings.

## Public Git repository

```bash
gh auth login
gh repo create cursor-mem0 --public --source=. --remote=origin
git push -u origin main
```

Then update `[project.urls]` in `pyproject.toml` with your real GitHub URLs and publish a new patch version.

## List in Cursor (discovery)

After a PyPI release, submit the public repo so users can find it in Cursor:

1. **cursor.directory** (community, do this first): [cursor.directory/plugins/new](https://cursor.directory/plugins/new) — paste `https://github.com/xwqiang/cursor-mem0`. Auto-detects `.mcp.json` / `mcp.json` and `.cursor-plugin/plugin.json`.
2. **MCP.Directory**: [mcp.directory/submit](https://mcp.directory/submit) — GitHub URL + PyPI package `cursor-mem0`.
3. **Cursor Marketplace** (official, manual review): [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish) — requires `.cursor-plugin/plugin.json` at repo root.

Repo files used for discovery:

| File | Purpose |
|------|---------|
| `mcp.json` | Cursor plugin MCP config (`uvx --python 3.12` + PyPI) |
| `.mcp.json` | Open Plugins / cursor.directory detection |
| `.cursor-plugin/plugin.json` | Marketplace plugin manifest |
