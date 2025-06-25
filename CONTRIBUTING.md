# Contributing to spreadsheet-agent

Thank you for your interest in contributing! Please read these guidelines to help us maintain a high-quality, consistent codebase.

## Git Workflow
- **Fork and Pull Request:** Fork the repository and submit changes via pull requests. No direct pushes to `main` or `develop`.
- **Feature Branches:** Create a new branch for each feature or fix.
- **Commit Messages:** Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.
- **Branch Naming:** Use descriptive names following the project's branch naming conventions.
- **Protected Branches:** All changes must come through pull requests.

## Code Style
- **Style Guide:** Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
- **Linting & Formatting:** Use [Ruff](https://docs.astral.sh/ruff/) for linting, formatting, and import sorting.
- **Type Safety:** Use [`ty`](https://github.com/hynek/ty) for type checking. All code must have explicit type annotations.
- **Reference:** See `.cursor/rules/python-style.mdc` for detailed style rules.

## Testing
- **Framework:** Use [pytest](https://docs.pytest.org/en/stable/) for all tests.
- **Test Location:** Place all tests in the `tests/` directory.
- **Naming:** Test files: `test_*.py` or `*_test.py`. Test classes: `Test*`. Test functions: `test_*`.
- **Reference:** See `.cursor/rules/pytest-rules.mdc` for detailed testing rules.

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

*This document will evolve as our workflow and culture develop. Feel free to suggest improvements!* 