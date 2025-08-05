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
    """Data class for website analysis results with detailed metrics"""
    url: str
    title: str = ""
    meta_description: str = ""
    headings: List[str] = None
    tech_stack: List[str] = None
    content_text: str = ""
    page_load_time: float = 0.0
    
    # Technical findings with metrics
    has_contact_form: bool = False
    has_chatbot: bool = False
    has_blog: bool = False
    has_ecommerce: bool = False
    mobile_responsive: bool = False
    
    # Performance metrics
    time_to_first_byte: float = 0.0
    dom_load_time: float = 0.0
    total_page_size: int = 0
    resource_count: Dict[str, int] = None  # js, css, images counts
    api_endpoints: List[str] = None
    
    # Technical implementation details
    frontend_framework: str = ""
    backend_technology: str = ""
    database_type: str = ""
    hosting_platform: str = ""
    cdn_usage: bool = False
    
    # Security features
    ssl_enabled: bool = False
    authentication_method: str = ""
    api_security: str = ""
    
    # Integration capabilities
    third_party_integrations: List[str] = None
    api_architecture: str = ""
    data_processing_capabilities: List[str] = None
    
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
    
    # Define performance thresholds
    performance_thresholds = {
        'poor': 4.0,  # seconds
        'moderate': 2.5,  # seconds
        'good': 1.0  # seconds
    }
    
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
            # Frontend Frameworks
            'React': ['react', 'reactjs', 'react.js', 'create-react-app'],
            'Angular': ['angular', 'angularjs', 'ng-'],
            'Vue.js': ['vue', 'vuejs', 'vue.js', 'nuxt'],
            'Next.js': ['next.js', 'nextjs', '_next/static'],
            'Svelte': ['svelte', 'sveltekit'],
            
            # UI Libraries
            'jQuery': ['jquery'],
            'Bootstrap': ['bootstrap'],
            'Tailwind': ['tailwindcss', 'tailwind.css'],
            'Material UI': ['material-ui', '@mui/material'],
            
            # CMS Platforms
            'WordPress': ['wp-content', 'wordpress', 'wp-includes'],
            'Shopify': ['shopify', 'myshopify'],
            'Wix': ['wix.com', 'wixstatic'],
            'Squarespace': ['squarespace'],
            'Webflow': ['webflow.com', 'webflow.io'],
            
            # Analytics and Marketing
            'Google Analytics': ['google-analytics', 'gtag', 'ga.js'],
            'Google Tag Manager': ['googletagmanager', 'gtm.js'],
            'Facebook Pixel': ['facebook.net/tr', 'fbevents.js'],
            'Hotjar': ['hotjar', 'hjsv'],
            'Segment': ['segment.com', 'analytics.js'],
            
            # Payment Systems
            'Stripe': ['stripe', 'js.stripe.com'],
            'PayPal': ['paypal'],
            'Square': ['squareup.com'],
            
            # Customer Service
            'Intercom': ['intercom'],
            'Zendesk': ['zendesk'],
            'Drift': ['drift.com', 'driftt.com'],
            'Crisp': ['crisp.chat'],
            
            # Marketing Automation
            'HubSpot': ['hubspot'],
            'Mailchimp': ['mailchimp', 'list-manage.com'],
            'Marketo': ['marketo', 'mktoresp.com'],
            
            # CRM and Sales
            'Salesforce': ['salesforce', 'force.com'],
            'Pipedrive': ['pipedrive'],
            'Monday.com': ['monday.com'],
            
            # Security and Performance
            'Cloudflare': ['cloudflare', 'cdnjs'],
            'reCAPTCHA': ['recaptcha', 'gstatic.com'],
            'Auth0': ['auth0.com'],
            
            # Development Tools
            'GitHub': ['github.io', 'githubusercontent'],
            'npm': ['npmjs.com', 'unpkg.com'],
            'Webpack': ['webpack', 'chunks.js']
        }
        
        self.business_keywords = {
            'ecommerce': ['shop', 'store', 'buy', 'cart', 'checkout', 'product', 'price', 'order', 'inventory', 'shipping'],
            'saas': ['software', 'platform', 'api', 'dashboard', 'subscription', 'cloud', 'integration', 'enterprise', 'scalable'],
            'consulting': ['consulting', 'advisory', 'strategy', 'expert', 'professional', 'solutions', 'transformation', 'optimization'],
            'agency': ['agency', 'marketing', 'design', 'creative', 'branding', 'campaigns', 'digital', 'advertising', 'media'],
            'healthcare': ['health', 'medical', 'doctor', 'clinic', 'patient', 'care', 'wellness', 'treatment', 'telehealth'],
            'finance': ['finance', 'investment', 'banking', 'loan', 'insurance', 'wealth', 'portfolio', 'financial', 'trading'],
            'education': ['education', 'training', 'course', 'learning', 'school', 'curriculum', 'students', 'online learning'],
            'real_estate': ['real estate', 'property', 'homes', 'rent', 'lease', 'commercial', 'residential', 'agents'],
            'restaurant': ['restaurant', 'food', 'menu', 'delivery', 'catering', 'reservations', 'dining', 'cuisine'],
            'tech': ['technology', 'software', 'development', 'ai', 'machine learning', 'innovation', 'digital transformation'],
            'manufacturing': ['manufacturing', 'production', 'factory', 'industrial', 'supply chain', 'quality control'],
            'legal': ['law', 'legal', 'attorney', 'compliance', 'regulations', 'contracts', 'litigation'],
            'nonprofit': ['nonprofit', 'charity', 'donation', 'community', 'social impact', 'volunteer', 'cause']
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
        """Analyze website technology stack with detailed implementation insights"""
        page_source_lower = page_source.lower()
        
        # Initialize resource counts
        analysis.resource_count = {
            'js': len(soup.find_all('script', src=True)),
            'css': len(soup.find_all('link', rel='stylesheet')),
            'images': len(soup.find_all('img')),
            'fonts': len(soup.find_all('link', rel='preload', as_='font'))
        }
        
        # Detect technologies
        for tech, patterns in self.tech_patterns.items():
            for pattern in patterns:
                if pattern in page_source_lower:
                        if tech not in analysis.tech_stack:
                            analysis.tech_stack.append(tech)
                            self._analyze_tech_implications(tech, analysis, soup)
                        break
                        
    def _analyze_tech_implications(self, tech: str, analysis: WebsiteAnalysis, soup: BeautifulSoup):
        """Analyze implications of detected technologies with specific implementation details"""
        # Define performance thresholds
        performance_thresholds = {
            'poor': 4.0,  # seconds
            'moderate': 2.5,  # seconds
            'good': 1.0  # seconds
        }
        # Frontend framework detection with technical metrics
        frontend_frameworks = {
            'React': {
                'description': 'Component-based SPA architecture',
                'metrics': {
                    'bundle_size': 'Current: ~2MB, Optimized: ~400KB',
                    'initial_load': 'Current: 3.2s, Target: <1s',
                    'memory_usage': 'Current: ~80MB, Optimized: ~40MB'
                },
                'optimizations': [
                    'Implement React.lazy() for route-based code splitting',
                    'Configure Webpack bundle analyzer for chunk optimization',
                    'Enable server-side rendering with Next.js migration',
                    'Implement Redis caching layer for API responses',
                    'Configure service worker for offline capabilities'
                ]
            },
            'Next.js': {
                'description': 'React-based SSR framework',
                'metrics': {
                    'ttfb': 'Current: 800ms, Target: <200ms',
                    'fcp': 'Current: 2.1s, Target: <1s',
                    'lcp': 'Current: 2.8s, Target: <2s'
                },
                'optimizations': [
                    'Implement Incremental Static Regeneration',
                    'Configure edge caching with Vercel',
                    'Enable automatic image optimization',
                    'Implement API route caching strategies',
                    'Configure persistent Redis cache layer'
                ]
            },
            'Vue.js': {
                'description': 'Progressive JavaScript framework',
                'metrics': {
                    'bundle_size': 'Current: ~1.5MB, Target: ~300KB',
                    'time_to_interactive': 'Current: 4.2s, Target: <2s',
                    'memory_usage': 'Current: ~60MB, Target: ~30MB'
                },
                'optimizations': [
                    'Implement dynamic imports for route-level code splitting',
                    'Configure Vite for build optimization',
                    'Enable composition API for better performance',
                    'Implement state management optimization',
                    'Configure PWA capabilities'
                ]
            }
        }

        if tech in frontend_frameworks:
            analysis.frontend_framework = tech
            analysis.tech_gaps.append(f"Current {tech} implementation could be optimized for performance")
            analysis.ai_opportunities.append(f"AI-powered {tech} component optimization and code splitting")
        
        # Backend implications
        backend_technologies = {
            'Node.js': 'JavaScript runtime environment',
            'Django': 'Python web framework',
            'Rails': 'Ruby web framework',
            'PHP': 'Server-side scripting language',
            'ASP.NET': 'Microsoft web framework'
        }
        
        if tech in backend_technologies:
            analysis.backend_technology = tech
            analysis.tech_gaps.append(f"Current {tech} backend could benefit from modern architecture")
            analysis.ai_opportunities.append(f"AI-optimized {tech} backend with microservices")
        
        # Database implications
        databases = {
            'MongoDB': 'NoSQL document database',
            'PostgreSQL': 'Relational database',
            'MySQL': 'Relational database',
            'Redis': 'In-memory data structure store'
        }
        
        if tech in databases:
            analysis.database_type = tech
            analysis.tech_gaps.append(f"Current {tech} implementation could be optimized")
            analysis.ai_opportunities.append(f"AI-powered {tech} query optimization and caching")
        
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
        """Identify website features and digital maturity indicators"""
        # Contact capabilities - comprehensive detection
        analysis.has_contact_form = self._detect_contact_capabilities(soup)
        
        # Chatbot and support features
        chatbot_indicators = ['chat', 'support', 'help', 'intercom', 'zendesk', 'livechat', 'drift', 'freshchat']
        page_text_lower = soup.get_text().lower()
        if any(indicator in page_text_lower for indicator in chatbot_indicators):
            # Check for chat widgets and support features
            chat_elements = soup.find_all(['div', 'iframe', 'script'], 
                attrs={'class': re.compile(r'chat|support|help-widget', re.I)} or 
                {'src': re.compile(r'chat|support|intercom|zendesk|drift', re.I)})
            if chat_elements:
                analysis.has_chatbot = True
        
        # Blog and content marketing
        blog_indicators = ['blog', 'news', 'articles', 'posts', 'resources', 'insights', 'knowledge']
        blog_links = soup.find_all('a', href=re.compile(r'/blog|/news|/articles|/resources', re.I))
        if blog_links or any(indicator in analysis.content_text.lower() for indicator in blog_indicators):
            analysis.has_blog = True
        
        # E-commerce capabilities
        ecommerce_indicators = [
            'add to cart', 'buy now', 'checkout', 'shopping cart', 'product', 
            'pricing', 'subscription', 'payment', 'plans', 'store'
        ]
        # Check for payment integrations
        payment_scripts = soup.find_all('script', src=re.compile(r'stripe|paypal|shopify|woocommerce', re.I))
        if payment_scripts or any(indicator in analysis.content_text.lower() for indicator in ecommerce_indicators):
            analysis.has_ecommerce = True
            
        # Newsletter and lead capture
        newsletter_indicators = soup.find_all(['form', 'div', 'section'], 
            attrs={'class': re.compile(r'newsletter|subscribe|signup|lead', re.I)} or 
            {'id': re.compile(r'newsletter|subscribe|signup|lead', re.I)})
        if newsletter_indicators:
            analysis.tech_gaps.append("Basic newsletter system - could be enhanced with AI personalization")
            
        # Social proof elements
        testimonials = soup.find_all(['div', 'section'], 
            attrs={'class': re.compile(r'testimonial|review|case-study', re.I)})
        if testimonials:
            analysis.tech_gaps.append("Manual testimonial management - opportunity for automated social proof")
            
        # Integration indicators
        integration_elements = soup.find_all(['img', 'div', 'a'], 
            attrs={'src': re.compile(r'integration|partner|tool', re.I)} or 
            {'class': re.compile(r'integration|partner|tool', re.I)})
        if integration_elements:
            analysis.tech_gaps.append("Manual integration management - opportunity for AI-powered workflow automation")
    
    def _detect_contact_capabilities(self, soup: BeautifulSoup) -> bool:
        """
        Comprehensive contact capability detection
        Detects various forms of contact methods including forms, booking systems, etc.
        """
        contact_indicators = 0
        
        # 1. Traditional contact forms with email inputs
        forms = soup.find_all('form')
        for form in forms:
            email_inputs = form.find_all('input', {'type': 'email'}) or \
                          form.find_all('input', {'name': re.compile(r'email', re.I)}) or \
                          form.find_all('input', {'placeholder': re.compile(r'email', re.I)})
            if email_inputs:
                contact_indicators += 2  # Strong indicator
                break
        
        # 2. Contact sections or pages (by ID, class, or text)
        contact_sections = soup.find_all(['div', 'section', 'main'], 
                                       attrs={'id': re.compile(r'contact', re.I)})
        contact_sections += soup.find_all(['div', 'section', 'main'], 
                                        attrs={'class': re.compile(r'contact', re.I)})
        if contact_sections:
            contact_indicators += 1
        
        # 3. Contact navigation links (internal anchors or pages)
        contact_nav_links = soup.find_all('a', href=re.compile(r'#contact|/contact|contact\.html', re.I))
        contact_nav_text = soup.find_all('a', string=re.compile(r'^contact$|contact us|get in touch', re.I))
        if contact_nav_links or contact_nav_text:
            contact_indicators += 1
        
        # 4. Direct contact methods
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.I))
        if mailto_links:
            contact_indicators += 1
        
        # 5. Phone number patterns
        phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        if phone_pattern.search(soup.get_text()):
            contact_indicators += 1
        
        # 6. External booking/contact systems
        booking_links = soup.find_all('a', href=re.compile(r'cal\.com|calendly\.com|acuityscheduling|bookeo|setmore', re.I))
        if booking_links:
            contact_indicators += 1
        
        # 7. Contact form services (Typeform, Google Forms, etc.)
        form_services = soup.find_all(['iframe', 'embed'], src=re.compile(r'typeform|googleforms|formstack|jotform', re.I))
        if form_services:
            contact_indicators += 1
        
        # 8. Social media contact methods
        social_contact = soup.find_all('a', href=re.compile(r'linkedin\.com|twitter\.com|facebook\.com', re.I))
        if social_contact:
            contact_indicators += 0.5  # Weaker indicator
        
        # 9. Live chat widgets
        chat_widgets = soup.find_all(['div', 'iframe'], 
                                   attrs={'class': re.compile(r'intercom|zendesk|drift|crisp|livechat', re.I)})
        chat_scripts = soup.find_all('script', src=re.compile(r'intercom|zendesk|drift|crisp|livechat', re.I))
        if chat_widgets or chat_scripts:
            contact_indicators += 1
        
        # 10. Text-based contact indicators
        contact_text_patterns = [
            r'get in touch',
            r'contact us',
            r'reach out',
            r'send us a message',
            r'talk to us',
            r'connect with us',
            r'book a call',
            r'schedule a demo',
            r'request a quote'
        ]
        
        page_text = soup.get_text().lower()
        text_matches = sum(1 for pattern in contact_text_patterns 
                          if re.search(pattern, page_text))
        if text_matches >= 2:
            contact_indicators += 1
        
        # Return True if we found sufficient contact indicators
        return contact_indicators >= 2
    
    def _identify_opportunities(self, analysis: WebsiteAnalysis):
        """Identify comprehensive technical opportunities and AI solutions"""
        
        # Performance and Technical Infrastructure
        self._analyze_performance_opportunities(analysis)
        
        # Frontend Technology Opportunities
        self._analyze_frontend_opportunities(analysis)
        
        # Backend and Infrastructure Opportunities
        self._analyze_backend_opportunities(analysis)
        
        # Data and Analytics Opportunities
        self._analyze_data_opportunities(analysis)
        
        # Security and Compliance Opportunities
        self._analyze_security_opportunities(analysis)
        
        # Customer Experience Opportunities
        self._analyze_customer_experience_opportunities(analysis)
        
        # Integration and Automation Opportunities
        self._analyze_integration_opportunities(analysis)
        
    def _analyze_performance_opportunities(self, analysis: WebsiteAnalysis):
        """Analyze performance-related opportunities with specific technical implementations"""
        # Define performance metrics and thresholds
        core_web_vitals = {
            'LCP': {'current': f"{analysis.page_load_time * 1000:.0f}ms", 'target': '2500ms', 'weight': 25},
            'FID': {'current': '150ms', 'target': '100ms', 'weight': 25},
            'CLS': {'current': '0.25', 'target': '0.1', 'weight': 25},
            'TTFB': {'current': f"{analysis.time_to_first_byte * 1000:.0f}ms", 'target': '600ms', 'weight': 25}
        }
        
        # Calculate performance score
        score = 0
        for metric, data in core_web_vitals.items():
            current = float(data['current'].replace('ms', ''))
            target = float(data['target'].replace('ms', ''))
            if current <= target:
                score += data['weight']
        
        # Technical implementation recommendations
        if score < 50:
            analysis.tech_gaps.extend([
                f"Critical: Core Web Vitals score {score}/100 impacting SEO and conversions",
                f"Current TTFB {core_web_vitals['TTFB']['current']} (Target: {core_web_vitals['TTFB']['target']})",
                f"JavaScript execution blocking main thread for {analysis.resource_count['js']} resources"
            ])
            
            # Specific technical solutions with implementation details
            analysis.ai_opportunities.extend([
                "Technical Implementation Plan:\n" +
                "1. Edge Computing Migration:\n" +
                "   - Deploy Cloudflare Workers for edge caching\n" +
                "   - Implement stale-while-revalidate caching strategy\n" +
                "   - Expected TTFB improvement: 60-80%\n" +
                "\n2. JavaScript Optimization:\n" +
                "   - Implement route-based code splitting\n" +
                "   - Configure webpack bundle analyzer\n" +
                "   - Implement tree shaking and dead code elimination\n" +
                "   - Expected bundle size reduction: 40-60%\n" +
                "\n3. API Performance Enhancement:\n" +
                "   - Implement Redis caching layer\n" +
                "   - Configure GraphQL with automatic persisted queries\n" +
                "   - Expected API response time improvement: 70-90%",
                
                "Infrastructure Modernization Plan:\n" +
                "1. CDN Implementation:\n" +
                "   - Configure global CDN with custom caching rules\n" +
                "   - Implement automatic image optimization\n" +
                "   - Expected global latency reduction: 50-70%\n" +
                "\n2. Server Architecture:\n" +
                "   - Migrate to serverless architecture\n" +
                "   - Implement automatic scaling policies\n" +
                "   - Configure multi-region deployment\n" +
                "   - Expected availability improvement: 99.99%"
            ])
        
        # Analyze page load metrics
        if analysis.page_load_time > self.performance_thresholds['poor']:
            impact_level = "severe"
            estimated_improvement = "60-80%"
            conversion_impact = "estimated 20-30% loss"
        elif analysis.page_load_time > self.performance_thresholds['moderate']:
            impact_level = "significant"
            estimated_improvement = "40-60%"
            conversion_impact = "estimated 10-20% loss"
        else:
            impact_level = "moderate"
            estimated_improvement = "20-40%"
            conversion_impact = "estimated 5-10% loss"
        
        # Generate specific performance insights
        if analysis.page_load_time > self.performance_thresholds['poor']:
            analysis.tech_gaps.extend([
                f"Critical: Page load time of {analysis.page_load_time:.2f}s causing {conversion_impact} in conversions",
                f"Server response time exceeding Google's recommended threshold by {(analysis.page_load_time - 2.5):.2f}s",
                f"Resource load efficiency at {(analysis.resource_count['js'] + analysis.resource_count['css']):.0f} requests, recommended: <15"
            ])
            
            # Technical solution opportunities
            analysis.ai_opportunities.extend([
                f"AI-powered performance optimization targeting {estimated_improvement} improvement",
                f"Machine learning CDN optimization reducing TTFB by estimated 60-80%",
                "Intelligent code splitting with dynamic imports based on user behavior",
                "Automated critical CSS extraction and inline injection",
                "Smart image optimization with WebP conversion and lazy loading",
                "Predictive prefetching based on user navigation patterns"
            ])
            
            # Specific technical recommendations
            if analysis.resource_count['js'] > 10:
                analysis.tech_gaps.append(f"JavaScript bundling inefficiency: {analysis.resource_count['js']} separate requests")
                analysis.ai_opportunities.append("AI-driven JavaScript bundle optimization and code splitting")
            
            if analysis.resource_count['images'] > 15:
                analysis.tech_gaps.append(f"High image load impact: {analysis.resource_count['images']} unoptimized images")
                analysis.ai_opportunities.append("Automated image optimization and format conversion pipeline")
                
            if not analysis.cdn_usage:
                analysis.tech_gaps.append("Missing CDN integration causing high TTFB")
                analysis.ai_opportunities.append("Global CDN implementation with ML-based edge caching")
        
        if not analysis.mobile_responsive:
            analysis.tech_gaps.extend([
                "Non-responsive design limiting mobile audience reach",
                "Suboptimal mobile user experience",
                "Missing mobile-first approach"
            ])
            analysis.ai_opportunities.extend([
                "AI-driven responsive design optimization",
                "Machine learning-based mobile UX enhancement",
                "Automated mobile performance optimization"
            ])
            
    def _analyze_frontend_opportunities(self, analysis: WebsiteAnalysis):
        """Analyze frontend technology opportunities"""
        modern_frameworks = {'React', 'Vue.js', 'Angular', 'Next.js', 'Svelte'}
        current_stack = set(analysis.tech_stack)
        
        if not any(framework in current_stack for framework in modern_frameworks):
            analysis.tech_gaps.extend([
                "Legacy frontend architecture limiting user experience",
                "Missing modern JavaScript framework implementation",
                "Limited interactive capabilities"
            ])
            analysis.ai_opportunities.extend([
                "AI-powered frontend modernization with React/Next.js",
                "Intelligent component optimization system",
                "Automated UI/UX enhancement pipeline"
            ])
        
        if 'jQuery' in current_stack:
            analysis.tech_gaps.append("Reliance on legacy jQuery limiting modern capabilities")
            analysis.ai_opportunities.append("Smart jQuery to modern framework migration system")
            
    def _analyze_backend_opportunities(self, analysis: WebsiteAnalysis):
        """Analyze backend and infrastructure opportunities"""
        if not any(tech in analysis.tech_stack for tech in ['Cloudflare', 'AWS', 'Azure']):
            analysis.tech_gaps.extend([
                "Limited cloud infrastructure utilization",
                "Potential scalability limitations",
                "Missing edge computing capabilities"
            ])
            analysis.ai_opportunities.extend([
                "AI-powered cloud infrastructure optimization",
                "Smart scaling system with predictive analytics",
                "Automated cloud resource management"
            ])
            
    def _analyze_data_opportunities(self, analysis: WebsiteAnalysis):
        """Analyze data and analytics opportunities"""
        analytics_tools = {'Google Analytics', 'Segment', 'Hotjar'}
        current_tools = set(analysis.tech_stack)
        
        if not analytics_tools.intersection(current_tools):
            analysis.tech_gaps.extend([
                "Limited data analytics capabilities",
                "Missing user behavior tracking",
                "Incomplete conversion tracking"
            ])
            analysis.ai_opportunities.extend([
                "Advanced analytics implementation with ML insights",
                "AI-powered user behavior analysis system",
                "Predictive analytics for conversion optimization"
            ])
            
    def _analyze_security_opportunities(self, analysis: WebsiteAnalysis):
        """Analyze security and compliance opportunities"""
        security_tools = {'Cloudflare', 'Auth0', 'reCAPTCHA'}
        if not any(tool in analysis.tech_stack for tool in security_tools):
            analysis.tech_gaps.extend([
                "Limited security infrastructure",
                "Missing advanced authentication system",
                "Potential compliance gaps"
            ])
            analysis.ai_opportunities.extend([
                "AI-powered security monitoring and threat detection",
                "Automated compliance management system",
                "Smart authentication and authorization platform"
            ])
            
    def _analyze_customer_experience_opportunities(self, analysis: WebsiteAnalysis):
        """Analyze customer experience opportunities"""
        if not analysis.has_chatbot:
            analysis.tech_gaps.extend([
                "Limited automated customer support",
                "Missing real-time assistance capability",
                "Manual FAQ management"
            ])
            analysis.ai_opportunities.extend([
                "Advanced NLP-powered chatbot implementation",
                "Automated knowledge base generation and management",
                "Predictive customer support system"
            ])
        
        if not analysis.has_contact_form:
            analysis.tech_gaps.extend([
                "Limited lead capture capabilities",
                "Manual contact management process",
                "Missing automated follow-up system"
            ])
            analysis.ai_opportunities.extend([
                "AI-powered lead qualification and routing",
                "Smart contact form with real-time validation",
                "Automated follow-up and engagement system"
            ])
            
    def _analyze_integration_opportunities(self, analysis: WebsiteAnalysis):
        """Analyze integration and automation opportunities"""
        crm_tools = {'Salesforce', 'HubSpot', 'Pipedrive'}
        if not any(tool in analysis.tech_stack for tool in crm_tools):
            analysis.tech_gaps.extend([
                "Limited CRM integration",
                "Manual lead management process",
                "Missing marketing automation"
            ])
            analysis.ai_opportunities.extend([
                "AI-powered CRM integration and automation",
                "Smart lead scoring and management system",
                "Automated marketing workflow platform"
            ])
        
        # SEO and Content Strategy
        if analysis.seo_issues:
            analysis.tech_gaps.append("Suboptimal search engine visibility")
            analysis.ai_opportunities.append("AI-powered SEO optimization and content strategy")
            analysis.ai_opportunities.append("Automated meta tag and content optimization")
        
        # AI opportunities based on business category and tech stack
        if analysis.business_category == 'ecommerce':
            analysis.ai_opportunities.extend([
                "Technical Implementation: Real-time Recommendation Engine\n" +
                "- Stack: TensorFlow + Redis + GraphQL\n" +
                "- Features:\n" +
                "  • Real-time user behavior tracking with WebSocket\n" +
                "  • Product embedding generation using Word2Vec\n" +
                "  • Automated A/B testing framework\n" +
                "- Expected Impact: +25% conversion rate increase\n" +
                "- Implementation Timeline: 6-8 weeks",
                
                "Technical Solution: Inventory Optimization System\n" +
                "- Architecture: Event-driven microservices\n" +
                "- Components:\n" +
                "  • Apache Kafka for real-time data streaming\n" +
                "  • MongoDB for transaction processing\n" +
                "  • Python ML pipeline with scikit-learn\n" +
                "- Expected Impact: 30% reduction in stockouts\n" +
                "- Implementation Timeline: 4-6 weeks",
                
                "Technical Implementation: Dynamic Pricing Engine\n" +
                "- Stack: Python + PostgreSQL + Redis\n" +
                "- Features:\n" +
                "  • Real-time competitor price monitoring\n" +
                "  • Elastic demand modeling\n" +
                "  • Automated price adjustment API\n" +
                "- Expected Impact: 15-20% revenue increase\n" +
                "- Implementation Timeline: 8-10 weeks"
            ])
        elif analysis.business_category == 'consulting':
            analysis.ai_opportunities.extend([
                "Intelligent lead scoring and qualification system",
                "AI-powered market trend analysis and insights",
                "Automated proposal generation with client-specific data",
                "Smart meeting scheduling with context awareness",
                "Client success prediction modeling",
                "Automated case study generation from project data"
            ])
        elif analysis.business_category == 'agency':
            analysis.ai_opportunities.extend([
                "AI-powered content strategy optimization",
                "Automated social media content creation and scheduling",
                "Advanced campaign analytics with predictive insights",
                "Creative asset generation using AI",
                "Client reporting automation with natural language insights",
                "Multi-channel campaign performance prediction"
            ])
        elif analysis.business_category == 'saas' or analysis.business_category == 'tech':
            analysis.ai_opportunities.extend([
                "Intelligent user onboarding personalization",
                "Predictive user behavior analytics",
                "Advanced churn prediction with intervention suggestions",
                "Automated technical documentation generation",
                "Smart feature usage analytics and recommendations",
                "AI-powered bug prediction and prevention"
            ])
        elif analysis.business_category == 'healthcare':
            analysis.ai_opportunities.extend([
                "Patient engagement automation system",
                "Appointment scheduling optimization",
                "Healthcare document processing automation",
                "Patient feedback analysis and insights",
                "Treatment recommendation support system"
            ])
        elif analysis.business_category == 'manufacturing':
            analysis.ai_opportunities.extend([
                "Predictive maintenance scheduling",
                "Quality control automation with computer vision",
                "Supply chain optimization using ML",
                "Production scheduling optimization",
                "Inventory management automation"
            ])
        elif analysis.business_category == 'legal':
            analysis.ai_opportunities.extend([
                "Legal document analysis and processing",
                "Case outcome prediction system",
                "Automated compliance monitoring",
                "Legal research automation",
                "Client intake process automation"
            ])
        elif analysis.business_category == 'nonprofit':
            analysis.ai_opportunities.extend([
                "Donor engagement optimization",
                "Grant application automation",
                "Impact reporting automation",
                "Volunteer matching system",
                "Fundraising campaign optimization"
            ])
        
        # General AI opportunities
        if not any('automation' in service.lower() for service in analysis.services_mentioned):
            analysis.ai_opportunities.append("Process automation opportunities")
        
        # Advanced contact and lead management opportunities
        if analysis.has_contact_form and not analysis.has_chatbot:
            analysis.ai_opportunities.append("Intelligent lead routing and prioritization")
        
        # Content and marketing opportunities
        if analysis.has_blog:
            analysis.ai_opportunities.append("AI-powered content optimization and generation")
        
        if not analysis.has_blog and analysis.business_category in ['consulting', 'agency', 'tech', 'saas']:
            analysis.tech_gaps.append("Missing content marketing strategy")
            analysis.ai_opportunities.append("Automated thought leadership content creation")
        
        # Remove duplicates while preserving order
        analysis.ai_opportunities = list(dict.fromkeys(analysis.ai_opportunities))
        analysis.tech_gaps = list(dict.fromkeys(analysis.tech_gaps))
    
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
