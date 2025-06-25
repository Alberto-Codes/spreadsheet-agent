# Contributing to spreadsheet-agent

Thank you for your interest in making spreadsheet-agent better! This guide will help you contribute effectively and ensure a smooth, consistent experience for everyone.

## Quick Start Checklist
- Fork the repository and create a feature branch.
- Make your changes, following our code style and testing guidelines.
- Run all pre-commit hooks, tests, and type checks locally.
- Submit a pull request (PR) to the `develop` branch.

---

## Git Workflow
- **Fork & PR:** Always fork the repo and submit changes via pull requests. Do not push directly to `main` or `develop`.
- **Feature Branches:** Create a new branch for each feature or fix.
- **Commit Messages:** Use [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `feat(auth): add login with Google`).
- **Branch Naming:** Use descriptive names (see project rules for details).
- **Protected Branches:** All changes must come through pull requests.

## Code Style & Quality
- **Style Guide:** Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
- **Linting & Formatting:** Use [Ruff](https://docs.astral.sh/ruff/) for linting, formatting, and import sorting.
- **Type Safety:** All code must have explicit type annotations and pass [`ty`](https://github.com/hynek/ty) checks.
- **Reference:** See `.cursor/rules/python-style.mdc` for detailed style rules.

## Testing
- **Framework:** Use [pytest](https://docs.pytest.org/en/stable/) for all tests.
- **Test Location:** Place all tests in the `tests/` directory.
- **Naming:**
  - Test files: `test_*.py` or `*_test.py`
  - Test classes: `Test*`
  - Test functions: `test_*`
- **Reference:** See `.cursor/rules/pytest-rules.mdc` for detailed testing rules.

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

## Environment Setup *(to be detailed)*
- Use `uv` for environment and dependency management.
- [Instructions to be added.]

## Running Tests & Linting *(to be detailed)*
- How to run tests, lint, and type checks locally before submitting a PR.
- [Instructions to be added.]

## Code Review Process *(to be detailed)*
- How to request a review and what to expect.
- [Instructions to be added.]

## Reporting Bugs & Requesting Features *(to be detailed)*
- Use GitHub Issues and the provided templates.
- [Instructions to be added.]

## Additional Resources
- [README.md](./README.md)
- `.cursor/rules/` for all project rules

---

*This document will evolve as our workflow and culture develop. Suggestions and improvements are always welcome!* 