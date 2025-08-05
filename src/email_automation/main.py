"""
Main Application Module
======================

Main orchestrator for the personalized email automation system.
Coordinates all modules to analyze websites and send personalized emails.
"""

import logging
import time
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from .config_manager import ConfigManager
from .prospect_manager import ProspectManager, Prospect
from .website_analyzer import WebsiteAnalyzer
from .ai_analyzer import AIAnalyzer
from .email_generator import EmailGenerator
from .email_sender import EmailSender, EmailBatch, EmailConfig


class PersonalizedEmailAutomation:
    """Main application class for email automation"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the email automation system
        
        Args:
            config_file: Path to configuration file (optional)
        """
        # Initialize configuration
        self.config_manager = ConfigManager(config_file)
        self.logger = self.config_manager.get_logger()
        
        # Validate configuration
        if not self.config_manager.validate_config():
            raise ValueError("Configuration validation failed")
        
        # Initialize modules
        self._initialize_modules()
        
        # Processing state
        self.prospects: List[Prospect] = []
        self.results: List[Dict[str, Any]] = []
        
        self.logger.info("Personalized Email Automation initialized successfully")
    
    def _initialize_modules(self):
        """Initialize all automation modules"""
        try:
            # Get configurations
            email_config = self.config_manager.get_email_config()
            ai_config = self.config_manager.get_ai_config()
            scraping_config = self.config_manager.get_scraping_config()
            
            # Initialize modules
            self.prospect_manager = ProspectManager(self.logger)
            
            self.website_analyzer = WebsiteAnalyzer(
                request_timeout=scraping_config.request_timeout,
                user_agent=scraping_config.user_agent,
                logger=self.logger
            )
            
            self.ai_analyzer = AIAnalyzer(
                api_key=ai_config.openai_api_key,
                model=ai_config.model,
                max_tokens=ai_config.max_tokens,
                temperature=ai_config.temperature,
                logger=self.logger
            )
            
            self.email_generator = EmailGenerator(
                api_key=ai_config.openai_api_key,
                model=ai_config.model,
                max_tokens=800,  # Specific for email generation
                temperature=0.8,  # Higher creativity for emails
                config=self.config_manager,
                logger=self.logger
            )
            
            # Convert email config to EmailConfig dataclass
            smtp_config = EmailConfig(
                smtp_server=email_config.smtp_server,
                smtp_port=email_config.smtp_port,
                email_address=email_config.email_address,
                password=email_config.email_password,
                use_tls=email_config.use_tls
            )
            
            self.email_sender = EmailSender(smtp_config, self.logger)
            
            self.logger.info("All modules initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize modules: {e}")
            raise
    
    def load_prospects(self, csv_file_path: str) -> bool:
        """
        Load prospects from CSV file
        
        Args:
            csv_file_path: Path to CSV file containing prospect data
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            success = self.prospect_manager.load_from_csv(csv_file_path)
            
            if success:
                self.prospects = self.prospect_manager.get_prospects()
                stats = self.prospect_manager.get_stats()
                
                self.logger.info(f"Loaded {stats['total_prospects']} prospects")
                self.logger.info(f"Success rate: {stats['validation_success_rate']:.1f}%")
                
                if stats['invalid_prospects'] > 0:
                    self.logger.warning(f"Found {stats['invalid_prospects']} invalid prospects")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error loading prospects: {e}")
            return False
    
    def test_email_connection(self) -> bool:
        """Test email connection before starting automation"""
        try:
            success, message = self.email_sender.test_connection()
            
            if success:
                self.logger.info("Email connection test successful")
            else:
                self.logger.error(f"Email connection test failed: {message}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error testing email connection: {e}")
            return False
    
    def process_single_prospect(self, prospect: Prospect, test_mode: bool = False) -> Dict[str, Any]:
        """
        Process a single prospect through the complete pipeline
        
        Args:
            prospect: Prospect to process
            test_mode: If True, don't send actual emails
            
        Returns:
            Dictionary containing processing results
        """
        result = {
            'prospect': prospect.to_dict(),
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'steps_completed': [],
            'errors': []
        }
        
        try:
            self.logger.info(f"Processing {prospect.first_name} {prospect.last_name} at {prospect.company_name}")
            
            # Step 1: Analyze website
            self.logger.info(f"Analyzing website: {prospect.company_url}")
            website_analysis = self.website_analyzer.analyze_website(prospect.company_url)
            
            if not website_analysis:
                result['errors'].append("Website analysis failed")
                return result
            
            result['steps_completed'].append('website_analysis')
            result['website_analysis'] = self.website_analyzer.get_analysis_summary(website_analysis)
            
            # Step 2: Generate AI insights
            self.logger.info("Generating AI insights...")
            ai_insights = None
            max_retries = 2
            
            for attempt in range(max_retries):
                ai_insights = self.ai_analyzer.analyze_opportunities(website_analysis, prospect)
                
                if ai_insights and self.ai_analyzer.validate_insights(ai_insights):
                    break
                elif attempt < max_retries - 1:
                    self.logger.warning(f"AI insights validation failed, retrying (attempt {attempt + 1}/{max_retries})")
                    # Increase temperature slightly for more diverse results
                    original_temp = self.ai_analyzer.temperature
                    self.ai_analyzer.temperature = min(original_temp + 0.2, 1.0)
                else:
                    self.logger.error("AI insights generation failed after all retries")
                    # Reset temperature
                    self.ai_analyzer.temperature = original_temp if 'original_temp' in locals() else 0.7
            
            if not ai_insights:
                result['errors'].append("AI insights generation failed or invalid")
                return result
            
            # Reset temperature if it was modified
            if 'original_temp' in locals():
                self.ai_analyzer.temperature = original_temp
            
            result['steps_completed'].append('ai_analysis')
            result['ai_insights'] = self.ai_analyzer.get_insights_summary(ai_insights)
            
            # Step 3: Generate personalization data
            try:
                self.logger.info("Generating personalization data...")
                personalization_data = self.ai_analyzer.generate_personalization_data(ai_insights, prospect)
                result['personalization_data'] = personalization_data
            except Exception as e:
                self.logger.error(f"Error generating personalization data: {e}")
                result['errors'].append(f"Personalization data generation failed: {e}")
                return result
            
            # Step 4: Generate email content
            try:
                self.logger.info("Generating personalized email...")
                email_content = self.email_generator.generate_email(
                    prospect, ai_insights, personalization_data, tone="professional"
                )
                
                if not email_content:
                    result['errors'].append("Email generation failed")
                    return result
            except Exception as e:
                self.logger.error(f"Error generating email: {e}")
                result['errors'].append(f"Email generation failed: {e}")
                return result
            
            result['steps_completed'].append('email_generation')
            result['email_content'] = {
                'subject': email_content.subject_line,
                'body_preview': email_content.get_preview(150),
                'personalization_score': email_content.personalization_score,
                'word_count': len(email_content.email_body.split())
            }
            
            # Step 5: Validate email content
            validation = self.email_generator.validate_email_content(email_content)
            result['email_validation'] = validation
            
            if not validation['is_valid']:
                self.logger.warning(f"Email validation issues: {validation['issues']}")
            
            # Step 6: Send email (if not in test mode)
            if not test_mode:
                self.logger.info(f"Sending email to {prospect.email}")
                delivery_result = self.email_sender.send_email(
                    recipient_email=prospect.email,
                    subject=email_content.subject_line,
                    body=email_content.email_body,
                    sender_name="Debraj Mukherjee"
                )
                
                result['steps_completed'].append('email_sent')
                result['delivery_result'] = delivery_result.to_dict()
                result['success'] = delivery_result.success
                
                if not delivery_result.success:
                    result['errors'].append(f"Email delivery failed: {delivery_result.error_message}")
            else:
                result['steps_completed'].append('test_mode_complete')
                result['success'] = True
                self.logger.info("TEST MODE: Email would have been sent")
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing prospect: {e}"
            self.logger.error(error_msg)
            result['errors'].append(error_msg)
            return result
    
    def process_all_prospects(self, test_mode: bool = False, 
                            delay_between_prospects: int = None) -> List[Dict[str, Any]]:
        """
        Process all loaded prospects
        
        Args:
            test_mode: If True, don't send actual emails
            delay_between_prospects: Delay in seconds between processing prospects
            
        Returns:
            List of processing results
        """
        if not self.prospects:
            self.logger.error("No prospects loaded")
            return []
        
        # Use configured delay if not specified
        if delay_between_prospects is None:
            delay_between_prospects = self.config_manager.get_scraping_config().delay_between_requests
        
        self.logger.info(f"Starting to process {len(self.prospects)} prospects")
        if test_mode:
            self.logger.info("Running in TEST MODE - no emails will be sent")
        
        self.results = []
        
        for i, prospect in enumerate(self.prospects):
            try:
                # Process single prospect
                result = self.process_single_prospect(prospect, test_mode)
                self.results.append(result)
                
                # Debug logging to prevent race conditions
                if result['success']:
                    self.logger.info(f"Successfully processed {prospect.first_name} {prospect.last_name}")
                else:
                    self.logger.warning(f"Failed to process {prospect.first_name} {prospect.last_name}: {result.get('errors', [])}")
                
                # Log progress
                success_count = sum(1 for r in self.results if r['success'])
                self.logger.info(f"Progress: {i+1}/{len(self.prospects)} - Success rate: {success_count}/{i+1}")
                
                # Delay between prospects (except for last one)
                if i < len(self.prospects) - 1:
                    self.logger.info(f"Waiting {delay_between_prospects} seconds before next prospect...")
                    time.sleep(delay_between_prospects)
                
            except Exception as e:
                import traceback
                self.logger.error(f"Error processing prospect {i+1}: {e}")
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                # Add a failed result
                failed_result = {
                    'prospect': prospect.to_dict(),
                    'timestamp': datetime.now().isoformat(),
                    'success': False,
                    'steps_completed': [],
                    'errors': [f"Exception: {e}"]
                }
                self.results.append(failed_result)
                continue
        
        # Log final statistics
        self._log_final_statistics()
        
        return self.results
    
    def _log_final_statistics(self):
        """Log final processing statistics"""
        if not self.results:
            return
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r['success'])
        failed = total - successful
        
        # Count step completions
        step_counts = {}
        for result in self.results:
            for step in result.get('steps_completed', []):
                step_counts[step] = step_counts.get(step, 0) + 1
        
        self.logger.info("=== FINAL STATISTICS ===")
        self.logger.info(f"Total prospects processed: {total}")
        self.logger.info(f"Successful: {successful} ({successful/total*100:.1f}%)")
        self.logger.info(f"Failed: {failed} ({failed/total*100:.1f}%)")
        
        self.logger.info("Step completion rates:")
        for step, count in step_counts.items():
            self.logger.info(f"  {step}: {count}/{total} ({count/total*100:.1f}%)")
        
        # Email delivery stats if emails were sent
        if hasattr(self.email_sender, 'delivery_results') and self.email_sender.delivery_results:
            delivery_stats = self.email_sender.get_delivery_stats()
            self.logger.info(f"Email delivery success rate: {delivery_stats['success_rate']:.1f}%")
            self.logger.info(f"Average delivery time: {delivery_stats['average_delivery_time_ms']:.0f}ms")
    
    def export_results(self, output_file: str) -> bool:
        """
        Export processing results to JSON file
        
        Args:
            output_file: Path to output JSON file
            
        Returns:
            bool: True if exported successfully
        """
        try:
            import json
            
            export_data = {
                'metadata': {
                    'export_timestamp': datetime.now().isoformat(),
                    'total_prospects': len(self.prospects),
                    'total_results': len(self.results),
                    'success_rate': sum(1 for r in self.results if r['success']) / len(self.results) * 100 if self.results else 0
                },
                'results': self.results
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Results exported to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export results: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        if not self.results:
            return {'message': 'No results available'}
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r['success'])
        
        # Average personalization scores
        personalization_scores = [
            r.get('email_content', {}).get('personalization_score', 0) 
            for r in self.results if r.get('email_content')
        ]
        avg_personalization = sum(personalization_scores) / len(personalization_scores) if personalization_scores else 0
        
        # Common errors
        all_errors = []
        for result in self.results:
            all_errors.extend(result.get('errors', []))
        
        from collections import Counter
        error_counts = Counter(all_errors)
        
        return {
            'total_prospects': total,
            'successful_processing': successful,
            'success_rate': successful / total * 100,
            'average_personalization_score': avg_personalization,
            'email_delivery_stats': self.email_sender.get_delivery_stats(),
            'common_errors': dict(error_counts.most_common(5)),
            'processing_timestamp': datetime.now().isoformat()
        }
