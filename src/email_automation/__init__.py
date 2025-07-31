"""
Personalized Email Automation Package
=====================================

A modular email automation tool for freelancers to send personalized outreach emails
based on website analysis and AI-powered opportunity detection.

Modules:
    - prospect_manager: Handle CSV prospect data management
    - website_analyzer: Analyze websites for tech/AI opportunities
    - ai_analyzer: AI-powered opportunity identification
    - email_generator: Generate personalized email content
    - email_sender: Handle email delivery
    - config_manager: Configuration and settings management
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .prospect_manager import ProspectManager
from .website_analyzer import WebsiteAnalyzer
from .ai_analyzer import AIAnalyzer
from .email_generator import EmailGenerator
from .email_sender import EmailSender
from .config_manager import ConfigManager

__all__ = [
    'ProspectManager',
    'WebsiteAnalyzer', 
    'AIAnalyzer',
    'EmailGenerator',
    'EmailSender',
    'ConfigManager'
]
