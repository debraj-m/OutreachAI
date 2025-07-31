"""
Website Analyzer Module
======================

Analyzes websites to extract information and identify potential tech/AI opportunities.
Performs web scraping, content analysis, and technical assessment.
"""

import requests
from bs4 import BeautifulSoup, Comment
import logging
from typing import Dict, List, Optional, Any, Set
from urllib.parse import urljoin, urlparse
import re
import time
from dataclasses import dataclass


@dataclass
class WebsiteAnalysis:
    """Data class for website analysis results"""
    url: str
    title: str = ""
    meta_description: str = ""
    headings: List[str] = None
    tech_stack: List[str] = None
    content_text: str = ""
    page_load_time: float = 0.0
    
    # Technical findings
    has_contact_form: bool = False
    has_chatbot: bool = False
    has_blog: bool = False
    has_ecommerce: bool = False
    mobile_responsive: bool = False
    
    # SEO and technical issues
    seo_issues: List[str] = None
    accessibility_issues: List[str] = None
    performance_issues: List[str] = None
    
    # Business insights
    business_category: str = ""
    services_mentioned: List[str] = None
    target_audience: str = ""
    
    # Identified opportunities
    tech_gaps: List[str] = None
    ai_opportunities: List[str] = None
    
    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.headings is None:
            self.headings = []
        if self.tech_stack is None:
            self.tech_stack = []
        if self.seo_issues is None:
            self.seo_issues = []
        if self.accessibility_issues is None:
            self.accessibility_issues = []
        if self.performance_issues is None:
            self.performance_issues = []
        if self.services_mentioned is None:
            self.services_mentioned = []
        if self.tech_gaps is None:
            self.tech_gaps = []
        if self.ai_opportunities is None:
            self.ai_opportunities = []


class WebsiteAnalyzer:
    """Analyzes websites for technical assessment and opportunity identification"""
    
    def __init__(self, request_timeout: int = 10, user_agent: str = None, logger: Optional[logging.Logger] = None):
        """
        Initialize WebsiteAnalyzer
        
        Args:
            request_timeout: Request timeout in seconds
            user_agent: User agent string for requests
            logger: Logger instance
        """
        self.request_timeout = request_timeout
        self.user_agent = user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.logger = logger or logging.getLogger(__name__)
        
        # Define patterns for analysis
        self.tech_patterns = {
            'React': ['react', 'reactjs', 'react.js'],
            'Angular': ['angular', 'angularjs'],
            'Vue.js': ['vue', 'vuejs', 'vue.js'],
            'jQuery': ['jquery'],
            'Bootstrap': ['bootstrap'],
            'WordPress': ['wp-content', 'wordpress'],
            'Shopify': ['shopify', 'myshopify'],
            'Wix': ['wix.com', 'wixstatic'],
            'Squarespace': ['squarespace'],
            'Google Analytics': ['google-analytics', 'gtag'],
            'Facebook Pixel': ['facebook.net/tr'],
            'Stripe': ['stripe', 'js.stripe.com'],
            'PayPal': ['paypal'],
            'Intercom': ['intercom'],
            'Zendesk': ['zendesk'],
            'HubSpot': ['hubspot'],
            'Salesforce': ['salesforce']
        }
        
        self.business_keywords = {
            'ecommerce': ['shop', 'store', 'buy', 'cart', 'checkout', 'product', 'price', 'order'],
            'saas': ['software', 'platform', 'api', 'dashboard', 'subscription', 'cloud'],
            'consulting': ['consulting', 'advisory', 'strategy', 'expert', 'professional'],
            'agency': ['agency', 'marketing', 'design', 'creative', 'branding'],
            'healthcare': ['health', 'medical', 'doctor', 'clinic', 'patient'],
            'finance': ['finance', 'investment', 'banking', 'loan', 'insurance'],
            'education': ['education', 'training', 'course', 'learning', 'school'],
            'real_estate': ['real estate', 'property', 'homes', 'rent', 'lease'],
            'restaurant': ['restaurant', 'food', 'menu', 'delivery', 'catering'],
            'tech': ['technology', 'software', 'development', 'ai', 'machine learning']
        }
    
    def analyze_website(self, url: str) -> Optional[WebsiteAnalysis]:
        """
        Perform comprehensive website analysis
        
        Args:
            url: Website URL to analyze
            
        Returns:
            WebsiteAnalysis object or None if analysis failed
        """
        try:
            # Clean and validate URL
            clean_url = self._clean_url(url)
            if not clean_url:
                self.logger.error(f"Invalid URL: {url}")
                return None
            
            self.logger.info(f"Analyzing website: {clean_url}")
            
            # Perform HTTP request
            start_time = time.time()
            response = self._make_request(clean_url)
            load_time = time.time() - start_time
            
            if not response:
                return None
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Create analysis object
            analysis = WebsiteAnalysis(url=clean_url, page_load_time=load_time)
            
            # Perform various analyses
            self._extract_basic_info(soup, analysis)
            self._analyze_tech_stack(soup, response.text, analysis)
            self._analyze_seo(soup, analysis)
            self._analyze_accessibility(soup, analysis)
            self._analyze_business_category(soup, analysis)
            self._identify_features(soup, analysis)
            self._identify_opportunities(analysis)
            
            self.logger.info(f"Analysis completed for {clean_url}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing website {url}: {e}")
            return None
    
    def _clean_url(self, url: str) -> str:
        """Clean and validate URL"""
        url = url.strip()
        if not url:
            return ""
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove trailing slash and fragments
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with proper headers"""
        try:
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(
                url, 
                headers=headers, 
                timeout=self.request_timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            return None
    
    def _extract_basic_info(self, soup: BeautifulSoup, analysis: WebsiteAnalysis):
        """Extract basic website information"""
        # Title
        title_tag = soup.find('title')
        if title_tag:
            analysis.title = title_tag.get_text().strip()
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            analysis.meta_description = meta_desc.get('content', '').strip()
        
        # Headings
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            text = heading.get_text().strip()
            if text and len(text) < 200:  # Reasonable heading length
                analysis.headings.append(text)
        
        # Content text (first 2000 characters)
        for script in soup(["script", "style", "meta", "link"]):
            script.decompose()
        
        text = soup.get_text()
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        analysis.content_text = ' '.join(chunk for chunk in chunks if chunk)[:2000]
    
    def _analyze_tech_stack(self, soup: BeautifulSoup, page_source: str, analysis: WebsiteAnalysis):
        """Analyze website technology stack"""
        page_source_lower = page_source.lower()
        
        for tech, patterns in self.tech_patterns.items():
            for pattern in patterns:
                if pattern in page_source_lower:
                    if tech not in analysis.tech_stack:
                        analysis.tech_stack.append(tech)
                    break
        
        # Check for specific script sources
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script.get('src', '').lower()
            
            if 'react' in src:
                if 'React' not in analysis.tech_stack:
                    analysis.tech_stack.append('React')
            elif 'angular' in src:
                if 'Angular' not in analysis.tech_stack:
                    analysis.tech_stack.append('Angular')
            elif 'vue' in src:
                if 'Vue.js' not in analysis.tech_stack:
                    analysis.tech_stack.append('Vue.js')
        
        # Check viewport for mobile responsiveness
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        analysis.mobile_responsive = viewport_meta is not None
    
    def _analyze_seo(self, soup: BeautifulSoup, analysis: WebsiteAnalysis):
        """Analyze SEO aspects"""
        # Missing title
        if not analysis.title:
            analysis.seo_issues.append("Missing title tag")
        elif len(analysis.title) < 30 or len(analysis.title) > 60:
            analysis.seo_issues.append("Title tag length not optimal (30-60 chars)")
        
        # Missing meta description
        if not analysis.meta_description:
            analysis.seo_issues.append("Missing meta description")
        elif len(analysis.meta_description) < 120 or len(analysis.meta_description) > 160:
            analysis.seo_issues.append("Meta description length not optimal (120-160 chars)")
        
        # Missing H1
        h1_tags = soup.find_all('h1')
        if not h1_tags:
            analysis.seo_issues.append("Missing H1 tag")
        elif len(h1_tags) > 1:
            analysis.seo_issues.append("Multiple H1 tags found")
        
        # Check for alt text on images
        images = soup.find_all('img')
        images_without_alt = [img for img in images if not img.get('alt')]
        if images_without_alt:
            analysis.seo_issues.append(f"{len(images_without_alt)} images missing alt text")
    
    def _analyze_accessibility(self, soup: BeautifulSoup, analysis: WebsiteAnalysis):
        """Analyze accessibility issues"""
        # Check for skip links
        skip_links = soup.find_all('a', href=re.compile(r'^#'))
        if not skip_links:
            analysis.accessibility_issues.append("No skip navigation links found")
        
        # Check for form labels
        forms = soup.find_all('form')
        for form in forms:
            inputs = form.find_all(['input', 'textarea', 'select'])
            for input_elem in inputs:
                if input_elem.get('type') not in ['hidden', 'submit', 'button']:
                    if not input_elem.get('aria-label') and not input_elem.get('id'):
                        analysis.accessibility_issues.append("Form inputs without proper labels")
                        break
    
    def _analyze_business_category(self, soup: BeautifulSoup, analysis: WebsiteAnalysis):
        """Determine business category and services"""
        content_lower = analysis.content_text.lower()
        
        # Determine primary business category
        category_scores = {}
        for category, keywords in self.business_keywords.items():
            score = sum(content_lower.count(keyword) for keyword in keywords)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            analysis.business_category = max(category_scores, key=category_scores.get)
        
        # Extract services mentioned
        service_patterns = [
            r'we (offer|provide|deliver|specialize in)',
            r'our (services|solutions|products)',
            r'(consulting|development|design|marketing|support)'
        ]
        
        for pattern in service_patterns:
            matches = re.findall(pattern, content_lower)
            analysis.services_mentioned.extend(matches)
    
    def _identify_features(self, soup: BeautifulSoup, analysis: WebsiteAnalysis):
        """Identify website features"""
        # Contact form
        if soup.find('form') and (soup.find('input', {'type': 'email'}) or 
                                 soup.find('input', {'name': re.compile(r'email', re.I)})):
            analysis.has_contact_form = True
        
        # Chatbot indicators
        chatbot_indicators = ['chat', 'support', 'help', 'intercom', 'zendesk', 'livechat']
        page_text_lower = soup.get_text().lower()
        if any(indicator in page_text_lower for indicator in chatbot_indicators):
            # Check for chat widgets
            chat_elements = soup.find_all(['div', 'iframe'], class_=re.compile(r'chat|support', re.I))
            if chat_elements:
                analysis.has_chatbot = True
        
        # Blog
        blog_indicators = ['blog', 'news', 'articles', 'posts']
        if any(indicator in analysis.content_text.lower() for indicator in blog_indicators):
            analysis.has_blog = True
        
        # E-commerce
        ecommerce_indicators = ['add to cart', 'buy now', 'checkout', 'shopping cart', 'product']
        if any(indicator in analysis.content_text.lower() for indicator in ecommerce_indicators):
            analysis.has_ecommerce = True
    
    def _identify_opportunities(self, analysis: WebsiteAnalysis):
        """Identify potential tech and AI opportunities"""
        # Tech gaps based on missing features
        if not analysis.has_chatbot:
            analysis.tech_gaps.append("No chatbot for customer support")
            analysis.ai_opportunities.append("AI-powered customer support chatbot")
        
        if not analysis.mobile_responsive:
            analysis.tech_gaps.append("Website not mobile responsive")
        
        if analysis.page_load_time > 3.0:
            analysis.tech_gaps.append("Slow page loading speed")
            analysis.performance_issues.append(f"Page load time: {analysis.page_load_time:.2f}s")
        
        if analysis.seo_issues:
            analysis.tech_gaps.append("SEO optimization needed")
        
        # AI opportunities based on business category
        if analysis.business_category == 'ecommerce':
            analysis.ai_opportunities.extend([
                "Product recommendation system",
                "Inventory demand forecasting",
                "Price optimization AI"
            ])
        elif analysis.business_category == 'consulting':
            analysis.ai_opportunities.extend([
                "Automated lead qualification",
                "Content generation for thought leadership",
                "Client communication automation"
            ])
        elif analysis.business_category == 'agency':
            analysis.ai_opportunities.extend([
                "Automated social media content creation",
                "Client reporting automation",
                "Design asset generation"
            ])
        
        # General AI opportunities
        if not any('automation' in service.lower() for service in analysis.services_mentioned):
            analysis.ai_opportunities.append("Process automation opportunities")
        
        if analysis.has_contact_form and not analysis.has_chatbot:
            analysis.ai_opportunities.append("Lead qualification automation")
    
    def get_analysis_summary(self, analysis: WebsiteAnalysis) -> Dict[str, Any]:
        """Get a summary of the analysis results"""
        return {
            'url': analysis.url,
            'title': analysis.title,
            'business_category': analysis.business_category,
            'tech_stack_count': len(analysis.tech_stack),
            'seo_issues_count': len(analysis.seo_issues),
            'tech_gaps_count': len(analysis.tech_gaps),
            'ai_opportunities_count': len(analysis.ai_opportunities),
            'mobile_responsive': analysis.mobile_responsive,
            'has_chatbot': analysis.has_chatbot,
            'page_load_time': analysis.page_load_time,
            'top_opportunities': analysis.ai_opportunities[:3]
        }
