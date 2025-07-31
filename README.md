# Personalized Email Automation Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Issues](https://img.shields.io/github/issues/yourusername/personalized-email-automation)](https://github.com/yourusername/personalized-email-automation/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/yourusername/personalized-email-automation)](https://github.com/yourusername/personalized-email-automation/pulls)

> **⚠️ Important Notice**: This tool is designed for legitimate business outreach only. Please ensure you comply with local email marketing laws (CAN-SPAM Act, GDPR, etc.) and respect website terms of service.

An open-source Python application that analyzes websites and generates highly personalized, industry-specific outreach emails based on comprehensive technical analysis and AI-powered insights.

## Table of Contents

- [About](#about)
- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [CSV Format](#csv-format)
- [How It Works](#how-it-works)
- [Solution Categories](#solution-categories)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Ethical Usage](#ethical-usage)

## About

This tool helps freelancers, consultants, and business development professionals create personalized outreach emails by automatically analyzing target websites and generating relevant business opportunities. Unlike generic email templates, this system provides specific, actionable insights tailored to each prospect's business.

## Key Features

- **🎯 Industry-Specific Analysis**: Tailored insights for 10+ business categories (e-commerce, SaaS, consulting, healthcare, restaurants, etc.)
- **🔍 Comprehensive Website Analysis**: Technical performance, SEO gaps, UX issues, and business opportunities
- **🤖 Advanced AI Insights**: Diverse, actionable recommendations beyond generic suggestions
- **📧 Highly Personalized Emails**: Each email focuses on specific, relevant opportunities unique to the business
- **🛡️ Smart Validation**: Prevents repetitive content and ensures solution diversity
- **🚀 Easy Setup**: Simple installation process with clear documentation
- **💰 Cost-Effective**: Open source with minimal API costs (typically $0.01-0.05 per email)
- **🔧 Modular Design**: Easy to extend and customize for specific needs

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** installed on your system
- **OpenAI API account** with credits (for AI analysis)
- **Email account** (Gmail recommended with App Password)
- **Basic command line knowledge**
- **Stable internet connection** for website analysis

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/personalized-email-automation.git
cd personalized-email-automation
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials (see Configuration section)
```

## Quick Start

### 1. Test the Installation

```bash
# Test mode - no emails will be sent
python run.py data/sample_prospects.csv --test-mode
```

### 2. Test Email Connection

```bash
# Verify your email configuration
python run.py data/sample_prospects.csv --test-email
```

### 3. Run Analysis Only

```bash
# Generate insights without sending emails
python run.py data/sample_prospects.csv --stats-only
```

### 4. Send Your First Email Campaign

```bash
# Start with a small test batch
python run.py data/your_prospects.csv --delay 60
```

## Project Structure

```
personalized-email-automation/
├── 📁 src/
│   └── 📁 email_automation/        # Main application package
│       ├── 📄 __init__.py          # Package initialization
│       ├── 📄 config_manager.py    # Configuration and environment management
│       ├── 📄 prospect_manager.py  # CSV data loading and prospect handling
│       ├── 📄 website_analyzer.py  # Website scraping and technical analysis
│       ├── 📄 ai_analyzer.py       # OpenAI-powered opportunity detection
│       ├── 📄 email_generator.py   # Personalized email content creation
│       ├── 📄 email_sender.py      # Email delivery and tracking
│       └── 📄 main.py              # Application orchestrator and main logic
├── 📁 config/                      # Configuration files (optional)
├── 📁 data/                        # Data directory
│   ├── 📄 sample_prospects.csv     # Example CSV format
│   └── 📄 test_prospects.csv       # Test data for development
├── 📁 logs/                        # Application logs and debugging info
│   └── 📄 email_automation.log     # Main application log file
├── 📁 tests/                       # Test suite (if available)
├── 📄 run.py                       # Command-line interface and entry point
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment variables template
├── 📄 .gitignore                   # Git ignore patterns
├── 📄 LICENSE                      # MIT license file
└── 📄 README.md                    # This documentation file
```

### Module Descriptions

| Module | Purpose | Key Functions |
|--------|---------|--------------|
| `config_manager.py` | Environment configuration, API keys, settings | `load_config()`, `validate_settings()` |
| `prospect_manager.py` | CSV handling, data validation, prospect loading | `load_prospects()`, `validate_csv()` |
| `website_analyzer.py` | Web scraping, technical analysis, performance metrics | `analyze_website()`, `get_tech_stack()` |
| `ai_analyzer.py` | OpenAI integration, opportunity detection, insights | `analyze_opportunities()`, `generate_insights()` |
| `email_generator.py` | Email composition, personalization, content validation | `generate_email()`, `calculate_score()` |
| `email_sender.py` | SMTP handling, email delivery, tracking | `send_email()`, `test_connection()` |
| `main.py` | Application orchestration, workflow management | `PersonalizedEmailAutomation` class |

### Security Considerations

- 🔐 **API Keys**: Stored in `.env` file (never committed to version control)
- 🛡️ **Email Credentials**: Encrypted transmission via TLS/SSL
- 🌐 **Web Requests**: Rate limited and respectful of robots.txt
- 📝 **Logging**: Sensitive data is sanitized in log files
- 🔒 **Data Storage**: Prospect data handled securely, not permanently stored

## Configuration

### OpenAI API Setup

1. **Create OpenAI Account**:
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Sign up for an account
   - Add billing information (required for API access)

2. **Generate API Key**:
   - Navigate to [API Keys](https://platform.openai.com/api-keys)
   - Click "Create new secret key"
   - Copy the key (you won't see it again!)

3. **Add to Environment**:
   ```env
   OPENAI_API_KEY=sk-your-api-key-here
   ```

### Email Configuration (Gmail)

1. **Enable 2-Factor Authentication**:
   - Go to your [Google Account](https://myaccount.google.com/)
   - Security → 2-Step Verification → Turn on

2. **Generate App Password**:
   - Go to Security → 2-Step Verification → App passwords
   - Select "Mail" and generate password
   - Copy the 16-character password

3. **Update Environment File**:
   ```env
   EMAIL_ADDRESS=your.email@gmail.com
   EMAIL_PASSWORD=your-16-character-app-password
   SENDER_NAME=Your Full Name
   ```

### Other Email Providers

<details>
<summary>Click to see configurations for other email providers</summary>

#### Outlook/Hotmail
```env
EMAIL_ADDRESS=your.email@outlook.com
EMAIL_PASSWORD=your-password
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
USE_TLS=true
```

#### Yahoo Mail
```env
EMAIL_ADDRESS=your.email@yahoo.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
USE_TLS=true
```
</details>

### Complete Environment Configuration

Copy `.env.example` to `.env` and configure all variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7

# Email Configuration
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your_app_password_here
SENDER_NAME=Your Full Name
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
USE_TLS=true

# Website Scraping Configuration
REQUEST_TIMEOUT=10
DELAY_BETWEEN_REQUESTS=30
MAX_RETRIES=3
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Logging Configuration
LOG_LEVEL=INFO
```

## CSV Format

Your prospects CSV file should have these exact columns:

| Column | Description | Example |
|--------|-------------|---------|
| Email | Contact email | john@company.com |
| First name | First name | John |
| Last name | Last name | Smith |
| LinkedIn | LinkedIn profile URL | https://linkedin.com/in/johnsmith |
| Job position | Their job title | CTO |
| Country | Country location | United States |
| Company name | Company name | TechCorp |
| Company URL | Company website | techcorp.com |

See `data/sample_prospects.csv` for an example.

## Usage

### Command Line Interface

The tool provides a simple command-line interface with various options:

```bash
# Basic usage - test mode (recommended for first run)
python run.py data/prospects.csv --test-mode

# Test email connection only
python run.py data/prospects.csv --test-email

# Run with custom delay between emails (in seconds)
python run.py data/prospects.csv --delay 60

# Export analysis results to JSON file
python run.py data/prospects.csv --output results.json

# Show prospect statistics without processing
python run.py data/prospects.csv --stats-only

# Process only first N prospects (useful for testing)
python run.py data/prospects.csv --limit 5

# Verbose output for debugging
python run.py data/prospects.csv --verbose
```

### Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--test-mode` | Analyze and generate emails without sending | `--test-mode` |
| `--test-email` | Test email connection only | `--test-email` |
| `--delay <seconds>` | Delay between emails (default: 30) | `--delay 60` |
| `--output <file>` | Export results to JSON file | `--output results.json` |
| `--stats-only` | Show statistics without processing | `--stats-only` |
| `--limit <number>` | Process only first N prospects | `--limit 10` |
| `--verbose` | Enable verbose logging | `--verbose` |

### Programmatic Usage

For integration into other applications:

```python
from src.email_automation.main import PersonalizedEmailAutomation

# Initialize the automation system
automation = PersonalizedEmailAutomation()

# Test email connection
if automation.test_email_connection():
    print("✅ Email connection successful!")
else:
    print("❌ Email connection failed")
    exit(1)

# Load prospects from CSV
success = automation.load_prospects('data/prospects.csv')
if not success:
    print("❌ Failed to load prospects")
    exit(1)

# Process all prospects (test mode)
results = automation.process_all_prospects(test_mode=True)

# Get statistics
stats = automation.get_statistics()
print(f"📊 Success rate: {stats['success_rate']:.1f}%")
print(f"📧 Emails generated: {stats['emails_generated']}")
print(f"⚠️  Errors: {stats['errors']}")

# Export results
automation.export_results('output/campaign_results.json')
```

## How It Works

1. **Load Prospects**: Reads CSV file and validates prospect data with comprehensive error checking
2. **Comprehensive Website Analysis**: Performs multi-layered analysis including:
   - Technology stack detection and modernization opportunities
   - SEO optimization and content strategy gaps
   - User experience and conversion optimization potential
   - Performance bottlenecks and technical improvements
   - Industry-specific functionality assessment
3. **Advanced AI Analysis**: Uses OpenAI to generate diverse insights across:
   - **Technical Infrastructure**: Performance optimization, security, mobile responsiveness
   - **Digital Marketing**: SEO improvements, content strategy, local optimization
   - **Business Process Automation**: Workflow optimization, manual task elimination
   - **User Experience**: Navigation improvements, conversion optimization, accessibility
   - **Data & Analytics**: Tracking implementation, reporting automation, business intelligence
   - **Industry-Specific Solutions**: Tailored recommendations based on business category
4. **Dynamic Email Generation**: Creates highly personalized emails featuring:
   - Specific technical findings from website analysis
   - Industry-relevant improvement opportunities
   - Business-appropriate solution recommendations
   - Professional tone with varied approaches based on opportunity type
5. **Smart Email Delivery**: Sends emails with intelligent rate limiting, delivery tracking, and validation

## Solution Categories 🎯

The system generates diverse, industry-specific recommendations across multiple categories:

### **E-commerce Businesses**
- Cart abandonment recovery systems
- Product recommendation engines
- Inventory management optimization
- Payment security enhancements
- Mobile shopping experience improvements

### **SaaS Companies**
- User onboarding automation
- Feature adoption tracking
- Churn prediction analytics
- API optimization and documentation
- Performance monitoring dashboards

### **Consulting Firms**
- Client portal development
- Knowledge management systems
- Automated proposal generation
- Project tracking solutions
- CRM integration and automation

### **Healthcare Providers**
- Patient appointment management
- HIPAA-compliant communication systems
- Electronic health record integration
- Automated reminder systems
- Telehealth platform optimization

### **Restaurants & Food Service**
- Online ordering systems
- Table reservation platforms
- Inventory tracking automation
- Customer loyalty programs
- Delivery optimization tools

### **And Many More Industries...**
Each business category receives tailored analysis and recommendations specific to their operational needs and market challenges.

## API Documentation

### Core Classes

#### `PersonalizedEmailAutomation`

Main orchestrator class for the email automation system.

```python
class PersonalizedEmailAutomation:
    def __init__(self, config_path: str = None)
    def load_prospects(self, csv_file: str) -> bool
    def test_email_connection(self) -> bool
    def process_all_prospects(self, test_mode: bool = False) -> List[Dict]
    def get_statistics(self) -> Dict[str, Any]
    def export_results(self, output_file: str) -> None
```

#### `WebsiteAnalyzer`

Handles website scraping and technical analysis.

```python
class WebsiteAnalyzer:
    def analyze_website(self, url: str) -> Dict[str, Any]
    def get_technical_stack(self, soup: BeautifulSoup) -> List[str]
    def analyze_seo(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]
    def analyze_performance(self, url: str) -> Dict[str, Any]
```

#### `AIAnalyzer`

AI-powered opportunity detection and insight generation.

```python
class AIAnalyzer:
    def analyze_opportunities(self, website_data: Dict, prospect_info: Dict) -> Dict[str, Any]
    def generate_insights(self, analysis_data: Dict) -> List[Dict[str, Any]]
    def categorize_business(self, website_data: Dict) -> str
```

#### `EmailGenerator`

Email content generation and personalization.

```python
class EmailGenerator:
    def generate_personalized_email(self, prospect: Dict, analysis: Dict) -> Dict[str, str]
    def calculate_personalization_score(self, email_content: str, analysis: Dict) -> float
    def validate_email_content(self, content: str) -> bool
```

### Configuration Options

The system can be configured through environment variables or a configuration file:

```python
# Configuration parameters
OPENAI_MODEL = "gpt-4o-mini"  # AI model to use
OPENAI_MAX_TOKENS = 1000      # Maximum tokens per request
OPENAI_TEMPERATURE = 0.7      # AI creativity level (0.0-1.0)
REQUEST_TIMEOUT = 10          # Website request timeout (seconds)
DELAY_BETWEEN_REQUESTS = 30   # Rate limiting delay (seconds)
MAX_RETRIES = 3              # Maximum retry attempts
LOG_LEVEL = "INFO"           # Logging level
```

### Error Handling

All major functions return result objects with error information:

```python
{
    "success": True,
    "data": {...},
    "error": None,
    "error_type": None
}
```

Common error types:
- `NetworkError`: Website connection issues
- `APIError`: OpenAI API problems
- `ValidationError`: Data validation failures
- `EmailError`: Email sending issues
- Patient appointment management
- HIPAA-compliant communication systems
- Electronic health record integration
- Automated reminder systems
- Telehealth platform optimization

### **Restaurants & Food Service**
- Online ordering systems
- Table reservation platforms
- Inventory tracking automation
- Customer loyalty programs
- Delivery optimization tools

### **And Many More Industries...**
Each business category receives tailored analysis and recommendations specific to their operational needs and market challenges.

## Key Features

### Advanced Website Analysis
- **Technology Stack Assessment**: Comprehensive detection and modernization recommendations
- **Multi-Category Technical Auditing**: Performance, SEO, accessibility, and security analysis
- **Business Category Intelligence**: Automatic industry classification with tailored analysis
- **Gap Identification**: Technical, operational, and competitive gap analysis
- **Performance Benchmarking**: Page speed, mobile responsiveness, and user experience evaluation

### AI-Powered Insight Generation
- **Industry-Specific Opportunity Detection**: Tailored recommendations for 10+ business categories
- **Diverse Solution Categories**: Technical, marketing, automation, UX, analytics, and integration opportunities
- **Competitive Analysis**: Gap identification compared to industry standards
- **ROI Assessment**: Realistic potential return evaluation with implementation complexity analysis
- **Smart Validation**: Prevents generic suggestions and ensures solution diversity

### Dynamic Email Personalization
- **Opportunity Categorization**: Automatically sorts insights into relevant solution types
- **Adaptive Email Focus**: Selects email approach based on strongest opportunity category
- **Industry-Appropriate Messaging**: Tailored communication style for different business types
- **Technical Credibility**: Demonstrates genuine website analysis and technical understanding
- **Personalization Scoring**: Quantitative assessment of email relevance and specificity

### Enhanced Safety Features
- **Intelligent Content Validation**: Prevents repetitive or generic email content
- **Solution Diversity Enforcement**: Ensures varied recommendations across email campaigns
- **Test Mode Capabilities**: Safe testing environment with comprehensive preview options
- **Rate Limiting Intelligence**: Respectful request pacing with website-specific delays
- **Comprehensive Error Handling**: Robust failure recovery and detailed error reporting

## Logging

Logs are stored in the `logs/` directory:
- `email_automation.log`: Complete application logs
- Console output for real-time monitoring

## Troubleshooting

### Common Issues and Solutions

#### 🔐 Email Authentication Errors

**Problem**: `SMTPAuthenticationError` or "Username and Password not accepted"

**Solutions**:
1. **For Gmail users**:
   - Ensure 2-Factor Authentication is enabled
   - Use App Password, not your regular password
   - Generate new App Password if needed
   
2. **For other providers**:
   - Check SMTP settings are correct
   - Verify less secure app access is enabled (if required)
   - Try with regular password first

**Test your email**:
```bash
python run.py data/sample_prospects.csv --test-email
```

#### 🤖 OpenAI API Errors

**Problem**: `OpenAIError` or "API key invalid"

**Solutions**:
1. **Check API key validity**:
   - Verify key is correctly copied (starts with `sk-`)
   - Ensure no extra spaces or characters
   - Check if key has been revoked

2. **Account issues**:
   - Verify you have API credits/billing set up
   - Check usage limits haven't been exceeded
   - Try a smaller batch to test

**Test API connection**:
```python
import openai
openai.api_key = "your-key-here"
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=5
    )
    print("✅ API connection successful")
except Exception as e:
    print(f"❌ API error: {e}")
```

#### 🌐 Website Analysis Issues

**Problem**: Websites fail to load or analysis is incomplete

**Common causes and solutions**:

1. **Website blocks requests**:
   - Some sites have anti-scraping measures
   - Try increasing `DELAY_BETWEEN_REQUESTS` in `.env`
   - Check if the website requires specific headers

2. **Network connectivity**:
   - Test internet connection
   - Try accessing websites manually in browser
   - Check if corporate firewall is blocking requests

3. **Website structure issues**:
   - Some sites use heavy JavaScript (can't be scraped easily)
   - Protected/login-required pages
   - Invalid URLs in CSV

**Test website access**:
```bash
# Test with verbose logging
python run.py data/sample_prospects.csv --test-mode --verbose
```

#### 📁 File and Import Errors

**Problem**: `ModuleNotFoundError` or `FileNotFoundError`

**Solutions**:
1. **Virtual environment issues**:
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

2. **CSV file issues**:
   - Check file path is correct
   - Verify CSV has required columns
   - Check for encoding issues (use UTF-8)

3. **Path issues**:
   - Run commands from project root directory
   - Check that all files are in expected locations

#### 💾 Memory and Performance Issues

**Problem**: Script runs slowly or runs out of memory

**Solutions**:
1. **Process smaller batches**:
   ```bash
   # Process only first 10 prospects
   python run.py data/prospects.csv --limit 10
   ```

2. **Adjust delays**:
   ```bash
   # Increase delay between requests
   python run.py data/prospects.csv --delay 60
   ```

3. **Monitor logs**:
   - Check `logs/email_automation.log` for errors
   - Look for specific error patterns

### Debug Mode

Enable verbose logging for detailed troubleshooting:

```bash
# Enable debug logging
python run.py data/prospects.csv --verbose --test-mode
```

### Log Files

Check these log files for detailed error information:
- `logs/email_automation.log` - Main application logs
- Console output - Real-time status updates

### Getting Help

1. **Check the logs** in `logs/email_automation.log` for detailed error information
2. **Run in test mode** first to identify issues without sending emails
3. **Test components individually** using the test flags
4. **Open an issue** on GitHub with:
   - Error message (sanitized - remove API keys!)
   - Steps to reproduce
   - Your environment (OS, Python version)
   - Relevant log entries

### System Requirements

- **Python**: 3.8 or higher
- **Memory**: At least 512MB available RAM
- **Network**: Stable internet connection
- **Disk Space**: 100MB for logs and temporary files

### Performance Tips

1. **Optimize batch size**: Start with 5-10 prospects for testing
2. **Adjust delays**: Increase delay for better reliability
3. **Monitor API usage**: Track OpenAI token consumption
4. **Clean CSV data**: Remove invalid URLs and duplicates
5. **Use test mode**: Always test before live campaigns

## Limitations

- Respects website robots.txt and implements intelligent rate limiting
- Requires stable internet connection for optimal website analysis
- OpenAI API usage costs apply (typically $0.01-0.05 per email generated)
- Some websites may implement anti-scraping measures
- Analysis quality depends on website content availability and structure
- Email deliverability subject to recipient email provider policies

## Best Practices

1. **Always test first**: Use `--test-mode` to preview generated content before sending real emails
2. **Leverage diversity**: The system automatically generates varied solutions - review different approaches
3. **Respect rate limits**: Use appropriate delays between requests to maintain website relationships
4. **Monitor personalization scores**: Aim for scores above 0.75 for optimal engagement
5. **Validate industry categorization**: Ensure prospects are correctly classified for best results
6. **Review generated insights**: Check that technical recommendations align with actual business needs
7. **Track email performance**: Monitor open rates and responses to refine your approach
8. **Backup results**: Export results for analysis and continuous improvement

## Recent Improvements 🚀

### Enhanced Email Diversity (Latest Update)
- **Fixed Monotonous Content**: Eliminated repetitive "AI chatbot" suggestions
- **Industry-Specific Solutions**: Each business type now receives relevant, tailored recommendations
- **Technical Depth**: Genuine website analysis drives specific, actionable insights
- **Solution Variety**: 6+ solution categories ensure diverse email approaches
- **Smart Validation**: Automatic prevention of generic or repetitive content

### Example Improvements:
- **Before**: Every email suggested "AI chatbot for customer engagement"
- **After**: 
  - E-commerce gets cart abandonment and inventory optimization
  - Restaurants get online ordering and reservation systems
  - Consultants get client portals and automation tools
  - Healthcare gets patient management and compliance solutions

## License

## Contributing

We welcome contributions from the community! Whether you're fixing bugs, adding features, improving documentation, or reporting issues, your help is appreciated.

### Ways to Contribute

- 🐛 **Report Bugs**: Open an issue with detailed reproduction steps
- 💡 **Suggest Features**: Share ideas for new functionality
- 📝 **Improve Documentation**: Help make the project more accessible
- 🔧 **Submit Code**: Fix bugs or implement new features
- 🧪 **Add Tests**: Help improve code reliability
- 🌍 **Translate**: Help make the project multilingual

### Getting Started

1. **Fork the Repository**
   ```bash
   # Click the "Fork" button on GitHub
   git clone https://github.com/yourusername/personalized-email-automation.git
   cd personalized-email-automation
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies including development tools
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   
   # Install pre-commit hooks (if configured)
   pre-commit install
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-new-feature
   # or
   git checkout -b bugfix/fix-critical-issue
   ```

### Development Guidelines

#### Code Style

- Follow **PEP 8** Python style guidelines
- Use **type hints** for function parameters and return values
- Include **comprehensive docstrings** for classes and functions
- Use **meaningful variable and function names**
- Keep functions small and focused (ideally < 50 lines)

#### Code Quality

```python
# Good example
def analyze_website_performance(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Analyze website performance metrics.
    
    Args:
        url: The website URL to analyze
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing performance metrics
        
    Raises:
        NetworkError: If website is unreachable
        ValidationError: If URL is invalid
    """
    if not validators.url(url):
        raise ValidationError(f"Invalid URL: {url}")
    
    # Implementation here
    return {"load_time": 1.2, "size": 1024}
```

#### Testing

- Write **unit tests** for new functionality
- Ensure **existing tests pass** before submitting PR
- Include **integration tests** for complex features
- Test with **different email providers** and **website types**

```bash
# Run tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_website_analyzer.py

# Run with coverage
python -m pytest --cov=src tests/
```

#### Documentation

- Update **README.md** if adding new features
- Include **docstrings** for all public methods
- Add **code examples** for new functionality
- Update **API documentation** section

### Submission Process

1. **Test Your Changes**
   ```bash
   # Run all tests
   python -m pytest
   
   # Test with sample data
   python run.py data/sample_prospects.csv --test-mode
   
   # Check code style
   flake8 src/
   black --check src/
   ```

2. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add website performance analysis
   
   - Add load time measurement
   - Include page size calculation
   - Add error handling for timeouts
   
   Fixes #123"
   ```

3. **Push and Create Pull Request**
   ```bash
   git push origin feature/amazing-new-feature
   ```
   Then open a Pull Request on GitHub with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots (if UI changes)
   - Testing instructions

### Commit Message Format

Use conventional commits for better tracking:

```
type(scope): short description

Longer description if needed

- List of changes
- Another change

Fixes #issue-number
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Pull Request Guidelines

Before submitting a PR, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages are clear and descriptive
- [ ] No secrets or API keys in code
- [ ] Performance impact is considered
- [ ] Backwards compatibility is maintained (or breaking changes are documented)

### Issues and Bug Reports

When reporting bugs, please include:

1. **Environment Information**:
   - Operating System and version
   - Python version
   - Package versions (`pip freeze`)

2. **Reproduction Steps**:
   - Minimal code example
   - Sample data (anonymized)
   - Expected vs actual behavior

3. **Error Information**:
   - Full error message
   - Relevant log entries (sanitized)
   - Stack trace

### Feature Requests

For new features, please:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** and problem being solved
3. **Propose a solution** with examples
4. **Consider backwards compatibility**
5. **Discuss implementation approach**

### Development Priorities

Current areas where contributions are especially welcome:

- 🔧 **Email Provider Support**: Add support for more email services
- 🌐 **Website Analysis**: Improve analysis accuracy and add new metrics
- 🤖 **AI Improvements**: Enhance insight generation and personalization
- 📊 **Analytics**: Add campaign tracking and success metrics
- 🛡️ **Security**: Improve data handling and privacy features
- 🧪 **Testing**: Expand test coverage and add integration tests
- 📚 **Documentation**: Tutorial videos, examples, and guides

### Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/0/code_of_conduct/) Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### What this means:

- ✅ **Commercial use**: You can use this project for commercial purposes
- ✅ **Modification**: You can modify and distribute your changes
- ✅ **Distribution**: You can distribute the original or modified version
- ✅ **Private use**: You can use this project privately
- ❗ **No warranty**: The software is provided "as is" without warranty
- ❗ **Attribution required**: You must include the original license and copyright

## Ethical Usage

### 🚨 Important Legal and Ethical Guidelines

This tool is designed for **legitimate business outreach only**. Users must:

#### Legal Compliance
- **Follow local laws**: Comply with email marketing regulations in your jurisdiction
  - **US**: CAN-SPAM Act requirements
  - **EU**: GDPR and ePrivacy regulations  
  - **Canada**: CASL (Canadian Anti-Spam Legislation)
  - **Australia**: Spam Act 2003
- **Obtain consent**: Ensure you have legal basis for contacting prospects
- **Provide opt-out**: Include unsubscribe options in all emails
- **Be truthful**: Never misrepresent your identity or intentions

#### Website Respect
- **Honor robots.txt**: The tool respects website robots.txt files
- **Rate limiting**: Built-in delays prevent overwhelming target websites
- **Terms of service**: Respect website terms of service and usage policies
- **No harm**: Never use for malicious purposes or harm target websites

#### Email Best Practices
- **Quality over quantity**: Focus on relevant, valuable outreach
- **Personalization**: Use the tool's insights to provide genuine value
- **Professional tone**: Maintain respectful, professional communication
- **Response handling**: Be prepared to handle replies and objections professionally

#### Prohibited Uses

**DO NOT use this tool for:**
- ❌ Spam or mass unsolicited emails
- ❌ Misleading or deceptive practices
- ❌ Harvesting email addresses without permission
- ❌ Violating website terms of service
- ❌ Any illegal activities
- ❌ Harassment or unwanted persistent contact

#### Best Practices

**DO use this tool for:**
- ✅ Legitimate business development
- ✅ Professional service offerings
- ✅ Educational or informational outreach
- ✅ Building genuine business relationships
- ✅ Providing value-focused communications

### Privacy and Data Protection

- **Data minimization**: Only collect necessary prospect information
- **Secure storage**: Protect prospect data and credentials
- **Data retention**: Don't store data longer than necessary
- **Third-party APIs**: Understand data sharing with OpenAI and email providers
- **Consent tracking**: Maintain records of consent where required

### Reporting Issues

If you become aware of misuse of this tool:
1. Report to relevant authorities if illegal activity is suspected
2. Contact project maintainers through GitHub issues
3. Consider whether the issue requires immediate security response

### Disclaimer

The authors and contributors of this project:
- Are not responsible for how users deploy this tool
- Do not endorse any particular use case
- Recommend users seek legal advice for compliance questions
- Expect users to act responsibly and ethically

**By using this software, you agree to use it responsibly and in compliance with all applicable laws and regulations.**

---

## Acknowledgments

- Thanks to all contributors who help improve this project
- OpenAI for providing the GPT API that powers the AI analysis
- The Python community for excellent libraries used in this project
- Early users who provided feedback and bug reports

## Support

- 📖 **Documentation**: Read this README thoroughly
- 🐛 **Bug Reports**: Open an issue on GitHub
- 💡 **Feature Requests**: Discuss in GitHub issues
- 💬 **Questions**: Use GitHub Discussions
- 📧 **Security Issues**: Email maintainers directly

---

**Made with ❤️ for the open source community**
