# Contributing to agent-preflight

Thank you for your interest in contributing to agent-preflight!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/just-sree/agent-preflight.git
   cd agent-preflight
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install in editable mode along with testing dependencies:
   ```bash
   pip install -e ".[test]"
   ```

4. Run tests:
   ```bash
   python -m pytest
   ```

## Pull Request Process

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make changes, ensuring existing tests pass and adding new tests as needed.
4. Submit a Pull Request targeting the `main` branch.
