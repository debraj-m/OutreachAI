"""
AI Analyzer Module
==================

Uses AI/LLM to analyze website content and generate insights about 
tech/AI opportunities for personalized email outreach.
"""

try:
    # Try importing the new OpenAI client (v1.0+)
    from openai import OpenAI
    OPENAI_NEW_API = True
except ImportError:
    # Fall back to legacy OpenAI API
    import openai
    OPENAI_NEW_API = False

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .website_analyzer import WebsiteAnalysis
from .prospect_manager import Prospect


@dataclass
class AIInsights:
    """Data class for AI-generated insights"""
    opportunities: List[str]
    pain_points: List[str]
    recommendations: List[str]
    industry_trends: List[str]
    competitive_gaps: List[str]
    roi_potential: str
    implementation_complexity: str
    
    def __post_init__(self):
        """Initialize empty lists if None"""
        if self.opportunities is None:
            self.opportunities = []
        if self.pain_points is None:
            self.pain_points = []
        if self.recommendations is None:
            self.recommendations = []
        if self.industry_trends is None:
            self.industry_trends = []
        if self.competitive_gaps is None:
            self.competitive_gaps = []


class AIAnalyzer:
    """AI-powered analyzer for generating business insights and opportunities"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", 
                 max_tokens: int = 1000, temperature: float = 0.7,
                 logger: Optional[logging.Logger] = None):
        """
        Initialize AI Analyzer
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
            max_tokens: Maximum tokens for response
            temperature: Response creativity (0.0-1.0)
            logger: Logger instance
        """
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize OpenAI client based on version
        if OPENAI_NEW_API:
            self.client = OpenAI(api_key=self.api_key)
        else:
            openai.api_key = self.api_key
        
        # Industry-specific prompts with business-critical focus areas
        self.industry_contexts = {
            'ecommerce': {
                'revenue_leaks': ['cart abandonment without recovery', 'poor product search', 'missing upsell automation', 'slow checkout process'],
                'competitive_gaps': ['no product recommendations', 'limited payment options', 'no inventory alerts', 'poor mobile checkout'],
                'scaling_bottlenecks': ['manual inventory management', 'no customer segmentation', 'basic analytics', 'limited integrations'],
                'efficiency_gains': ['automated reorder notifications', 'dynamic pricing', 'inventory forecasting', 'customer service automation']
            },
            'saas': {
                'revenue_leaks': ['poor onboarding conversion', 'high trial-to-paid dropout', 'no usage-based upselling', 'customer churn'],
                'competitive_gaps': ['no in-app guidance', 'limited integrations', 'poor feature discovery', 'basic analytics'],
                'scaling_bottlenecks': ['manual user onboarding', 'no automated workflows', 'limited customer success tracking'],
                'efficiency_gains': ['automated user journeys', 'usage analytics', 'churn prediction', 'feature adoption tracking']
            },
            'consulting': {
                'revenue_leaks': ['no lead scoring', 'poor proposal automation', 'missing case studies', 'weak authority positioning'],
                'competitive_gaps': ['no thought leadership content', 'basic contact process', 'no client portal', 'limited social proof'],
                'scaling_bottlenecks': ['manual proposal creation', 'no knowledge management', 'time tracking inefficiencies'],
                'efficiency_gains': ['automated lead qualification', 'proposal templates', 'client communication systems', 'project tracking']
            },
            'agency': {
                'revenue_leaks': ['no retainer automation', 'poor project scoping', 'missing upsell opportunities', 'client churn'],
                'competitive_gaps': ['no automated reporting', 'limited client self-service', 'basic project visibility'],
                'scaling_bottlenecks': ['manual reporting', 'poor resource planning', 'scattered project data'],
                'efficiency_gains': ['automated client reporting', 'resource management', 'project profitability tracking']
            },
            'healthcare': {
                'revenue_leaks': ['appointment no-shows', 'poor online booking', 'missing patient communications', 'inefficient scheduling'],
                'competitive_gaps': ['no patient portal', 'limited online presence', 'poor patient experience'],
                'scaling_bottlenecks': ['manual appointment management', 'paper-based processes', 'poor patient flow'],
                'efficiency_gains': ['automated appointment reminders', 'online scheduling', 'patient communication systems']
            },
            'restaurant': {
                'revenue_leaks': ['no online ordering', 'poor table management', 'missing loyalty program', 'delivery inefficiencies'],
                'competitive_gaps': ['limited online presence', 'no reservation system', 'poor customer data collection'],
                'scaling_bottlenecks': ['manual order management', 'poor inventory tracking', 'limited customer insights'],
                'efficiency_gains': ['online ordering system', 'table management software', 'inventory automation', 'customer loyalty tracking']
            },
            'real_estate': {
                'revenue_leaks': ['poor lead qualification', 'missing virtual tours', 'weak follow-up systems', 'limited market reach'],
                'competitive_gaps': ['basic property listings', 'no lead automation', 'poor client communication'],
                'scaling_bottlenecks': ['manual lead tracking', 'paper-based processes', 'limited market analysis'],
                'efficiency_gains': ['CRM automation', 'virtual tour integration', 'market analytics', 'automated follow-up']
            },
            'education': {
                'revenue_leaks': ['poor student retention', 'limited online offerings', 'manual enrollment', 'weak student engagement'],
                'competitive_gaps': ['no online learning platform', 'basic student tracking', 'limited digital content'],
                'scaling_bottlenecks': ['manual grading', 'poor progress tracking', 'limited communication tools'],
                'efficiency_gains': ['learning management system', 'automated progress tracking', 'student engagement tools']
            },
            'finance': {
                'revenue_leaks': ['slow client onboarding', 'manual compliance', 'poor client experience', 'limited service automation'],
                'competitive_gaps': ['no client portal', 'manual reporting', 'basic document management'],
                'scaling_bottlenecks': ['manual processes', 'paper-based workflows', 'limited client self-service'],
                'efficiency_gains': ['automated onboarding', 'digital document management', 'compliance automation', 'client portal']
            },
            'manufacturing': {
                'revenue_leaks': ['poor supply chain visibility', 'quality control issues', 'inventory inefficiencies', 'production bottlenecks'],
                'competitive_gaps': ['manual tracking systems', 'limited automation', 'poor data visibility'],
                'scaling_bottlenecks': ['manual processes', 'poor production planning', 'reactive maintenance'],
                'efficiency_gains': ['supply chain automation', 'predictive maintenance', 'quality tracking systems', 'production optimization']
            }
        }
    
    def analyze_opportunities(self, website_analysis: WebsiteAnalysis, 
                            prospect: Prospect) -> Optional[AIInsights]:
        """
        Analyze website and generate AI-powered insights
        
        Args:
            website_analysis: Website analysis results
            prospect: Prospect information
            
        Returns:
            AIInsights object or None if analysis failed
        """
        try:
            self.logger.info(f"Generating AI insights for {prospect.company_name}")
            
            # Create comprehensive prompt
            prompt = self._create_analysis_prompt(website_analysis, prospect)
            
            # Call OpenAI API
            if OPENAI_NEW_API:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": self._get_system_prompt()
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                response_content = response.choices[0].message.content
            else:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": self._get_system_prompt()
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                response_content = response.choices[0].message.content
            insights = self._parse_ai_response(response_content)
            
            if insights:
                self.logger.info(f"Generated {len(insights.opportunities)} opportunities for {prospect.company_name}")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating AI insights: {e}")
            return None
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI analysis"""
        return """You are a technical freelance consultant who specializes in identifying both technical optimization opportunities and business growth potential through website analysis.

        Your expertise combines TECHNICAL EXCELLENCE with BUSINESS IMPACT:
        - Revenue optimization: Converting visitors through technical improvements (A/B testing, performance optimization)
        - Cost reduction: Implementing modern tech stack and automation (Cloud solutions, API integrations)
        - Competitive advantages: Building advanced technical features (AI integration, custom algorithms)
        - Customer retention: Developing data-driven engagement systems (Analytics, personalization)
        - Market expansion: Creating scalable technical architecture (Microservices, cloud infrastructure)
        - Process efficiency: Engineering automated workflows (API development, system integration)
        
        CRITICAL ANALYSIS APPROACH:
        1. **Find technical revenue leaks** - Which technical issues are causing revenue loss?
           - Slow page load impacting conversions
           - Poor API integrations affecting sales
           - Outdated tech stack limiting capabilities
        
        2. **Identify technical competitive gaps** - What modern solutions give competitors an edge?
           - AI/ML implementation opportunities
           - Advanced automation possibilities
           - Modern tech stack advantages
           - AI innovations that can be added in their website 
           - Missing advanced features 
           - Improvements from Technical Point of View

        3. **Spot technical efficiency gaps** - Which processes need automation/optimization?
           - Manual data processing bottlenecks
           - Integration opportunities
           - Performance optimization needs
        
        4. **Calculate technical ROI** - What's the business impact of technical improvements?
           - Performance optimization gains
           - Automation time savings
           - Infrastructure cost reduction
        
        5. **Find technical scaling barriers** - What technical limitations prevent growth?
           - Architecture scalability issues
           - Technical debt impact
           - Infrastructure limitations
        
        AVOID these generic suggestions:
        - "Add a contact form" (instead, suggest specific conversion optimization with A/B testing)
        - "Improve SEO" (instead, propose technical SEO architecture improvements)
        - "Add AI chatbot" (instead, recommend specific AI use cases with ROI calculations)
        - "Mobile optimization" (instead, suggest progressive web app conversion with metrics)
        
        INSTEAD, FOCUS ON:
        - Technical implementations that drive business results:
          * API-driven automation opportunities with clear ROI
          * Performance optimizations with conversion impact
          * Modern tech stack upgrades with competitive advantages
          * Data architecture improvements for better insights
          * Scalable solutions for growth readiness
          * Custom development opportunities with unique value
        
        Make every technical suggestion demonstrate both implementation expertise AND business impact:
        - Technical Aspect: How you'll implement it (specific technologies/methods)
        - Business Impact: Quantifiable outcomes (revenue, costs, efficiency)
        - Competitive Edge: Why it's better than generic solutions
        - ROI Timeline: When they'll see results from the implementation"""
    
    def _create_analysis_prompt(self, website_analysis: WebsiteAnalysis, 
                               prospect: Prospect) -> str:
        """Create detailed analysis prompt"""
        
        # Get industry context
        industry_context = self.industry_contexts.get(
            website_analysis.business_category, 
            self.industry_contexts.get('consulting', {})
        )
        
        # Create dynamic analysis based on website findings
        tech_gaps_analysis = self._analyze_tech_gaps(website_analysis)
        seo_opportunities = self._analyze_seo_opportunities(website_analysis)
        ux_improvements = self._analyze_ux_opportunities(website_analysis)
        
        prompt = f"""
        You are analyzing {prospect.company_name} ({website_analysis.business_category}) for a business consultant who needs to identify SPECIFIC revenue opportunities and competitive gaps.
        
        COMPANY CONTEXT:
        - Company: {prospect.company_name}
        - Industry: {website_analysis.business_category}
        - Decision Maker: {prospect.first_name} {prospect.last_name}, {prospect.job_position}
        - Market: {prospect.country}
        - Website: {website_analysis.url}
        
        WEBSITE INTELLIGENCE:
        - Current Tech: {', '.join(website_analysis.tech_stack)}
        - Business Model Indicators: {website_analysis.business_category}
        - Contact Options: {'Contact form available' if website_analysis.has_contact_form else 'No contact form - potential lead loss'}
        - Mobile Experience: {'Optimized' if website_analysis.mobile_responsive else 'Not mobile-optimized - losing mobile customers'}
        - Content Strategy: {'Has blog/content' if website_analysis.has_blog else 'No content marketing presence'}
        - E-commerce: {'E-commerce enabled' if website_analysis.has_ecommerce else 'No e-commerce functionality'}
        - Performance: {website_analysis.page_load_time:.1f}s load time
        
        BUSINESS CONTENT ANALYSIS:
        {website_analysis.content_text[:1000]}
        
        INDUSTRY-SPECIFIC BUSINESS INTELLIGENCE:
        Common revenue leaks in {website_analysis.business_category}: {industry_context.get('revenue_leaks', [])}
        Typical competitive gaps: {industry_context.get('competitive_gaps', [])}
        Scaling bottlenecks: {industry_context.get('scaling_bottlenecks', [])}
        Efficiency opportunities: {industry_context.get('efficiency_gains', [])}
        
        CRITICAL ANALYSIS REQUIRED:
        Based on this specific business, identify opportunities in technical implementations that would make the business owner think "This person really understands my business challenges."
        
        Focus on these high-impact areas:
        
        1. **REVENUE LEAKS** - What potential customers/money are they losing?
           - Missing conversion optimization points
           - Customer segments they're not capturing
           - Pricing or sales process gaps
           
        2. **COMPETITIVE DISADVANTAGES** - What do competitors have that they don't?
           - Industry-standard features they lack
           - Technology gaps that hurt competitiveness
           - Market positioning weaknesses
           
        3. **OPERATIONAL BOTTLENECKS** - What manual processes are costing time/money?
           - Workflow inefficiencies you can spot
           - Automation opportunities
           - Resource allocation issues
           
        4. **SCALING LIMITATIONS** - What prevents growth?
           - Infrastructure that won't scale
           - Process limitations
           - Market expansion barriers
           
        5. **CUSTOMER EXPERIENCE GAPS** - Where are they losing customers?
           - User journey friction points
           - Communication gaps
           - Service delivery issues
        
        ANALYSIS INSTRUCTIONS:
        - Be SPECIFIC to their business model and industry
        - Focus on measurable business impact (revenue, cost savings, efficiency)
        - Avoid generic web development suggestions
        - Think like a business consultant, not a web developer
        - Identify opportunities worth $10k+ in value annually
        - Consider their specific market position and competitors
        
        Return JSON with specific, business-focused insights:
        {{
            "opportunities": [
                "Specific revenue opportunity unique to their business model",
                "Competitive advantage they could gain in their market",
                "Operational efficiency that would save significant time/money"
            ],
            "pain_points": [
                "Business-critical challenge affecting their bottom line",
                "Competitive weakness hurting their market position",
                "Technical limitation preventing growth",
                "Missing advanced features",
                "Improvements from Technical Point of View"
            ],
            "recommendations": [
                "High-impact solution with clear ROI calculation",
                "Strategic improvement that addresses core business need"
            ],
            "industry_trends": [
                "Market trend creating urgency for this business",
                "Technology shift affecting their competitive position"
            ],
            "competitive_gaps": [
                "Specific feature/capability their competitors have",
                "Market positioning weakness compared to industry leaders"
            ],
            "roi_potential": "High/Medium/Low - with specific dollar impact estimate",
            "implementation_complexity": "Low/Medium/High - with realistic timeline and resources needed"
        }}
        
        Each insight should be so specific to their business that they'll think "How did they know that about our industry/challenges?"
        """
        
        return prompt
    
    def _analyze_tech_gaps(self, website_analysis: WebsiteAnalysis) -> str:
        """Analyze technical gaps in the website"""
        gaps = []
        
        # Performance issues
        if website_analysis.page_load_time > 3.0:
            gaps.append(f"Slow page load time ({website_analysis.page_load_time:.1f}s) - affecting user experience and SEO")
        
        # Mobile responsiveness
        if not website_analysis.mobile_responsive:
            gaps.append("Website not optimized for mobile devices - missing significant mobile traffic")
        
        # Missing features based on business type
        if not website_analysis.has_contact_form:
            gaps.append("No contact form - potential lead loss from interested visitors")
        
        if not website_analysis.has_blog and website_analysis.business_category in ['consulting', 'agency', 'saas']:
            gaps.append("No blog/content section - missing SEO and thought leadership opportunities")
        
        # SEO issues
        if website_analysis.seo_issues:
            gaps.extend([f"SEO issue: {issue}" for issue in website_analysis.seo_issues[:3]])
        
        # Tech stack modernization
        if 'jquery' in str(website_analysis.tech_stack).lower() and 'react' not in str(website_analysis.tech_stack).lower():
            gaps.append("Outdated JavaScript framework - potential for modernization")
        
        return '\n'.join([f"- {gap}" for gap in gaps[:5]]) if gaps else "- No major technical gaps identified"
    
    def _analyze_seo_opportunities(self, website_analysis: WebsiteAnalysis) -> str:
        """Analyze SEO and marketing opportunities"""
        opportunities = []
        
        # Content opportunities
        if not website_analysis.has_blog:
            opportunities.append("Content marketing potential - no current blog or resource section")
        
        # Meta optimization
        if not website_analysis.meta_description or len(website_analysis.meta_description) < 120:
            opportunities.append("Meta description optimization needed for better search visibility")
        
        # Structured data
        if 'schema' not in str(website_analysis.tech_stack).lower():
            opportunities.append("Missing structured data markup - opportunity for rich snippets")
        
        # Local SEO (if applicable)
        if website_analysis.business_category in ['restaurant', 'healthcare', 'real_estate']:
            opportunities.append("Local SEO optimization potential for location-based searches")
        
        return '\n'.join([f"- {opp}" for opp in opportunities[:4]]) if opportunities else "- Standard SEO practices appear to be in place"
    
    def _analyze_ux_opportunities(self, website_analysis: WebsiteAnalysis) -> str:
        """Analyze user experience improvement opportunities"""
        improvements = []
        
        # Navigation and structure
        if len(website_analysis.headings) < 3:
            improvements.append("Poor content hierarchy - needs better heading structure for readability")
        
        # Conversion optimization
        if not website_analysis.has_contact_form and website_analysis.business_category in ['consulting', 'agency', 'saas']:
            improvements.append("Missing clear conversion paths - no lead capture mechanisms")
        
        # Accessibility
        if website_analysis.accessibility_issues:
            improvements.extend([f"Accessibility improvement: {issue}" for issue in website_analysis.accessibility_issues[:2]])
        
        # Industry-specific UX
        if website_analysis.business_category == 'ecommerce' and not website_analysis.has_ecommerce:
            improvements.append("E-commerce functionality missing despite business model")
        
        return '\n'.join([f"- {imp}" for imp in improvements[:4]]) if improvements else "- User experience appears well-structured"
    
    def _parse_ai_response(self, response_content: str) -> Optional[AIInsights]:
        """Parse AI response into structured insights"""
        try:
            # Try to parse as JSON first
            if response_content.strip().startswith('{'):
                data = json.loads(response_content)
            else:
                # If not JSON, try to extract JSON from text
                json_start = response_content.find('{')
                json_end = response_content.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = response_content[json_start:json_end]
                    data = json.loads(json_str)
                else:
                    # Fallback: parse as text
                    data = self._parse_text_response(response_content)
            
            return AIInsights(
                opportunities=data.get('opportunities', []),
                pain_points=data.get('pain_points', []),
                recommendations=data.get('recommendations', []),
                industry_trends=data.get('industry_trends', []),
                competitive_gaps=data.get('competitive_gaps', []),
                roi_potential=data.get('roi_potential', 'Medium'),
                implementation_complexity=data.get('implementation_complexity', 'Medium')
            )
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            # Try text parsing as fallback
            return self._parse_text_response(response_content)
        
        except Exception as e:
            self.logger.error(f"Error parsing AI response: {e}")
            return None
    
    def _parse_text_response(self, text: str) -> AIInsights:
        """Parse text response as fallback"""
        lines = text.split('\n')
        
        opportunities = []
        pain_points = []
        recommendations = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect sections
            if 'opportunit' in line.lower():
                current_section = 'opportunities'
            elif 'pain' in line.lower() or 'challenge' in line.lower():
                current_section = 'pain_points'
            elif 'recommend' in line.lower():
                current_section = 'recommendations'
            elif line.startswith(('-', '*', '•')) or line[0].isdigit():
                # This is a list item
                item = line.lstrip('-*•0123456789. ').strip()
                if current_section == 'opportunities':
                    opportunities.append(item)
                elif current_section == 'pain_points':
                    pain_points.append(item)
                elif current_section == 'recommendations':
                    recommendations.append(item)
        
        return AIInsights(
            opportunities=opportunities,
            pain_points=pain_points,
            recommendations=recommendations,
            industry_trends=[],
            competitive_gaps=[],
            roi_potential="Medium",
            implementation_complexity="Medium"
        )
    
    def generate_personalization_data(self, insights: AIInsights, 
                                    prospect: Prospect) -> Dict[str, Any]:
        """
        Generate personalization data for email templates
        
        Args:
            insights: AI insights
            prospect: Prospect information
            
        Returns:
            Dictionary with personalization data
        """
        # Categorize and prioritize opportunities
        categorized_opps = self._categorize_insights_for_email(insights)
        
        # Select the most compelling opportunity based on business impact
        primary_opportunity = self._select_primary_opportunity(categorized_opps, insights)
        secondary_opportunities = [opp for opp in insights.opportunities[:3] if opp != primary_opportunity]
        
        # Select most relevant pain point
        primary_pain_point = self._select_primary_pain_point(insights.pain_points, categorized_opps)
        
        # Create diverse talking points
        talking_points = self._generate_talking_points(insights, categorized_opps)
        
        # Determine urgency and priority
        urgency_level = self._assess_urgency(insights)
        
        return {
            'prospect_name': prospect.first_name,
            'company_name': prospect.company_name,
            'job_position': prospect.job_position,
            'primary_opportunity': primary_opportunity,
            'secondary_opportunities': secondary_opportunities[:2],
            'primary_pain_point': primary_pain_point,
            'roi_potential': insights.roi_potential,
            'implementation_complexity': insights.implementation_complexity,
            'talking_points': talking_points,
            'urgency_level': urgency_level,
            'industry_trend': insights.industry_trends[0] if insights.industry_trends else "",
            'competitive_advantage': insights.competitive_gaps[0] if insights.competitive_gaps else "",
            'opportunity_category': categorized_opps['primary_category'],
            'solution_type': categorized_opps['solution_type']
        }
    
    def _categorize_insights_for_email(self, insights: AIInsights) -> Dict[str, Any]:
        """Categorize insights for better email personalization"""
        categories = {
            'technical': [],
            'marketing': [],
            'automation': [],
            'ux': [],
            'analytics': [],
            'integration': []
        }
        
        for opp in insights.opportunities:
            opp_lower = opp.lower()
            if any(term in opp_lower for term in ['performance', 'speed', 'technical', 'optimization', 'infrastructure']):
                categories['technical'].append(opp)
            elif any(term in opp_lower for term in ['seo', 'content', 'marketing', 'search', 'visibility']):
                categories['marketing'].append(opp)
            elif any(term in opp_lower for term in ['automation', 'workflow', 'process', 'manual']):
                categories['automation'].append(opp)
            elif any(term in opp_lower for term in ['ux', 'user experience', 'design', 'conversion', 'navigation']):
                categories['ux'].append(opp)
            elif any(term in opp_lower for term in ['analytics', 'tracking', 'data', 'insights', 'reporting']):
                categories['analytics'].append(opp)
            else:
                categories['integration'].append(opp)
        
        # Determine primary category
        primary_category = max(categories.keys(), key=lambda k: len(categories[k]))
        
        # Determine solution type
        solution_types = {
            'technical': 'Performance Optimization',
            'marketing': 'Digital Marketing Enhancement',
            'automation': 'Process Automation',
            'ux': 'User Experience Improvement',
            'analytics': 'Data & Analytics Setup',
            'integration': 'System Integration'
        }
        
        return {
            'categories': categories,
            'primary_category': primary_category,
            'solution_type': solution_types.get(primary_category, 'Technology Modernization')
        }
    
    def _select_primary_opportunity(self, categorized_opps: Dict[str, Any], insights: AIInsights) -> str:
        """Select the most compelling opportunity for email focus"""
        primary_category = categorized_opps['primary_category']
        category_opportunities = categorized_opps['categories'][primary_category]
        
        if category_opportunities:
            # Return the first opportunity from the primary category
            return category_opportunities[0]
        elif insights.opportunities:
            # Fallback to first opportunity
            return insights.opportunities[0]
        else:
            # Ultimate fallback
            return "website optimization and modernization"
    
    def _select_primary_pain_point(self, pain_points: List[str], categorized_opps: Dict[str, Any]) -> str:
        """Select the most relevant pain point"""
        if not pain_points:
            return "operational efficiency challenges"
        
        # Try to match pain point with opportunity category
        primary_category = categorized_opps['primary_category']
        
        for pain in pain_points:
            pain_lower = pain.lower()
            if primary_category == 'technical' and any(term in pain_lower for term in ['speed', 'performance', 'technical']):
                return pain
            elif primary_category == 'marketing' and any(term in pain_lower for term in ['visibility', 'traffic', 'leads']):
                return pain
            elif primary_category == 'automation' and any(term in pain_lower for term in ['manual', 'time', 'efficiency']):
                return pain
        
        # Return first pain point if no match
        return pain_points[0]
    
    def _generate_talking_points(self, insights: AIInsights, categorized_opps: Dict[str, Any]) -> List[str]:
        """Generate diverse talking points for email"""
        talking_points = []
        
        # Add category-specific talking points
        primary_category = categorized_opps['primary_category']
        
        if primary_category == 'technical':
            talking_points.append("Optimize website performance and technical infrastructure")
        elif primary_category == 'marketing':
            talking_points.append("Enhance digital marketing and search visibility")
        elif primary_category == 'automation':
            talking_points.append("Automate manual processes and improve efficiency")
        elif primary_category == 'ux':
            talking_points.append("Improve user experience and conversion rates")
        elif primary_category == 'analytics':
            talking_points.append("Implement data tracking and business insights")
        else:
            talking_points.append("Modernize technology stack and integrations")
        
        # Add pain point addressing
        if insights.pain_points:
            talking_points.append(f"Address {insights.pain_points[0].lower()}")
        
        return talking_points[:3]  # Keep it concise
    
    def _assess_urgency(self, insights: AIInsights) -> str:
        """Assess urgency level based on insights"""
        high_urgency_indicators = ['security', 'compliance', 'performance', 'competitive', 'outdated']
        
        all_text = ' '.join(insights.opportunities + insights.pain_points + insights.competitive_gaps).lower()
        
        urgency_score = sum(1 for indicator in high_urgency_indicators if indicator in all_text)
        
        if urgency_score >= 3:
            return "high"
        elif urgency_score >= 1:
            return "medium"
        else:
            return "low"
    
    def validate_insights(self, insights: AIInsights) -> bool:
        """Validate that insights contain meaningful and diverse content"""
        if not insights:
            return False
        
        # Check if we have at least one substantial opportunity
        if not insights.opportunities or not any(len(opp.strip()) > 15 for opp in insights.opportunities):
            return False
        
        # Check for diversity - avoid repetitive AI chatbot suggestions
        opportunities_text = ' '.join(insights.opportunities[:3]).lower()
        
        # Red flags for overly generic or repetitive content
        generic_flags = [
            'ai chatbot', 'customer engagement', 'customer service chatbot',
            'ai-powered chatbot', 'chatbot integration'
        ]
        
        # If more than 60% of opportunities mention the same generic concept, reject
        flag_mentions = sum(1 for flag in generic_flags if flag in opportunities_text)
        if flag_mentions > 1:  # More than one generic mention
            self.logger.warning("Insights too focused on generic AI chatbot solutions - regenerating")
            return False
        
        # Check for specific, actionable terms that indicate quality insights
        quality_indicators = [
            'implement', 'develop', 'create', 'build', 'integrate', 'deploy', 
            'design', 'customize', 'optimize', 'automate', 'track', 'analyze',
            'performance', 'seo', 'conversion', 'workflow', 'dashboard',
            'system', 'platform', 'tool', 'solution'
        ]
        
        # Count quality indicators in opportunities
        quality_score = sum(1 for indicator in quality_indicators 
                          if indicator in opportunities_text)
        
        # We want at least 2 quality indicators for good insights
        if quality_score < 2:
            self.logger.warning("Insights lack specific technical detail - regenerating")
            return False
        
        # Check for variety in opportunity types
        opportunity_types = self._classify_opportunity_types(insights.opportunities[:3])
        if len(set(opportunity_types)) < 2:  # Want at least 2 different types
            self.logger.warning("Insights lack variety in solution types - regenerating")
            return False
        
        return True
    
    def _classify_opportunity_types(self, opportunities: List[str]) -> List[str]:
        """Classify opportunities into types for diversity checking"""
        types = []
        
        for opp in opportunities:
            opp_lower = opp.lower()
            if any(term in opp_lower for term in ['chatbot', 'ai chat', 'conversation']):
                types.append('chatbot')
            elif any(term in opp_lower for term in ['seo', 'search', 'content', 'marketing']):
                types.append('marketing')
            elif any(term in opp_lower for term in ['performance', 'speed', 'optimization', 'load']):
                types.append('performance')
            elif any(term in opp_lower for term in ['automation', 'workflow', 'process']):
                types.append('automation')
            elif any(term in opp_lower for term in ['analytics', 'tracking', 'data', 'insights']):
                types.append('analytics')
            elif any(term in opp_lower for term in ['design', 'ux', 'user experience', 'conversion']):
                types.append('ux')
            elif any(term in opp_lower for term in ['integration', 'api', 'system', 'platform']):
                types.append('integration')
            else:
                types.append('general')
        
        return types
    
    def get_insights_summary(self, insights: AIInsights) -> Dict[str, Any]:
        """Get summary of insights for logging/reporting"""
        return {
            'opportunities_count': len(insights.opportunities),
            'pain_points_count': len(insights.pain_points),
            'recommendations_count': len(insights.recommendations),
            'roi_potential': insights.roi_potential,
            'complexity': insights.implementation_complexity,
            'top_opportunity': insights.opportunities[0] if insights.opportunities else None
        }
