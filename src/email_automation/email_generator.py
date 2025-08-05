"""
Email Generator Module
=====================

Generates personalized email content based on AI insights and prospect information.
Creates compelling subject lines and email bodies for outreach campaigns.
"""

import logging
try:
    # Try importing the new OpenAI client (v1.0+)
    from openai import OpenAI
    OPENAI_NEW_API = True
except ImportError:
    # Fall back to legacy OpenAI API
    import openai
    OPENAI_NEW_API = False

import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from .ai_analyzer import AIInsights
from .prospect_manager import Prospect
import random


@dataclass
class EmailContent:
    """Data class for generated email content"""
    subject_line: str
    email_body: str
    call_to_action: str
    personalization_score: float
    tone: str = "professional"
    
    def get_preview(self, length: int = 100) -> str:
        """Get a preview of the email content"""
        preview = self.email_body.replace('\n', ' ').strip()
        return preview[:length] + ('...' if len(preview) > length else '')


class EmailGenerator:
    """Generates personalized email content using AI insights"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini",
                 max_tokens: int = 800, temperature: float = 0.8,
                 config: Optional[Any] = None,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize Email Generator
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
            max_tokens: Maximum tokens for response
            temperature: Response creativity (0.0-1.0)
            config: Configuration manager instance
            logger: Logger instance
        """
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize OpenAI client based on version
        if OPENAI_NEW_API:
            self.client = OpenAI(api_key=self.api_key)
        else:
            # Fall back to legacy API
            import openai
            openai.api_key = self.api_key
            self.client = openai
        
        # Enhanced email templates and patterns with more variety and specificity
        self.subject_patterns = {
            'data_driven': [
                "{company}'s conversion rate could increase by {percentage}%",
                "{first_name}, your site loads {seconds}s slower than competitors",
                "Found a {value} revenue leak at {company}",
                "{company}'s mobile traffic drops by {percentage}% - here's why",
                "Your {tech_stack} setup is costing {company} {amount} annually"
            ],
            'curiosity_driven': [
                "{first_name}, noticed something unusual about {company}",
                "Quick question about {company}'s {technology} implementation",
                "{company} vs {competitor} - spotted a key difference",
                "Your {business_category} competitors are doing this differently",
                "{first_name}, is {company} planning to scale {specific_area}?"
            ],
            'opportunity_focused': [
                "{company}'s untapped {opportunity_type} potential",
                "{first_name}, your {pain_point} solution is simpler than you think",
                "How {similar_company} increased {metric} by {percentage}% with {solution}",
                "{company} could save {amount} with this one change",
                "The {technology} upgrade {company} needs for {goal}"
            ],
            'industry_specific': [
                "{industry} leaders are implementing {technology} - is {company}?",
                "{first_name}, {industry} regulations changing - {company} ready?",
                "New {industry} compliance requirements affect {company}",
                "{industry} trend: {technology} adoption up {percentage}%",
                "{company}'s {industry} positioning opportunity"
            ],
            'technical_insight': [
                "{first_name}, your {tech_metric} indicates {specific_issue}",
                "{company}'s {technology} architecture needs attention",
                "Found {number} performance bottlenecks on {company}'s site",
                "{technology} deprecation affects {company} - timeline?",
                "Your {tech_stack} could be {percentage}% more efficient"
            ]
        }
        
        self.email_hooks = {
            'metric_based': [
                "Your website's {metric} is currently {current_value}, but industry leaders in {industry} are achieving {target_value}.",
                "I noticed {company}'s {technology} implementation could be optimized to increase {business_metric} by approximately {percentage}%.",
                "Your current {tech_stack} configuration is processing {current_performance}, but there's potential to reach {improved_performance} with targeted optimization."
            ],
            'competitive_intelligence': [
                "While analyzing {industry} companies, I found that {company} has a unique opportunity that your main competitors haven't capitalized on yet.",
                "Your competitors in {industry} are missing something that {company} could leverage for significant advantage.",
                "I've been tracking {industry} trends and noticed {company} is positioned perfectly for a strategic move your competitors can't replicate."
            ],
            'specific_observation': [
                "I was reviewing {company}'s {specific_feature} and identified a pattern that typically indicates {business_opportunity}.",
                "Your {technology} setup shows characteristics I've seen in companies right before they scaled successfully.",
                "While researching {industry} solutions, {company}'s approach to {specific_area} caught my attention for an interesting reason."
            ],
            'urgency_without_pressure': [
                "With {industry} evolving rapidly, there's a narrow window for {company} to implement {solution} before it becomes standard practice.",
                "The {technology} landscape is shifting, and {company} has about {timeframe} to capitalize on the current advantage.",
                "Based on {industry} adoption rates, {company} has a first-mover advantage that won't last beyond {timeframe}."
            ]
        }
        
        self.value_propositions = {
            'revenue_growth': [
                "increase revenue by {percentage}% through {specific_solution}",
                "capture an additional ${amount} annually via {optimization_area}",
                "boost conversion rates by {percentage}% with {technology_implementation}",
                "unlock ${amount} in untapped revenue through {strategic_change}"
            ],
            'cost_reduction': [
                "reduce operational costs by ${amount} annually through {automation_solution}",
                "eliminate {percentage}% of manual processes with {technology}",
                "cut {expense_category} expenses by ${amount} monthly via {optimization}",
                "save {hours} hours weekly through {efficiency_improvement}"
            ],
            'competitive_advantage': [
                "establish market leadership in {specific_area} before competitors catch up",
                "create a {timeframe} competitive moat through {technology_advantage}",
                "position {company} as the go-to {industry} provider for {service_area}",
                "differentiate from {number} competitors through {unique_implementation}"
            ],
            'efficiency_gains': [
                "streamline {process_area} to achieve {percentage}% efficiency improvement",
                "automate {specific_workflow} reducing processing time by {timeframe}",
                "optimize {system_component} for {percentage}% performance improvement",
                "enhance {user_experience_area} resulting in {metric_improvement}"
            ]
        }
        
        self.cta_templates = {
            'consultative': [
                "Would you be interested in seeing the specific analysis I put together for {company}?",
                "I'd be happy to share the detailed breakdown of how this could work for {company} - interested in a brief call?",
                "Should I send over the implementation roadmap I drafted for similar {industry} companies?",
                "Would a 15-minute technical discussion about {specific_solution} be valuable?"
            ],
            'collaborative': [
                "I'm curious about {company}'s current priorities in {area} - does this align with your roadmap?",
                "Would you be open to exploring how this fits with {company}'s existing {technology_stack}?",
                "I'd love to understand {company}'s perspective on {industry_challenge} - brief chat possible?",
                "Interested in comparing notes on {technology_area} implementations?"
            ],
            'value_focused': [
                "Would you like me to model the potential {metric} impact for {company} specifically?",
                "Should I prepare a cost-benefit analysis tailored to {company}'s situation?",
                "Interested in seeing the ROI projections I calculated for {specific_solution}?",
                "Would a brief demo of {solution} working with {company}'s setup be helpful?"
            ],
            'low_pressure': [
                "No agenda here - just thought this might be relevant to {company}'s growth plans.",
                "Feel free to ignore if timing isn't right, but I thought you might find this interesting.",
                "Not sure if this fits {company}'s current priorities, but worth a quick discussion?",
                "This might not be a priority right now, but the opportunity seemed worth mentioning."
            ]
        }
        
        self.tone_configurations = {
            'professional': {
                'formality': 'formal',
                'personality': 'professional and respectful',
                'language': 'business-appropriate',
                'approach': 'consultative'
            },
            'friendly': {
                'formality': 'semi-formal',
                'personality': 'friendly and approachable',
                'language': 'conversational but professional',
                'approach': 'collaborative'
            },
            'direct': {
                'formality': 'formal',
                'personality': 'direct and results-oriented',
                'language': 'concise and clear',
                'approach': 'solution-focused'
            }
        }
    
    def generate_email(self, prospect: Prospect, insights: AIInsights,
                      personalization_data: Dict[str, Any],
                      tone: str = "professional") -> Optional[EmailContent]:
        """
        Generate personalized email content
        
        Args:
            prospect: Prospect information
            insights: AI-generated insights
            personalization_data: Additional personalization data
            tone: Email tone (professional, friendly, direct)
            
        Returns:
            EmailContent object or None if generation failed
        """
        try:
            self.logger.info(f"Generating email for {prospect.first_name} at {prospect.company_name}")
            
            # Generate email content using AI
            email_response = self._generate_email_content(
                prospect, insights, personalization_data, tone
            )
            
            if not email_response:
                return None
            
            # Parse the response
            subject, body, cta = self._parse_email_response(email_response)
            
            # Calculate personalization score
            personalization_score = self._calculate_personalization_score(
                subject, body, prospect, insights
            )
            
            # Create EmailContent object
            email_content = EmailContent(
                subject_line=subject,
                email_body=body,
                call_to_action=cta,
                personalization_score=personalization_score,
                tone=tone
            )
            
            self.logger.info(f"Generated email with personalization score: {personalization_score:.2f}")
            return email_content
            
        except Exception as e:
            self.logger.error(f"Error generating email: {e}")
            return None
    
    def _generate_email_content(self, prospect: Prospect, insights: AIInsights,
                               personalization_data: Dict[str, Any], tone: str) -> Optional[str]:
        """Generate email content using OpenAI"""
        try:
            # Create comprehensive prompt
            prompt = self._create_email_prompt(prospect, insights, personalization_data, tone)
            
            # Call OpenAI API
            if OPENAI_NEW_API:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": self._get_email_system_prompt(tone)
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                return response.choices[0].message.content
            else:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": self._get_email_system_prompt(tone)
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error calling OpenAI API: {e}")
            return None
    
    def _get_email_system_prompt(self, tone: str) -> str:
        """Get system prompt for email generation"""
        tone_config = self.tone_configurations.get(tone, self.tone_configurations['professional'])
        
        # Get sender name from config or use default
        sender_name = "Your Technical Solutions Consultant"
        try:
            if self.config and hasattr(self.config, 'email_config') and hasattr(self.config.email_config, 'sender_name'):
                sender_name = self.config.email_config.sender_name
        except AttributeError as e:
            self.logger.warning(f"Could not access sender name from config: {e}")
            pass
        
        return f"""You are {sender_name}, a freelance business technology consultant who specializes in finding revenue opportunities and competitive advantages through technology.

        Your unique approach as a Technical Solutions Architect:
        - Deep technical analysis of infrastructure, code, and systems
        - Specific technical recommendations backed by performance metrics
        - Focus on modern architectural solutions and technology stack optimization
        - Balance between cutting-edge tech implementation and business value
        
        Your technical expertise areas:
        1. Performance Optimization
           - Frontend optimization (Core Web Vitals, code splitting, lazy loading)
           - Backend architecture (microservices, caching layers, database optimization)
           - Infrastructure scaling (cloud architecture, load balancing, CDN implementation)
        
        2. Modern Tech Stack Implementation
           - Frontend: React/Next.js, TypeScript, PWA capabilities
           - Backend: Node.js/Python, GraphQL APIs, WebSocket
           - Database: MongoDB, PostgreSQL, Redis caching
        
        3. AI/ML Integration
           - Custom ML model development and deployment
           - NLP for customer service automation
           - Predictive analytics implementation
        
        4. Security & Scalability
           - OAuth 2.0 and JWT implementation
           - Microservices architecture design
           - Docker/Kubernetes deployment
        
        5. Data Architecture
           - Real-time analytics pipeline setup
           - Data warehouse optimization
           - ETL process automation
        
        Your background:
        - 5+ years in technical architecture and development
        - Specialized in scalable, high-performance solutions
        - Track record of successful technical transformations
        - Work with international clients from India
        - Focus on projects requiring sophisticated technical solutions
        
        Email writing rules:
        1. **Hook with technical insight** - Demonstrate deep technical understanding of their current setup
           Example: "Your React app's client-side rendering is causing a 3.2s First Contentful Paint"
        
        2. **Provide specific technical solution** - Detail exact implementation approach
           Example: "Implementing server-side rendering with Next.js and edge caching could reduce this to sub-500ms"
        
        3. **Show technical expertise** - Reference relevant technologies and methodologies
           Example: "Using React.lazy() for component splitting and a Redis caching layer"
        
        4. **Include measurable metrics** - Quote specific performance numbers
           Example: "Recent implementation reduced API response time by 76% through GraphQL optimization"
        
        5. **Technical differentiation** - Show why your technical approach is superior
           Example: "Unlike basic caching, our distributed caching architecture ensures real-time data consistency"
        
        Email structure:
        - Open with specific technical metric or insight from their system
        - Detail ONE technical solution with implementation approach
        - Show expertise through specific tech stack recommendations
        - Include performance metrics from similar implementations
        - End with technical discussion invitation
        - Sign: "Best regards, Debraj Mukherjee"
        
        Technical Focus Areas (Rotate based on analysis):
        1. Performance Optimization
           - Core Web Vitals metrics
           - API response times
           - Database query optimization
        
        2. Architecture Modernization
           - Microservices implementation
           - Cloud infrastructure
           - Serverless architecture
        
        3. AI/ML Integration
           - Custom model deployment
           - NLP implementation
           - Predictive analytics
        
        4. Data Engineering
           - Real-time analytics
           - ETL automation
           - Data warehouse optimization
        
        5. Security Enhancement
           - Auth implementation
           - API security
           - Compliance automation
        
        Tone: {tone_config['personality']}
        Length: 120-180 words maximum
        
        AVOID:
        - Generic compliments about their website
        - Lists of technical improvements
        - Sounding like every other web developer
        - Being pushy or sales-focused
        
        FOCUS ON:
        - Specific business challenges you identified
        - Revenue or efficiency opportunities
        - Industry knowledge and understanding
        - Creating a peer-to-peer technical consultant conversation
        - Making them think "This person gets our business"
        
        Write as if you're a technical consultant who happened to analyze their online presence, not a web developer looking for work."""
    
    def _create_email_prompt(self, prospect: Prospect, insights: AIInsights,
                            personalization_data: Dict[str, Any], tone: str) -> str:
        """Create detailed email generation prompt"""
        
        primary_opportunity = personalization_data.get('primary_opportunity', 'website optimization')
        pain_point = personalization_data.get('primary_pain_point', 'operational efficiency')
        
        # Categorize opportunities for better email variety
        opportunity_categories = self._categorize_opportunities(insights.opportunities)
        selected_category = self._select_email_focus(opportunity_categories)
        
        # Get sender name from config or use default
        sender_name = "Your Technical Solutions Consultant"
        try:
            if self.config and hasattr(self.config, 'email_config') and hasattr(self.config.email_config, 'sender_name'):
                sender_name = self.config.email_config.sender_name
        except AttributeError as e:
            self.logger.warning(f"Could not access sender name from config: {e}")
            pass
        
        prompt = f"""
        Create a compelling business outreach email from {sender_name} to {prospect.first_name} {prospect.last_name} 
        ({prospect.job_position} at {prospect.company_name}).
        
        CRITICAL BUSINESS INSIGHTS DISCOVERED:
        Top opportunity: {insights.opportunities[0] if insights.opportunities else primary_opportunity}
        Business impact: {insights.roi_potential}
        Key challenge: {insights.pain_points[0] if insights.pain_points else pain_point}
        Competitive gap: {insights.competitive_gaps[0] if insights.competitive_gaps else 'industry positioning'}
        
        WRITING STRATEGY:
        1. **Hook with business insight** - Open with a specific observation about their business that shows you understand their challenges
        2. **Demonstrate value** - Mention ONE compelling opportunity that would impact revenue/efficiency
        3. **Position as consultant** - You're not selling web services, you're discussing business improvements
        4. **Create curiosity** - Hint at other opportunities without listing everything
        5. **Soft invitation** - Position as exploring mutual fit, not pitching services
        
        EMAIL TONE REQUIREMENTS:
        - Sound like a technical consultant who analyzed their company
        - Focus on business outcomes (revenue, efficiency, competitive advantage)
        - Avoid technical jargon - speak in business terms
        - Be specific to their industry and company
        - Create peer-to-peer professional conversation
        
        SPECIFIC REQUIREMENTS:
        - Length: 120-180 words maximum
        - Start with "Hi {prospect.first_name}," 
        - Open with specific insight about their business/website
        - Focus on business impact, not technical features
        - Mention ONE compelling opportunity clearly
        - Position as business strategist, not web developer
        - End with consultative invitation to discuss
        - Include proper email signature: "Best regards,\\n{sender_name}"
        
        AVOID THESE COMMON MISTAKES:
        - Generic compliments about their website
        - Lists of technical improvements
        - Mentioning "AI chatbots" unless directly relevant
        - Sounding like a typical web developer pitch
        - Being pushy or sales-focused
        - Talking about SEO unless it's a specific revenue opportunity
        
        Return in JSON format:
        {{
            "subject": "Specific tech insight about {prospect.company_name} (under 60 characters)",
            "body": "Hi {prospect.first_name},\\n\\n[Main email content]\\n\\n[Call to action question]\\n\\nBest regards,\\n{sender_name}",
            "cta": "Consultative invitation to discuss further"
        }}
        
        IMPORTANT: The email body must start with "Hi {prospect.first_name}," and end with:\\n\\nBest regards,\\n{sender_name}
        
        Make {prospect.first_name} think: "This person actually understands our business and has found something valuable."
        """
        
        return prompt
    
    def _categorize_opportunities(self, opportunities: List[str]) -> Dict[str, List[str]]:
        """Categorize opportunities by type for varied email approaches"""
        categories = {
            'technical': [],
            'marketing': [],
            'automation': [],
            'ux_conversion': [],
            'data_analytics': [],
            'performance': []
        }
        
        for opp in opportunities:
            opp_lower = opp.lower()
            if any(term in opp_lower for term in ['performance', 'speed', 'load time', 'optimization', 'technical']):
                categories['technical'].append(opp)
            elif any(term in opp_lower for term in ['seo', 'content', 'marketing', 'visibility', 'search']):
                categories['marketing'].append(opp)
            elif any(term in opp_lower for term in ['automation', 'workflow', 'process', 'manual', 'automated']):
                categories['automation'].append(opp)
            elif any(term in opp_lower for term in ['conversion', 'user experience', 'ux', 'navigation', 'design']):
                categories['ux_conversion'].append(opp)
            elif any(term in opp_lower for term in ['analytics', 'tracking', 'data', 'insights', 'reporting']):
                categories['data_analytics'].append(opp)
            else:
                categories['performance'].append(opp)  # Default category
        
        return categories
    
    def _select_email_focus(self, opportunity_categories: Dict[str, List[str]]) -> Dict[str, str]:
        """
        Select email focus based on available opportunities with detailed technical solutions
        
        Returns:
            Dictionary containing focus area, technical approach, value proposition,
            specific technologies, and implementation details
        """
        focus_options = {
            'technical': {
                'focus_area': 'technical performance optimization',
                'approach': 'Full-stack performance engineering and optimization',
                'value_prop': 'Sub-second load times and optimal resource utilization',
                'technologies': ['Next.js', 'Redis', 'CloudFront', 'WebP/AVIF', 'Service Workers'],
                'implementation': {
                    'frontend': 'Dynamic imports, code splitting, asset optimization',
                    'backend': 'Caching layers, database indexing, query optimization',
                    'infrastructure': 'CDN implementation, edge computing, load balancing'
                }
            },
            'marketing': {
                'focus_area': 'technical SEO and analytics architecture',
                'approach': 'Data-driven marketing infrastructure development',
                'value_prop': 'Automated SEO optimization and conversion tracking',
                'technologies': ['Next.js', 'Google Analytics 4', 'Schema.org', 'GTM', 'BigQuery'],
                'implementation': {
                    'frontend': 'SSR/SSG optimization, structured data implementation',
                    'tracking': 'Custom event tracking, conversion attribution',
                    'automation': 'Automated reporting, A/B testing infrastructure'
                }
            },
            'automation': {
                'focus_area': 'process automation and integration',
                'approach': 'Custom automation system development',
                'value_prop': 'End-to-end workflow automation and integration',
                'technologies': ['Node.js', 'Python', 'Docker', 'RabbitMQ', 'Redis'],
                'implementation': {
                    'backend': 'Microservices architecture, API development',
                    'integration': 'Custom API connectors, webhook systems',
                    'monitoring': 'Real-time metrics, alerting systems'
                }
            },
            'ux_conversion': {
                'focus_area': 'frontend architecture optimization',
                'approach': 'Modern frontend development and UX engineering',
                'value_prop': 'Performant, conversion-optimized user experiences',
                'technologies': ['React', 'Next.js', 'TailwindCSS', 'Framer Motion'],
                'implementation': {
                    'frontend': 'Component architecture, state management',
                    'performance': 'Core Web Vitals optimization, PWA implementation',
                    'analytics': 'User journey tracking, conversion funnels'
                }
            },
            'data_analytics': {
                'focus_area': 'data engineering and analytics architecture',
                'approach': 'Custom analytics infrastructure development',
                'value_prop': 'Real-time data processing and visualization',
                'technologies': ['Python', 'PostgreSQL', 'Apache Kafka', 'Elasticsearch'],
                'implementation': {
                    'backend': 'Data pipeline development, ETL processes',
                    'storage': 'Data warehouse design, optimization',
                    'visualization': 'Custom dashboard development'
                }
            },
            'performance': {
                'focus_area': 'full-stack system optimization',
                'approach': 'Comprehensive technical architecture enhancement',
                'value_prop': 'Scalable, high-performance system architecture',
                'technologies': ['Kubernetes', 'AWS/GCP', 'Terraform', 'Prometheus'],
                'implementation': {
                    'infrastructure': 'Cloud architecture, container orchestration',
                    'monitoring': 'Performance monitoring, automated scaling',
                    'security': 'Security hardening, compliance automation'
                }
            }
        }
        
        # Find categories with opportunities
        valid_categories = {k: v for k, v in opportunity_categories.items() if v}
        
        if not valid_categories:
            # Fallback to performance if no specific opportunities found
            return focus_options['performance']
        
        # Select primary and secondary focus areas
        primary_category = max(valid_categories.keys(), 
                             key=lambda x: len(valid_categories[x]))
        
        # Get the focus option for the primary category
        focus = focus_options.get(primary_category, focus_options['performance'])
        
        # Find secondary category for additional context
        other_categories = [k for k in valid_categories.keys() if k != primary_category]
        if other_categories:
            secondary_category = max(other_categories,
                                  key=lambda x: len(valid_categories[x]))
            # Enhance implementation details with secondary focus
            secondary_focus = focus_options[secondary_category]
            focus['implementation'].update({
                'additional': f"Integration with {secondary_focus['focus_area']}",
                'synergy': f"Combined {focus['focus_area']} with {secondary_focus['focus_area']}"
            })
            # Add relevant technologies from secondary focus
            focus['technologies'].extend([tech for tech in secondary_focus['technologies']
                                       if tech not in focus['technologies']][:2])
        
        return focus
    
    def _parse_email_response(self, response: str) -> Tuple[str, str, str]:
        """Parse AI response into email components"""
        try:
            self.logger.info(f"Raw AI response (first 500 chars): {response[:500]}")
            
            # Try to parse as JSON
            if response.strip().startswith('{'):
                data = json.loads(response)
                return (
                    data.get('subject', ''),
                    data.get('body', ''),
                    data.get('cta', '')
                )
            else:
                # Try to extract JSON from the response
                start_idx = response.find('{')
                end_idx = response.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx+1]
                    self.logger.info(f"Extracted JSON: {json_str[:200]}")
                    data = json.loads(json_str)
                    return (
                        data.get('subject', ''),
                        data.get('body', ''),
                        data.get('cta', '')
                    )
                else:
                    # Fallback: parse as text
                    return self._parse_text_email(response)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return self._parse_text_email(response)
    
    def _parse_text_email(self, text: str) -> Tuple[str, str, str]:
        """Parse text email response"""
        lines = text.split('\n')
        
        subject = ""
        body_lines = []
        cta = ""
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if 'subject' in line.lower() and ':' in line:
                subject = line.split(':', 1)[1].strip()
                current_section = 'subject'
            elif 'body' in line.lower() and ':' in line:
                current_section = 'body'
            elif 'cta' in line.lower() or 'call to action' in line.lower():
                current_section = 'cta'
            elif current_section == 'body' and line:
                body_lines.append(line)
            elif current_section == 'cta' and line:
                cta = line
        
        # If no structured parsing worked, treat as a complete email
        if not body_lines and not subject:
            # The whole response is likely the email body
            if len(text.strip()) > 50:  # Reasonable email length
                # Try to extract subject from first line if it looks like one
                first_line = lines[0].strip() if lines else ""
                if len(first_line) < 80 and not first_line.endswith('.'):
                    subject = first_line
                    body_lines = lines[1:]
                else:
                    subject = f"Opportunity for WorkInnov8's digital transformation"
                    body_lines = lines
                
                # Add a default CTA if missing
                if not cta:
                    cta = "Would you be open to a brief 15-minute conversation this week?"
            else:
                # Fallback for very short responses
                sender_name = "Your Technical Solutions Consultant"
                try:
                    if self.config and hasattr(self.config, 'email_config') and hasattr(self.config.email_config, 'sender_name'):
                        sender_name = self.config.email_config.sender_name
                except AttributeError:
                    pass
                
                subject = "Quick tech insight for your business"
                body_lines = [
                    f"Hi there,",
                    f"",
                    f"I recently analyzed your website and noticed some interesting opportunities for optimization.",
                    f"As someone new to freelancing but with strong technical expertise, I'd love to share my findings with you.",
                    f"",
                    f"Best regards,",
                    f"{sender_name}"
                ]
                cta = "Would you be interested in a quick chat?"
        
        body = '\n\n'.join(body_lines) if body_lines else '\n\n'.join([line for line in lines if line.strip()])
        
        return subject, body, cta
    
    def _calculate_personalization_score(self, subject: str, body: str,
                                       prospect: Prospect, insights: AIInsights) -> float:
        """Calculate email personalization score (0.0 to 1.0)"""
        score = 0.0
        body_lower = body.lower()
        
        # Check for prospect-specific information (30% of score)
        if prospect.first_name.lower() in body_lower:
            score += 0.10
        if prospect.company_name.lower() in body_lower:
            score += 0.15
        if prospect.job_position.lower() in body_lower:
            score += 0.05
        
        # Check for specific insights (40% of score)
        insight_mentions = 0
        all_insights = insights.opportunities + insights.pain_points + insights.recommendations
        
        for insight in all_insights[:5]:  # Check top 5 insights
            insight_words = [word for word in insight.split() if len(word) > 4]
            if any(word.lower() in body_lower for word in insight_words):
                insight_mentions += 1
        
        score += min(insight_mentions * 0.08, 0.40)
        
        # Check for specific business context (15% of score)
        business_terms = ['revenue', 'customers', 'growth', 'optimization', 'efficiency', 'competitive']
        business_mentions = sum(1 for term in business_terms if term in body_lower)
        score += min(business_mentions * 0.02, 0.15)
        
        # Check for proper email structure (15% of score)
        structure_score = 0.0
        if f"hi {prospect.first_name.lower()}" in body_lower:
            structure_score += 0.05
        if "best regards" in body_lower:
            structure_score += 0.05
        if any(phrase in body_lower for phrase in ["would you", "interested in", "call", "chat", "discuss"]):
            structure_score += 0.05
        
        score += structure_score
        
        return min(score, 1.0)
    
    def generate_subject_lines(self, prospect: Prospect, insights: AIInsights,
                             count: int = 5) -> List[str]:
        """Generate multiple subject line options"""
        subject_lines = []
        
        try:
            # Use patterns with personalization
            for pattern in random.sample(self.subject_patterns, min(count, len(self.subject_patterns))):
                subject = pattern.format(
                    first_name=prospect.first_name,
                    company=prospect.company_name,
                    opportunity=insights.opportunities[0][:20] if insights.opportunities else "tech upgrade",
                    industry="tech",
                    pain_point=insights.pain_points[0][:20] if insights.pain_points else "efficiency"
                )
                subject_lines.append(subject[:60])  # Limit to 60 characters
            
            # Generate additional AI-powered subjects if needed
            if len(subject_lines) < count:
                ai_subjects = self._generate_ai_subjects(prospect, insights, count - len(subject_lines))
                subject_lines.extend(ai_subjects)
            
            return subject_lines[:count]
            
        except Exception as e:
            self.logger.error(f"Error generating subject lines: {e}")
            return [f"Quick question for {prospect.first_name} at {prospect.company_name}"]
    
    def _generate_ai_subjects(self, prospect: Prospect, insights: AIInsights, count: int) -> List[str]:
        """Generate subject lines using AI"""
        try:
            prompt = f"""
            Generate {count} compelling email subject lines for outreach to:
            - {prospect.first_name} {prospect.last_name}, {prospect.job_position} at {prospect.company_name}
            - Primary opportunity: {insights.opportunities[0] if insights.opportunities else 'AI automation'}
            - Key pain point: {insights.pain_points[0] if insights.pain_points else 'efficiency'}
            
            Requirements:
            - Under 60 characters
            - Specific to their business
            - Professional but intriguing
            - Not salesy or pushy
            
            Return as JSON array: ["subject1", "subject2", ...]
            """
            
            if OPENAI_NEW_API:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.8
                )
                content = response.choices[0].message.content
            else:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.8
                )
                content = response.choices[0].message.content
            subjects = json.loads(content)
            
            return subjects if isinstance(subjects, list) else []
            
        except Exception as e:
            self.logger.error(f"Error generating AI subjects: {e}")
            return []
    
    def optimize_email_length(self, email_content: EmailContent, target_words: int = 150) -> EmailContent:
        """Optimize email length to target word count"""
        current_words = len(email_content.email_body.split())
        
        if current_words <= target_words:
            return email_content
        
        try:
            # Use AI to shorten the email
            prompt = f"""
            Shorten this email to approximately {target_words} words while maintaining:
            - All key personalized insights
            - Professional tone
            - Clear value proposition
            - Call to action
            
            Original email ({current_words} words):
            {email_content.email_body}
            
            Return only the shortened email body.
            """
            
            if OPENAI_NEW_API:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400,
                    temperature=0.3
                )
                shortened_body = response.choices[0].message.content.strip()
            else:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=400,
                    temperature=0.3
                )
                shortened_body = response.choices[0].message.content.strip()
            
            return EmailContent(
                subject_line=email_content.subject_line,
                email_body=shortened_body,
                call_to_action=email_content.call_to_action,
                personalization_score=email_content.personalization_score,
                tone=email_content.tone
            )
            
        except Exception as e:
            self.logger.error(f"Error optimizing email length: {e}")
            return email_content
    
    def validate_email_content(self, email_content: EmailContent) -> Dict[str, Any]:
        """Validate email content quality"""
        validation = {
            'is_valid': True,
            'issues': [],
            'suggestions': [],
            'score': 0.0
        }
        
        # Check subject line
        if len(email_content.subject_line) > 60:
            validation['issues'].append("Subject line too long (>60 characters)")
        elif len(email_content.subject_line) < 10:
            validation['issues'].append("Subject line too short (<10 characters)")
        else:
            validation['score'] += 0.2
        
        # Check email body length
        word_count = len(email_content.email_body.split())
        if word_count > 250:
            validation['issues'].append(f"Email too long ({word_count} words)")
        elif word_count < 50:
            validation['issues'].append(f"Email too short ({word_count} words)")
        else:
            validation['score'] += 0.3
        
        # Check for personalization
        if email_content.personalization_score < 0.3:
            validation['issues'].append("Low personalization score")
            validation['suggestions'].append("Add more specific business insights")
        else:
            validation['score'] += 0.3
        
        # Check for call to action
        if not email_content.call_to_action or len(email_content.call_to_action) < 10:
            validation['issues'].append("Weak or missing call to action")
        else:
            validation['score'] += 0.2
        
        # Overall validation
        validation['is_valid'] = len(validation['issues']) == 0
        validation['score'] = min(validation['score'], 1.0)
        
        return validation
