# Contributing to Personalized Email Automation Tool

Thank you for your interest in contributing to this project! We welcome contributions from developers of all skill levels.

## Quick Links

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Testing](#testing)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/). By participating, you are expected to uphold this code.

## Getting Started

### Types of Contributions

We welcome many different types of contributions:

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Implement bug fixes or new features
- **Documentation**: Improve or expand documentation
- **Testing**: Add or improve test coverage
- **Examples**: Create usage examples and tutorials

### Before You Start

1. Check if there's already an issue for what you want to work on
2. For new features, create an issue first to discuss the approach
3. Look at existing code to understand the project structure and style

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- A code editor (VS Code recommended)

### Setup Steps

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/personalized-email-automation.git
   cd personalized-email-automation
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   # If you're adding new dependencies, also install development tools
   pip install pytest black flake8 mypy
   ```

4. **Setup Environment**
   ```bash
   cp .env.example .env
   # Add your test API keys (use separate test accounts)
   ```

5. **Verify Setup**
   ```bash
   python run.py data/sample_prospects.csv --test-mode
   ```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-outlook-support`
- `bugfix/fix-csv-parsing`
- `docs/improve-readme`
- `test/add-email-tests`

### Commit Messages

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

Examples:
```
feat(email): add Outlook email provider support

- Add Outlook SMTP configuration
- Update email sender to handle different providers
- Add tests for Outlook authentication

Fixes #123
```

## Style Guidelines

### Python Code Style

- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters (Black default)
- Use descriptive variable names
- Include docstrings for all public functions and classes

### Code Formatting

We use Black for automatic code formatting:
```bash
black src/
```

### Linting

We use flake8 for linting:
```bash
flake8 src/
```

### Type Checking

We use mypy for type checking:
```bash
mypy src/
```

### Example Good Code

```python
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class EmailSender:
    """Handles email sending functionality for different providers."""
    
    def __init__(self, config: Dict[str, str]) -> None:
        """
        Initialize email sender with configuration.
        
        Args:
            config: Dictionary containing email configuration
        """
        self.config = config
        self.smtp_server: Optional[smtplib.SMTP] = None
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str
    ) -> bool:
        """
        Send an email to the specified recipient.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body content
            
        Returns:
            True if email was sent successfully, False otherwise
            
        Raises:
            EmailError: If email sending fails
        """
        try:
            # Implementation here
            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            raise EmailError(f"Email sending failed: {e}")
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific test file
python -m pytest tests/test_email_sender.py

# Run with verbose output
python -m pytest -v
```

### Writing Tests

- Write unit tests for all new functions
- Include edge cases and error conditions
- Use descriptive test names
- Mock external dependencies (APIs, network calls)

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch
from src.email_automation.email_sender import EmailSender

class TestEmailSender:
    def setup_method(self):
        """Setup run before each test method."""
        self.config = {
            "EMAIL_ADDRESS": "test@example.com",
            "EMAIL_PASSWORD": "password",
            "SMTP_SERVER": "smtp.gmail.com",
            "SMTP_PORT": "587"
        }
        self.sender = EmailSender(self.config)
    
    def test_send_email_success(self):
        """Test successful email sending."""
        with patch('smtplib.SMTP') as mock_smtp:
            result = self.sender.send_email(
                "recipient@example.com", 
                "Test Subject", 
                "Test Body"
            )
            assert result is True
            mock_smtp.assert_called_once()
    
    def test_send_email_failure(self):
        """Test email sending failure handling."""
        with patch('smtplib.SMTP', side_effect=Exception("SMTP Error")):
            with pytest.raises(EmailError):
                self.sender.send_email(
                    "recipient@example.com", 
                    "Test Subject", 
                    "Test Body"
                )
```

## Submitting Changes

### Pull Request Process

1. **Create Pull Request**
   - Use the pull request template
   - Fill in all sections completely
   - Reference related issues

2. **PR Requirements**
   - [ ] All tests pass
   - [ ] Code is properly formatted (Black)
   - [ ] No linting errors (flake8)
   - [ ] Type checking passes (mypy)
   - [ ] Documentation is updated
   - [ ] No secrets in code

3. **Review Process**
   - Maintainers will review your PR
   - Address any feedback promptly
   - Keep PR updated with main branch

### What to Expect

- Initial response within 48 hours
- Full review within 1 week
- Feedback on code quality, tests, documentation
- Possible requests for changes

## Development Guidelines

### File Organization

```
src/email_automation/
├── __init__.py          # Package initialization
├── config_manager.py    # Configuration handling
├── prospect_manager.py  # Data management
├── website_analyzer.py  # Web analysis
├── ai_analyzer.py       # AI functionality
├── email_generator.py   # Email creation
├── email_sender.py      # Email delivery
└── main.py             # Main orchestrator
```

### Error Handling

- Use specific exception types
- Include helpful error messages
- Log errors appropriately
- Don't expose sensitive information in errors

### Logging

- Use the logging module
- Include appropriate log levels
- Don't log sensitive information (API keys, passwords)
- Include context in log messages

### Security Considerations

- Never commit API keys or credentials
- Sanitize user input
- Use secure methods for handling sensitive data
- Follow OWASP guidelines

## Getting Help

- **Documentation**: Check the README and code comments
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Ask for feedback on draft PRs

## Recognition

Contributors are recognized in:
- GitHub contributor graphs
- Release notes for significant contributions
- Special thanks in documentation

Thank you for contributing to make this project better for everyone!
