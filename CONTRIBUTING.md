# Contributing

Thank you for your interest in this project!

## How to Contribute

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and ensure all tests pass: `pytest tests/ -v`
4. Commit with a clear message: `git commit -m "Add: description of change"`
5. Push and open a Pull Request against `main`

## Running Tests

pip install -r requirements.txt
python insights.py
pytest tests/ -v

## Code Standards

- Follow PEP 8 for Python
- Add docstrings to any new functions
- All new analytical logic should have a corresponding test in tests/test_insights.py
- SQL queries should include a business context comment header

## Reporting Issues

Open a GitHub Issue with a clear description of the problem and steps to reproduce.
