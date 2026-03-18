# Contributing to LLM Gateway Analysis

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## How Can I Contribute?

### Types of Contributions

- **Bug reports**: Help us identify issues in the analysis scripts or data processing
- **Bug fixes**: Submit patches for identified issues
- **New analysis**: Add new analysis scripts or visualizations
- **Documentation**: Improve README, add examples, clarify instructions
- **Dataset expansion**: Contribute new session data following the existing schema
- **Performance improvements**: Optimize token counting or analysis algorithms
- **Testing**: Add test coverage for existing functionality

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/llm-gateway-analysis.git
   cd llm-gateway-analysis
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development tools
   ```

4. **Run the analysis to verify setup**
   ```bash
   python scripts/analyze.py
   python scripts/visualize.py
   ```

5. **Run tests** (once test suite is available)
   ```bash
   pytest
   ```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use `black` for code formatting: `black scripts/`
- Use `ruff` for linting: `ruff check scripts/`
- Line length: 100 characters
- Use type hints where practical

### Code Quality

- Write clear, self-documenting code with meaningful variable names
- Add docstrings to functions and modules
- Keep functions focused and small
- Add comments for complex logic
- Avoid premature optimization

### Testing

- Add tests for new functionality
- Ensure existing tests pass before submitting PR
- Aim for high test coverage on utility functions
- Include both unit tests and integration tests where appropriate

### Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(analysis): add per-session overhead visualization

fix(token_counter): correct token counting for nested JSON

docs(README): add troubleshooting section
```

## Submitting Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   pytest                          # Run tests
   python scripts/analyze.py       # Verify analysis still works
   black scripts/                  # Format code
   ruff check scripts/             # Check for issues
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template
   - Link any related issues

### Pull Request Guidelines

- **Title**: Use conventional commit format
- **Description**: Clearly explain what changes were made and why
- **Link issues**: Reference any related issues with `Fixes #123` or `Relates to #456`
- **Tests**: Ensure all tests pass
- **Documentation**: Update README or other docs if needed
- **Small PRs**: Keep PRs focused on a single change when possible
- **Review ready**: Mark PR as ready for review only when complete

## Reporting Bugs

Before submitting a bug report:
1. Check existing issues to avoid duplicates
2. Try to reproduce with the latest version
3. Isolate the problem to a specific script or function

When submitting a bug report, include:
- **Clear title**: Briefly describe the issue
- **Steps to reproduce**: Exact steps to trigger the bug
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: Python version, OS, dependency versions
- **Error messages**: Full error output or stack trace
- **Sample data**: Minimal example that reproduces the issue (if applicable)

Use the bug report template when creating an issue.

## Suggesting Enhancements

We welcome ideas for improvements! When suggesting enhancements:

- **Check existing issues**: Your idea might already be proposed
- **Be specific**: Clearly describe the enhancement and its benefits
- **Provide context**: Explain the use case or problem it solves
- **Consider scope**: Think about how it fits with project goals

Use the feature request template when creating an issue.

## Dataset Contributions

When contributing new session data:

1. Follow the existing JSON schema in `sessions/all_sessions.json`
2. Include all required fields:
   - `session_id`: Use next available ID (S12, S13, etc.)
   - `session_type`: Descriptive category
   - `description`: What the session demonstrates
   - `turns`: Complete turn-by-turn breakdown
3. Add analysis metadata to each turn
4. Update the sessions overview table in README
5. Regenerate analysis CSVs to include new data

## Questions?

If you have questions about contributing:
- Open a GitHub Discussion
- Check existing documentation
- Ask in an issue or PR

Thank you for contributing! 🎉
