# Contributing

Contributions to Hedera Realtime Charts are welcome!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/livevnx8/hedera-realtime-charts.git
cd hedera-realtime-charts

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

## Code Style

This project uses Black for code formatting:

```bash
black src/ examples/
```

## Type Checking

This project uses mypy for type checking:

```bash
mypy src/
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Pull Request Guidelines

- Include tests for new features
- Update documentation as needed
- Ensure all tests pass
- Follow the existing code style
- Add disclaimers for any new data sources

## Public API Expectations

The public API should remain stable. Breaking changes should be avoided unless necessary and should be documented.

## Boundary Checks

- **No private keys** or credentials
- **No internal infrastructure** exposure
- **Public data sources only**
- **Clear disclaimers** for all data use
- **No financial advice** or trading recommendations

## Questions?

Feel free to open an issue for questions or discussions.
