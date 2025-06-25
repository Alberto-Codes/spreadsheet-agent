# Contributing to spreadsheet-agent

Thank you for your interest in making spreadsheet-agent better! This guide will help you contribute effectively and ensure a smooth, consistent experience for everyone.

---

## Quick Start
1. **Fork** the repository and create a feature branch.
2. **Install all dependencies (including dev tools):**
   ```bash
   uv sync --dev
   ```
3. **Set up pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```
4. **Make your changes,** following our code style and testing guidelines.
5. **Run all pre-commit hooks, tests, and type checks locally:**
   ```bash
   uv run pre-commit run --all-files
   uv run pytest
   uv run ty check .
   ```
6. **Submit a pull request (PR) to the `develop` branch.**

---

## Dependency Management
- All dependencies, including development tools (pre-commit, ruff, ty, pytest, etc.), are managed in `pyproject.toml`.
- Dev dependencies are listed under `[project.optional-dependencies.dev]`.
- Use `uv sync --dev` to install everything needed for development.

## Tool Configuration
- Linting, formatting, and import sorting are configured in the `[tool.ruff]` sections of `pyproject.toml`.
- Project-specific scripts can be added under `[tool.hatch.envs.default.scripts]`.

---

## Code Style & Quality
- **Style Guide:** [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- **Linting & Formatting:** [Ruff](https://docs.astral.sh/ruff/) for linting, formatting, and import sorting
- **Type Safety:** All code must have explicit type annotations and pass [`ty`](https://github.com/hynek/ty) checks
- **Reference:** See `.cursor/rules/python-style.mdc` for detailed style rules

## Testing
- **Framework:** [pytest](https://docs.pytest.org/en/stable/)
- **Test Location:** All tests in the `tests/` directory
- **Naming:**
  - Test files: `test_*.py` or `*_test.py`
  - Test classes: `Test*`
  - Test functions: `test_*`
- **Reference:** See `.cursor/rules/pytest-rules.mdc` for detailed testing rules

## Pre-commit Hooks
We use [pre-commit](https://pre-commit.com/) to automate code quality checks before every commit. **All contributors must install and use pre-commit.**

### What Gets Checked?
- **YAML files:** Validity (`check-yaml`)
- **End-of-file:** Ensures newline at end (`end-of-file-fixer`)
- **Trailing whitespace:** Removed automatically (`trailing-whitespace`)
- **Python code:** Linting and formatting (`ruff`, `ruff-format`)
- **Type checking:** Runs `uv run ty check .` (`ty-check`)

### How to Set Up
1. Install all dependencies (including dev dependencies):
   ```bash
   uv sync --dev
   ```
2. Install the hooks:
   ```bash
   uv run pre-commit install
   ```
3. (Optional) Run all hooks on all files:
   ```bash
   uv run pre-commit run --all-files
   ```
> **Note:** Commits will be blocked until all checks pass. Fix any issues before pushing.

---

## Git Workflow
- **Fork & PR:** Always fork the repo and submit changes via pull requests. Do not push directly to `main` or `develop`.
- **Feature Branches:** Create a new branch for each feature or fix.
- **Commit Messages:** Use [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `feat(auth): add login with Google`).
- **Branch Naming:** Use descriptive names (see project rules for details).
- **Protected Branches:** All changes must come through pull requests.

---

## To Be Detailed

### Environment Setup
- Use `uv` for environment and dependency management.
- [Instructions to be added.]

### Running Tests & Linting
- How to run tests, lint, and type checks locally before submitting a PR.
- [Instructions to be added.]

### Code Review Process
- How to request a review and what to expect.
- [Instructions to be added.]

### Reporting Bugs & Requesting Features
- Use GitHub Issues and the provided templates.
- [Instructions to be added.]

---

## Additional Resources
- [README.md](./README.md)
- `.cursor/rules/` for all project rules

---

*This document will evolve as our workflow and culture develop. Suggestions and improvements are always welcome!* 