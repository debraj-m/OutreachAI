<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Personalized Email Automation Project Instructions

This is a modular Python project for automated personalized email outreach based on website analysis and AI insights.

## Project Context
- Target users: Freelancers in tech/AI looking for clients
- Purpose: Analyze prospect websites and send personalized outreach emails
- Architecture: Modular design with clear separation of concerns

## Code Style Guidelines
- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and return values
- Include comprehensive docstrings for classes and functions
- Use dataclasses for structured data
- Implement proper error handling with logging
- Follow the existing modular structure

## Key Modules
- `config_manager.py`: Handles all configuration and environment variables
- `prospect_manager.py`: CSV data loading and prospect management
- `website_analyzer.py`: Website scraping and technical analysis
- `ai_analyzer.py`: OpenAI-powered opportunity identification
- `email_generator.py`: Personalized email content generation
- `email_sender.py`: Email delivery and tracking
- `main.py`: Application orchestrator

## When adding new features:
1. Maintain the modular architecture
2. Add proper logging for debugging
3. Include error handling and validation
4. Update type hints and docstrings
5. Consider rate limiting for external API calls
6. Add appropriate configuration options

## Testing Guidelines
- Use test mode functionality for safe testing
- Validate email connections before sending
- Test with small prospect lists first
- Monitor logs for errors and performance

## Important Notes
- Always respect website robots.txt and terms of service
- Implement appropriate delays between requests
- Use OpenAI API responsibly with proper error handling
- Follow email marketing regulations and best practices
