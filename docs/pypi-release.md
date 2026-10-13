# SpectralAudit release guide: GitHub Actions + PyPI Trusted Publishing

**The workflows do not publish anything until explicitly triggered.**
No long-lived PyPI tokens are stored in the repository.

## Author actions before the first release

1. Ensure project name `spectralaudit` remains available on [PyPI](https://pypi.org/) and [TestPyPI](https://test.pypi.org/); these are separate indexes.
2. On GitHub, go to repository **Settings → Environments**. Create `pypi` and
   `testpypi`. Protect production `pypi` with required human approval and
   restrict to permitted release tags if desired.
3. Under the PyPI account's **Publishing** page
   (https://pypi.org/manage/account/publishing/), create a pending
   Trusted Publisher with the following **exact** fields:
   - PyPI project: `spectralaudit`
   - GitHub owner: `edujbarrios`
   - Repository: `spectralaudit`
   - Workflow filename: `publish.yml`
   - Environment: `pypi`
4. Under [TestPyPI Publishing](https://test.pypi.org/manage/account/publishing/),
   register a separate pending publisher with the same owner/repository/workflow,
   project name, and environment `testpypi`.
5. Enable suitable release permissions and confirm actions are enabled.

A pending publisher does *not* reserve a project name. Verify account settings
and ownership before triggering publication.

## Local verification (before publishing)

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m build
python -m twine check dist/*
python -m pip install dist/spectralaudit-0.1.0-py3-none-any.whl
spectralaudit --version
```

## First TestPyPI run

On GitHub → Actions → **Publish Python package** → Run workflow, select
`target=testpypi`. After release, test an isolated installation. Note that
TestPyPI may not provide all dependencies, so allow fetching dependencies from
normal PyPI with care:

```bash
python -m pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ spectralaudit==0.1.0
```

For stronger supply-chain guarantees, pin dependencies or install them from
PyPI first and install only the distribution from TestPyPI using `--no-deps`.

## Publish production

Once approved and green, create the signed or annotated Git tag:

```bash
git tag -a v0.1.0 -m "SpectralAudit v0.1.0"
git push origin v0.1.0
```

In GitHub, publish a Release for `v0.1.0` (not a draft). This triggers
`.github/workflows/publish.yml` with the `pypi` environment, protected
approval and OIDC credentials. The publication job does not execute package
build scripts; it only downloads previously built distribution artifacts.

Confirm published package at https://pypi.org/project/spectralaudit/ and test
fresh environment installation: `python -m pip install spectralaudit`.

## Next releases

Update `pyproject.toml`, `src/spectralaudit/__init__.py`, `CITATION.cff`,
CHANGELOG and docs to the same new version, run CI, and release the matching tag.
Never reuse an uploaded version number (PyPI files are immutable).

Official guidance:
- https://docs.pypi.org/trusted-publishers/using-a-publisher/
- https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/
- https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/
