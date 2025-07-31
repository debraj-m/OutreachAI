"""
Prospect Manager Module
======================

Handles loading, validation, and management of prospect data from CSV files.
Supports the specific CSV format with columns: Email, First name, Last name, 
LinkedIn, Job position, Country, Company name, Company URL
"""

import pandas as pd
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import validators
import re


@dataclass
class Prospect:
    """Data class for individual prospect information"""
    email: str
    first_name: str
    last_name: str
    linkedin: str
    job_position: str
    country: str
    company_name: str
    company_url: str
    
    def __post_init__(self):
        """Validate and clean prospect data after initialization"""
        self.email = self.email.strip().lower()
        self.first_name = self.first_name.strip().title()
        self.last_name = self.last_name.strip().title()
        self.company_name = self.company_name.strip()
        self.job_position = self.job_position.strip()
        self.country = self.country.strip()
        
        # Clean and validate company URL
        self.company_url = self._clean_url(self.company_url)
    
    def _clean_url(self, url: str) -> str:
        """Clean and validate URL format"""
        url = url.strip()
        if not url:
            return url
            
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove trailing slash
        url = url.rstrip('/')
        
        return url
    
    def is_valid(self) -> bool:
        """Check if prospect data is valid"""
        # Check required fields
        required_fields = [
            self.email, self.first_name, self.last_name, 
            self.company_name, self.company_url
        ]
        
        if not all(field.strip() for field in required_fields):
            return False
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            return False
        
        # Validate URL format
        if self.company_url and not validators.url(self.company_url):
            return False
        
        return True
    
    def get_full_name(self) -> str:
        """Get full name of prospect"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert prospect to dictionary"""
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'linkedin': self.linkedin,
            'job_position': self.job_position,
            'country': self.country,
            'company_name': self.company_name,
            'company_url': self.company_url
        }


class ProspectManager:
    """Manages prospect data loading, validation, and processing"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize ProspectManager
        
        Args:
            logger: Logger instance (optional)
        """
        self.logger = logger or logging.getLogger(__name__)
        self.prospects: List[Prospect] = []
        self.invalid_prospects: List[Dict[str, Any]] = []
    
    def load_from_csv(self, csv_file_path: str) -> bool:
        """
        Load prospects from CSV file
        
        Args:
            csv_file_path: Path to CSV file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            # Define expected column mappings
            column_mapping = {
                'Email': 'email',
                'First name': 'first_name', 
                'Last name': 'last_name',
                'LinkedIn': 'linkedin',
                'Job position': 'job_position',
                'Country': 'country',
                'Company name': 'company_name',
                'Company URL': 'company_url'
            }
            
            # Load CSV
            df = pd.read_csv(csv_file_path)
            
            # Check if all required columns exist
            missing_columns = set(column_mapping.keys()) - set(df.columns)
            if missing_columns:
                self.logger.error(f"Missing required columns: {missing_columns}")
                return False
            
            # Rename columns to match our internal format
            df = df.rename(columns=column_mapping)
            
            # Convert to Prospect objects
            self.prospects = []
            self.invalid_prospects = []
            
            for index, row in df.iterrows():
                try:
                    # Replace NaN values with empty strings
                    row = row.fillna('')
                    
                    prospect = Prospect(
                        email=str(row['email']),
                        first_name=str(row['first_name']),
                        last_name=str(row['last_name']),
                        linkedin=str(row['linkedin']),
                        job_position=str(row['job_position']),
                        country=str(row['country']),
                        company_name=str(row['company_name']),
                        company_url=str(row['company_url'])
                    )
                    
                    if prospect.is_valid():
                        self.prospects.append(prospect)
                    else:
                        self.invalid_prospects.append({
                            'row_index': index,
                            'data': row.to_dict(),
                            'reason': 'Invalid data format'
                        })
                        
                except Exception as e:
                    self.invalid_prospects.append({
                        'row_index': index,
                        'data': row.to_dict(),
                        'reason': f'Error creating prospect: {e}'
                    })
            
            self.logger.info(f"Loaded {len(self.prospects)} valid prospects")
            
            if self.invalid_prospects:
                self.logger.warning(f"Found {len(self.invalid_prospects)} invalid prospects")
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading CSV file: {e}")
            return False
    
    def get_prospects(self) -> List[Prospect]:
        """Get list of valid prospects"""
        return self.prospects
    
    def get_invalid_prospects(self) -> List[Dict[str, Any]]:
        """Get list of invalid prospects with reasons"""
        return self.invalid_prospects
    
    def get_prospect_count(self) -> int:
        """Get count of valid prospects"""
        return len(self.prospects)
    
    def filter_by_country(self, country: str) -> List[Prospect]:
        """Filter prospects by country"""
        return [p for p in self.prospects if p.country.lower() == country.lower()]
    
    def filter_by_company(self, company_name: str) -> List[Prospect]:
        """Filter prospects by company name"""
        return [p for p in self.prospects 
                if company_name.lower() in p.company_name.lower()]
    
    def export_to_csv(self, output_path: str, include_invalid: bool = False) -> bool:
        """
        Export prospects back to CSV
        
        Args:
            output_path: Output file path
            include_invalid: Whether to include invalid prospects
            
        Returns:
            bool: True if exported successfully
        """
        try:
            # Convert prospects to DataFrame
            data = [prospect.to_dict() for prospect in self.prospects]
            
            if include_invalid and self.invalid_prospects:
                for invalid in self.invalid_prospects:
                    invalid_data = invalid['data'].copy()
                    invalid_data['validation_error'] = invalid['reason']
                    data.append(invalid_data)
            
            df = pd.DataFrame(data)
            
            # Rename columns back to original format
            reverse_mapping = {
                'email': 'Email',
                'first_name': 'First name',
                'last_name': 'Last name', 
                'linkedin': 'LinkedIn',
                'job_position': 'Job position',
                'country': 'Country',
                'company_name': 'Company name',
                'company_url': 'Company URL'
            }
            
            df = df.rename(columns=reverse_mapping)
            df.to_csv(output_path, index=False)
            
            self.logger.info(f"Exported {len(data)} records to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded prospects"""
        if not self.prospects:
            return {'total_prospects': 0}
        
        countries = [p.country for p in self.prospects if p.country]
        companies = [p.company_name for p in self.prospects]
        
        return {
            'total_prospects': len(self.prospects),
            'invalid_prospects': len(self.invalid_prospects),
            'unique_countries': len(set(countries)),
            'unique_companies': len(set(companies)),
            'top_countries': pd.Series(countries).value_counts().head(5).to_dict(),
            'validation_success_rate': len(self.prospects) / (len(self.prospects) + len(self.invalid_prospects)) * 100
        }
