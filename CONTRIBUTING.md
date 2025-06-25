# Contributing to spreadsheet-agent

Thank you for your interest in making spreadsheet-agent better! This guide will help you contribute effectively and ensure a smooth, consistent experience for everyone.

---

## 1. Quick Start
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

## 2. Submitting Pull Requests
- **Use the provided pull request template.** Fill out all sections and complete the pre-submission checklist before submitting your PR.
- The checklist includes: following this contributing guide, adhering to code style, adding tests and documentation, ensuring all checks pass, and providing enough context for reviewers.
- PRs that do not follow the template or checklist may be delayed or closed.

---

## 3. Reporting Bugs & Requesting Features
- **Use the provided GitHub issue templates** for feature requests and bug reports. These templates will guide you to provide all necessary information for maintainers to understand and address your request efficiently.
- For feature requests, fill out the user story, acceptance criteria, technical plan, and checklist as prompted.
- For bugs, provide clear steps to reproduce, expected and actual behavior, and any relevant logs or screenshots.

---

## 4. Dependency Management
- All dependencies, including development tools (pre-commit, ruff, ty, pytest, etc.), are managed in `pyproject.toml`.
- Dev dependencies are listed under `[dependency-groups]` in `pyproject.toml`.
- Use `uv sync --dev` to install everything needed for development.

## 5. Tool Configuration
- Linting, formatting, and import sorting are configured in the `[tool.ruff]` sections of `pyproject.toml`.
- Project-specific scripts can be added under `[tool.hatch.envs.default.scripts]`.

---

## 6. Code Style & Quality
- **Style Guide:** [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- **Linting & Formatting:** [Ruff](https://docs.astral.sh/ruff/) for linting, formatting, and import sorting
- **Type Safety:** All code must have explicit type annotations and pass [`ty`](https://github.com/hynek/ty) checks
- **Reference:** See `.cursor/rules/python-style.mdc` for detailed style rules

## 7. Testing
- **Framework:** [pytest](https://docs.pytest.org/en/stable/)
- **Test Location:** All tests in the `tests/` directory
- **Naming:**
  - Test files: `test_*.py` or `*_test.py`
  - Test classes: `Test*`
  - Test functions: `test_*`
- **Reference:** See `.cursor/rules/pytest-rules.mdc` for detailed testing rules

## 8. Pre-commit Hooks
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

## 9. Git Workflow
- **Fork & PR:** Always fork the repo and submit changes via pull requests. Do not push directly to `main` or `develop`.
- **Feature Branches:** Create a new branch for each feature or fix.
- **Commit Messages:** Use [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `feat(auth): add login with Google`).
- **Branch Naming:** Use descriptive names (see project rules for details).
- **Protected Branches:** All changes must come through pull requests.

---

## 10. To Be Detailed

### Environment Setup
- Use `uv` for environment and dependency management.
- [Instructions to be added.]

### Running Tests & Linting
- How to run tests, lint, and type checks locally before submitting a PR.
- [Instructions to be added.]

### Code Review Process
- How to request a review and what to expect.
- [Instructions to be added.]

---

## Windows-specific Setup Notes

- After running `uv run pre-commit install`, convert `.git/hooks/pre-commit` to Unix (LF) line endings:
  - In VS Code: Open the file, click the line ending selector (bottom right), choose "LF", and save.
  - Or, in Git Bash/WSL: run `dos2unix .git/hooks/pre-commit`
- When committing, always use:
  ```
  uv run git commit -m "your message"
  ```
  This ensures the pre-commit hook can find the correct environment and dependencies.
- If you see errors about missing `pre-commit` or line endings, follow the above steps to resolve them.

---

## Additional Resources
- [README.md](./README.md)
- `.cursor/rules/` for all project rules

---

## Recommended: Global CLI Tool Installation

For developer convenience, you may install common CLI tools globally using uv:

```
uv tool install pre-commit ruff ty --with pre-commit-uv
```

- This makes `pre-commit`, `ruff`, and `ty` available everywhere, regardless of your virtual environment.
- You can then use these tools directly in your shell and in pre-commit hooks without environment issues.
- We still recommend keeping these tools in your dev dependencies for reproducibility and CI.

See: https://adamj.eu/tech/2025/05/07/pre-commit-install-uv/

---

**Summary:**
- Always use the provided templates for PRs and issues.
- Follow the code style, testing, and workflow guidelines.
- Ensure all checks pass before submitting your work.
- When in doubt, ask questions or suggest improvements—collaboration is welcome!
