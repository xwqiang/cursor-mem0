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
