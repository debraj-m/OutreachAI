"""
Configuration Manager Module
===========================

Handles all configuration settings, environment variables, and API keys
for the email automation system.
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class EmailConfig:
    """Email configuration settings"""
    email_address: str
    email_password: str
    sender_name: str
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    use_tls: bool = True


@dataclass
class AIConfig:
    """AI service configuration"""
    openai_api_key: str
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7


@dataclass
class ScrapingConfig:
    """Website scraping configuration"""
    request_timeout: int = 10
    delay_between_requests: int = 30
    max_retries: int = 3
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class ConfigManager:
    """Manages all application configuration"""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            env_file: Path to .env file (optional)
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        self.email_config = self._load_email_config()
        self.ai_config = self._load_ai_config()
        self.scraping_config = self._load_scraping_config()
        self.logger = self._setup_logging()
    
    def _load_email_config(self) -> EmailConfig:
        """Load email configuration from environment variables"""
        email_address = os.getenv('EMAIL_ADDRESS')
        email_password = os.getenv('EMAIL_PASSWORD')
        sender_name = os.getenv('SENDER_NAME')
        
        if not email_address or not email_password:
            raise ValueError("EMAIL_ADDRESS and EMAIL_PASSWORD must be set in environment variables")
        if not sender_name:
            raise ValueError("SENDER_NAME must be set in environment variables")
        
        return EmailConfig(
            email_address=email_address,
            email_password=email_password,
            sender_name=sender_name,
            smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            smtp_port=int(os.getenv('SMTP_PORT', 587)),
            use_tls=os.getenv('USE_TLS', 'true').lower() == 'true'
        )
    
    def _load_ai_config(self) -> AIConfig:
        """Load AI configuration from environment variables"""
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        
        return AIConfig(
            openai_api_key=api_key,
            model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
            max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', 1000)),
            temperature=float(os.getenv('OPENAI_TEMPERATURE', 0.7))
        )
    
    def _load_scraping_config(self) -> ScrapingConfig:
        """Load web scraping configuration"""
        return ScrapingConfig(
            request_timeout=int(os.getenv('REQUEST_TIMEOUT', 10)),
            delay_between_requests=int(os.getenv('DELAY_BETWEEN_REQUESTS', 30)),
            max_retries=int(os.getenv('MAX_RETRIES', 3)),
            user_agent=os.getenv('USER_AGENT', 
                               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        )
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration"""
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format=log_format,
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'email_automation.log')),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger(__name__)
    
    def get_email_config(self) -> EmailConfig:
        """Get email configuration"""
        return self.email_config
    
    def get_ai_config(self) -> AIConfig:
        """Get AI configuration"""
        return self.ai_config
    
    def get_scraping_config(self) -> ScrapingConfig:
        """Get scraping configuration"""
        return self.scraping_config
    
    def get_logger(self) -> logging.Logger:
        """Get configured logger"""
        return self.logger
    
    def validate_config(self) -> bool:
        """Validate all configurations"""
        try:
            # Test that all required configs are loaded
            self.get_email_config()
            self.get_ai_config()
            self.get_scraping_config()
            
            self.logger.info("Configuration validation successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
