"""
Email Sender Module
==================

Handles email delivery, SMTP configuration, and email tracking.
Supports various email providers and includes delivery validation.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import ssl
from datetime import datetime
import os
import csv


@dataclass
class EmailDeliveryResult:
    """Data class for email delivery results"""
    success: bool
    recipient_email: str
    subject: str
    timestamp: datetime
    error_message: Optional[str] = None
    smtp_response: Optional[str] = None
    delivery_time_ms: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage"""
        return {
            'success': self.success,
            'recipient_email': self.recipient_email,
            'subject': self.subject,
            'timestamp': self.timestamp.isoformat(),
            'error_message': self.error_message,
            'smtp_response': self.smtp_response,
            'delivery_time_ms': self.delivery_time_ms
        }


@dataclass
class EmailConfig:
    """Email configuration settings"""
    smtp_server: str
    smtp_port: int
    email_address: str
    password: str
    use_tls: bool = True
    use_ssl: bool = False
    timeout: int = 30


@dataclass
class EmailBatch:
    """Batch email sending configuration"""
    emails: List[Dict[str, Any]] = field(default_factory=list)
    delay_between_emails: int = 30  # seconds
    max_retries: int = 3
    batch_size: int = 50
    
    def add_email(self, recipient: str, subject: str, body: str, **kwargs):
        """Add email to batch"""
        self.emails.append({
            'recipient': recipient,
            'subject': subject,
            'body': body,
            'metadata': kwargs
        })


class EmailSender:
    """Handles email sending and delivery tracking"""
    
    def __init__(self, email_config: EmailConfig, logger: Optional[logging.Logger] = None):
        """
        Initialize Email Sender
        
        Args:
            email_config: Email configuration
            logger: Logger instance
        """
        self.config = email_config
        self.logger = logger or logging.getLogger(__name__)
        self.delivery_results: List[EmailDeliveryResult] = []
        
        # SMTP provider configurations
        self.smtp_providers = {
            'gmail': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'use_tls': True,
                'instructions': 'Use App Password, not regular password'
            },
            'outlook': {
                'smtp_server': 'smtp-mail.outlook.com',
                'smtp_port': 587,
                'use_tls': True,
                'instructions': 'Enable SMTP auth in Outlook settings'
            },
            'yahoo': {
                'smtp_server': 'smtp.mail.yahoo.com',
                'smtp_port': 587,
                'use_tls': True,
                'instructions': 'Use App Password'
            },
            'custom': {
                'smtp_server': self.config.smtp_server,
                'smtp_port': self.config.smtp_port,
                'use_tls': self.config.use_tls,
                'instructions': 'Custom SMTP configuration'
            }
        }
    
    def send_email(self, recipient_email: str, subject: str, body: str,
                   sender_name: Optional[str] = None, html_body: Optional[str] = None,
                   attachments: Optional[List[str]] = None) -> EmailDeliveryResult:
        """
        Send individual email
        
        Args:
            recipient_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            sender_name: Sender display name
            html_body: HTML version of email body
            attachments: List of file paths to attach
            
        Returns:
            EmailDeliveryResult object
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Sending email to {recipient_email}")
            
            # Create message
            msg = self._create_message(
                recipient_email, subject, body, sender_name, html_body, attachments
            )
            
            # Send via SMTP
            smtp_response = self._send_via_smtp(msg, recipient_email)
            
            delivery_time = (time.time() - start_time) * 1000  # Convert to ms
            
            result = EmailDeliveryResult(
                success=True,
                recipient_email=recipient_email,
                subject=subject,
                timestamp=datetime.now(),
                smtp_response=smtp_response,
                delivery_time_ms=delivery_time
            )
            
            self.delivery_results.append(result)
            self.logger.info(f"Email sent successfully to {recipient_email} in {delivery_time:.0f}ms")
            
            return result
            
        except Exception as e:
            delivery_time = (time.time() - start_time) * 1000
            
            result = EmailDeliveryResult(
                success=False,
                recipient_email=recipient_email,
                subject=subject,
                timestamp=datetime.now(),
                error_message=str(e),
                delivery_time_ms=delivery_time
            )
            
            self.delivery_results.append(result)
            self.logger.error(f"Failed to send email to {recipient_email}: {e}")
            
            return result
    
    def _create_message(self, recipient_email: str, subject: str, body: str,
                       sender_name: Optional[str], html_body: Optional[str],
                       attachments: Optional[List[str]]) -> MIMEMultipart:
        """Create email message"""
        msg = MIMEMultipart('alternative')
        
        # Set headers
        if sender_name:
            msg['From'] = f"{sender_name} <{self.config.email_address}>"
        else:
            msg['From'] = self.config.email_address
        
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        # Add headers to improve deliverability
        msg['Message-ID'] = f"<{int(time.time())}.{hash(recipient_email)}@{self.config.email_address.split('@')[1]}>"
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        msg['X-Mailer'] = 'Personalized Email Automation Tool'
        
        # Add text body
        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # Add HTML body if provided
        if html_body:
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
        
        # Add attachments if provided
        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    self._add_attachment(msg, file_path)
        
        return msg
    
    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """Add file attachment to email"""
        try:
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(file_path)}'
            )
            
            msg.attach(part)
            self.logger.info(f"Added attachment: {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to add attachment {file_path}: {e}")
    
    def _send_via_smtp(self, msg: MIMEMultipart, recipient_email: str) -> str:
        """Send email via SMTP"""
        server = None
        try:
            # Create SMTP connection
            if self.config.use_ssl:
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(
                    self.config.smtp_server, 
                    self.config.smtp_port, 
                    context=context,
                    timeout=self.config.timeout
                )
            else:
                server = smtplib.SMTP(
                    self.config.smtp_server, 
                    self.config.smtp_port,
                    timeout=self.config.timeout
                )
                
                if self.config.use_tls:
                    server.starttls()
            
            # Login
            server.login(self.config.email_address, self.config.password)
            
            # Send email
            response = server.send_message(msg, to_addrs=[recipient_email])
            
            return str(response) if response else "Email sent successfully"
            
        finally:
            if server:
                server.quit()
    
    def send_batch(self, batch: EmailBatch, test_mode: bool = False) -> List[EmailDeliveryResult]:
        """
        Send batch of emails with rate limiting
        
        Args:
            batch: EmailBatch object containing emails to send
            test_mode: If True, don't actually send emails (for testing)
            
        Returns:
            List of EmailDeliveryResult objects
        """
        results = []
        
        self.logger.info(f"Starting batch send of {len(batch.emails)} emails")
        
        for i, email_data in enumerate(batch.emails):
            try:
                if test_mode:
                    # Simulate sending in test mode
                    result = EmailDeliveryResult(
                        success=True,
                        recipient_email=email_data['recipient'],
                        subject=email_data['subject'],
                        timestamp=datetime.now(),
                        smtp_response="TEST MODE - Email not actually sent"
                    )
                    self.logger.info(f"TEST MODE: Would send email to {email_data['recipient']}")
                else:
                    # Actually send email
                    result = self.send_email(
                        recipient_email=email_data['recipient'],
                        subject=email_data['subject'],
                        body=email_data['body']
                    )
                
                results.append(result)
                
                # Rate limiting - delay between emails
                if i < len(batch.emails) - 1:  # Don't delay after last email
                    self.logger.info(f"Waiting {batch.delay_between_emails} seconds before next email...")
                    time.sleep(batch.delay_between_emails)
                
            except Exception as e:
                self.logger.error(f"Error sending email {i+1}/{len(batch.emails)}: {e}")
                
                error_result = EmailDeliveryResult(
                    success=False,
                    recipient_email=email_data['recipient'],
                    subject=email_data['subject'],
                    timestamp=datetime.now(),
                    error_message=str(e)
                )
                results.append(error_result)
        
        self.logger.info(f"Batch send completed. Success rate: {self.get_success_rate(results):.1f}%")
        return results
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test SMTP connection without sending email
        
        Returns:
            Tuple of (success, message)
        """
        try:
            self.logger.info("Testing SMTP connection...")
            
            # Test connection
            if self.config.use_ssl:
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(
                    self.config.smtp_server, 
                    self.config.smtp_port, 
                    context=context,
                    timeout=self.config.timeout
                )
            else:
                server = smtplib.SMTP(
                    self.config.smtp_server, 
                    self.config.smtp_port,
                    timeout=self.config.timeout
                )
                
                if self.config.use_tls:
                    server.starttls()
            
            # Test login
            server.login(self.config.email_address, self.config.password)
            server.quit()
            
            message = "SMTP connection successful"
            self.logger.info(message)
            return True, message
            
        except smtplib.SMTPAuthenticationError:
            message = "SMTP authentication failed. Check email and password."
            self.logger.error(message)
            return False, message
            
        except smtplib.SMTPConnectError:
            message = f"Failed to connect to SMTP server {self.config.smtp_server}:{self.config.smtp_port}"
            self.logger.error(message)
            return False, message
            
        except Exception as e:
            message = f"SMTP connection test failed: {e}"
            self.logger.error(message)
            return False, message
    
    def get_delivery_stats(self) -> Dict[str, Any]:
        """Get delivery statistics"""
        if not self.delivery_results:
            return {'total_emails': 0}
        
        successful = [r for r in self.delivery_results if r.success]
        failed = [r for r in self.delivery_results if not r.success]
        
        # Calculate average delivery time for successful emails
        delivery_times = [r.delivery_time_ms for r in successful if r.delivery_time_ms]
        avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0
        
        return {
            'total_emails': len(self.delivery_results),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / len(self.delivery_results) * 100,
            'average_delivery_time_ms': avg_delivery_time,
            'last_email_sent': max(r.timestamp for r in self.delivery_results) if self.delivery_results else None
        }
    
    def get_success_rate(self, results: List[EmailDeliveryResult]) -> float:
        """Calculate success rate for given results"""
        if not results:
            return 0.0
        
        successful = sum(1 for r in results if r.success)
        return (successful / len(results)) * 100
    
    def export_delivery_log(self, file_path: str) -> bool:
        """
        Export delivery results to CSV file
        
        Args:
            file_path: Output CSV file path
            
        Returns:
            bool: True if exported successfully
        """
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                if not self.delivery_results:
                    csvfile.write("No delivery results to export\n")
                    return True
                
                fieldnames = [
                    'timestamp', 'recipient_email', 'subject', 'success',
                    'error_message', 'delivery_time_ms', 'smtp_response'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in self.delivery_results:
                    writer.writerow({
                        'timestamp': result.timestamp.isoformat(),
                        'recipient_email': result.recipient_email,
                        'subject': result.subject,
                        'success': result.success,
                        'error_message': result.error_message or '',
                        'delivery_time_ms': result.delivery_time_ms or 0,
                        'smtp_response': result.smtp_response or ''
                    })
            
            self.logger.info(f"Delivery log exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export delivery log: {e}")
            return False
    
    def clear_delivery_results(self):
        """Clear stored delivery results"""
        self.delivery_results.clear()
        self.logger.info("Delivery results cleared")
    
    def get_smtp_provider_info(self, provider: str) -> Dict[str, Any]:
        """Get SMTP configuration for common providers"""
        return self.smtp_providers.get(provider.lower(), self.smtp_providers['custom'])
