import anthropic
import json
import re
from typing import Dict, List, Optional, Any
from app.core.config import settings
from app.models.models import Brand, ContentType, ReferenceMaterial
import logging

logger = logging.getLogger(__name__)

class ClaudeContentGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-3-5-sonnet-20241022"
    
    async def generate_content(
        self,
        brand: Brand,
        content_type: ContentType,
        brief: str,
        platform: str = None,
        target_audience: Dict = None,
        reference_materials: List[ReferenceMaterial] = None,
        additional_context: Dict = None
    ) -> Dict[str, Any]:
        """
        Generate brand-consistent content using Claude AI
        """
        try:
            # Build comprehensive prompt
            prompt = self._build_prompt(
                brand=brand,
                content_type=content_type,
                brief=brief,
                platform=platform,
                target_audience=target_audience,
                reference_materials=reference_materials,
                additional_context=additional_context
            )
            
            # Generate content
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse and structure response
            content = self._parse_response(response.content[0].text, content_type)
            
            return {
                "success": True,
                "content": content,
                "model_used": self.model,
                "prompt_used": prompt,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens
            }
            
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def _build_prompt(
        self,
        brand: Brand,
        content_type: ContentType,
        brief: str,
        platform: str = None,
        target_audience: Dict = None,
        reference_materials: List[ReferenceMaterial] = None,
        additional_context: Dict = None
    ) -> str:
        """
        Build a comprehensive prompt for Claude based on brand guidelines and context
        """
        
        # Base prompt structure
        prompt_parts = [
            "You are an expert brand content creator and copywriter. Your task is to generate high-quality, brand-consistent content that perfectly aligns with the provided brand guidelines.",
            "",
            "## BRAND INFORMATION",
        ]
        
        # Add brand details
        prompt_parts.extend([
            f"**Brand Name:** {brand.name}",
            f"**Industry:** {brand.industry or 'Not specified'}",
            f"**Description:** {brand.description or 'Not provided'}",
            ""
        ])
        
        # Brand voice and personality
        if brand.brand_voice:
            prompt_parts.extend([
                "## BRAND VOICE & PERSONALITY",
                brand.brand_voice,
                ""
            ])
        
        # Target audience
        if brand.target_audience or target_audience:
            prompt_parts.append("## TARGET AUDIENCE")
            if target_audience:
                prompt_parts.append(self._format_audience_info(target_audience))
            elif brand.target_audience:
                prompt_parts.append(self._format_audience_info(brand.target_audience))
            prompt_parts.append("")
        
        # Brand values and messaging
        if brand.brand_values:
            prompt_parts.extend([
                "## BRAND VALUES",
                self._format_json_list(brand.brand_values),
                ""
            ])
        
        if brand.messaging_pillars:
            prompt_parts.extend([
                "## KEY MESSAGING PILLARS",
                self._format_json_list(brand.messaging_pillars),
                ""
            ])
        
        # Content guidelines
        if brand.content_guidelines:
            prompt_parts.extend([
                "## CONTENT GUIDELINES",
                self._format_content_guidelines(brand.content_guidelines),
                ""
            ])
        
        # Approved/banned elements
        if brand.approved_hashtags:
            prompt_parts.extend([
                "## APPROVED HASHTAGS",
                ", ".join(brand.approved_hashtags),
                ""
            ])
        
        if brand.banned_words:
            prompt_parts.extend([
                "## WORDS TO AVOID",
                ", ".join(brand.banned_words),
                ""
            ])
        
        # Reference materials context
        if reference_materials:
            prompt_parts.extend([
                "## REFERENCE MATERIALS",
                self._format_reference_materials(reference_materials),
                ""
            ])
        
        # Platform-specific guidelines
        if platform:
            prompt_parts.extend([
                "## PLATFORM SPECIFICATIONS",
                self._get_platform_guidelines(platform, content_type),
                ""
            ])
        
        # Content type specific instructions
        prompt_parts.extend([
            "## CONTENT REQUIREMENTS",
            f"**Content Type:** {content_type.value.replace('_', ' ').title()}",
            f"**Brief:** {brief}",
            ""
        ])
        
        # Add additional context
        if additional_context:
            prompt_parts.extend([
                "## ADDITIONAL CONTEXT",
                self._format_additional_context(additional_context),
                ""
            ])
        
        # Output format instructions
        prompt_parts.extend([
            "## OUTPUT FORMAT",
            self._get_output_format_instructions(content_type),
            "",
            "## REQUIREMENTS",
            "- Ensure ALL content aligns perfectly with the brand voice and guidelines",
            "- Incorporate relevant brand values and messaging pillars naturally",
            "- Avoid any banned words or phrases",
            "- Use approved hashtags where appropriate",
            "- Consider the target audience in tone and messaging",
            "- Follow platform-specific best practices",
            "- Be creative while staying brand-consistent",
            "- Include specific calls-to-action when appropriate",
            "",
            "Generate the content now:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _format_audience_info(self, audience: Dict) -> str:
        """Format target audience information"""
        if isinstance(audience, dict):
            return "\n".join([f"- **{k.title()}:** {v}" for k, v in audience.items()])
        return str(audience)
    
    def _format_json_list(self, data: List) -> str:
        """Format JSON list data for prompt"""
        if isinstance(data, list):
            return "\n".join([f"- {item}" for item in data])
        return str(data)
    
    def _format_content_guidelines(self, guidelines: Dict) -> str:
        """Format content guidelines"""
        if isinstance(guidelines, dict):
            return "\n".join([f"- **{k.title()}:** {v}" for k, v in guidelines.items()])
        return str(guidelines)
    
    def _format_reference_materials(self, materials: List[ReferenceMaterial]) -> str:
        """Format reference materials for context"""
        formatted = []
        for material in materials:
            formatted.append(f"- **{material.name}:** {material.description or 'No description'}")
            if material.extracted_text:
                formatted.append(f"  Content: {material.extracted_text[:500]}...")
            if material.content_tags:
                formatted.append(f"  Tags: {', '.join(material.content_tags)}")
        return "\n".join(formatted)
    
    def _format_additional_context(self, context: Dict) -> str:
        """Format additional context information"""
        return "\n".join([f"- **{k.title()}:** {v}" for k, v in context.items()])
    
    def _get_platform_guidelines(self, platform: str, content_type: ContentType) -> str:
        """Get platform-specific guidelines"""
        guidelines = {
            "instagram": {
                "social_post": "- Optimal length: 125-150 characters\n- Use 3-5 relevant hashtags\n- Include engaging visual description\n- Encourage interaction",
                "banner_ad": "- Square format (1080x1080) or story format (1080x1920)\n- Clear, bold text\n- Strong visual hierarchy\n- Compelling CTA"
            },
            "facebook": {
                "social_post": "- Optimal length: 40-80 characters for engagement\n- Use 1-2 hashtags maximum\n- Include question or call-to-action\n- Visual content performs better",
                "banner_ad": "- Multiple format options\n- Clear value proposition\n- Minimal text on image\n- Strong CTA button"
            },
            "twitter": {
                "social_post": "- Maximum 280 characters\n- Use 1-2 hashtags\n- Include mentions when relevant\n- Encourage retweets and replies",
                "banner_ad": "- Concise messaging\n- Clear CTA\n- Mobile-optimized\n- Video performs well"
            },
            "linkedin": {
                "social_post": "- Professional tone\n- 150-300 characters for best engagement\n- Industry-relevant hashtags\n- Thought leadership angle",
                "banner_ad": "- Professional imagery\n- B2B focused messaging\n- Clear ROI or benefit\n- Professional CTA"
            },
            "tiktok": {
                "social_post": "- Trending hashtags\n- Short, punchy captions\n- Encourage video creation\n- Fun, authentic tone",
                "video_script": "- Hook in first 3 seconds\n- 15-60 seconds optimal\n- Vertical format\n- Trending sounds/effects"
            }
        }
        
        platform_lower = platform.lower()
        content_key = content_type.value
        
        if platform_lower in guidelines and content_key in guidelines[platform_lower]:
            return guidelines[platform_lower][content_key]
        elif platform_lower in guidelines:
            # Return general guidelines for the platform
            return "\n".join(guidelines[platform_lower].values())
        else:
            return f"Create content optimized for {platform}"
    
    def _get_output_format_instructions(self, content_type: ContentType) -> str:
        """Get content type specific output format instructions"""
        formats = {
            ContentType.SOCIAL_POST: """
Provide the output in JSON format:
{
    "main_text": "Primary post content",
    "hashtags": ["#hashtag1", "#hashtag2"],
    "call_to_action": "Specific CTA",
    "image_description": "Description for visual content",
    "alternative_versions": ["Alternative text 1", "Alternative text 2"]
}
""",
            ContentType.BANNER_AD: """
Provide the output in JSON format:
{
    "headline": "Main headline",
    "subheading": "Supporting text",
    "body_text": "Main ad copy",
    "call_to_action": "CTA button text",
    "image_prompt": "Detailed description for image generation",
    "design_notes": "Visual design guidance"
}
""",
            ContentType.VIDEO_SCRIPT: """
Provide the output in JSON format:
{
    "title": "Video title",
    "hook": "Opening hook (first 3-5 seconds)",
    "script": "Full video script with timestamps",
    "key_messages": ["Message 1", "Message 2"],
    "call_to_action": "End CTA",
    "visual_notes": "Visual direction and style notes",
    "duration_estimate": "Estimated duration in seconds"
}
""",
            ContentType.EMAIL_CAMPAIGN: """
Provide the output in JSON format:
{
    "subject_line": "Email subject",
    "preview_text": "Preview/preheader text",
    "headline": "Main email headline",
    "body_text": "Full email content",
    "call_to_action": "Primary CTA",
    "alternative_subject_lines": ["Alt subject 1", "Alt subject 2"]
}
""",
            ContentType.BLOG_POST: """
Provide the output in JSON format:
{
    "title": "Blog post title",
    "meta_description": "SEO meta description",
    "introduction": "Opening paragraph",
    "main_content": "Full blog post content",
    "conclusion": "Closing paragraph",
    "call_to_action": "End CTA",
    "suggested_images": ["Image 1 description", "Image 2 description"],
    "seo_keywords": ["keyword1", "keyword2"]
}
""",
            ContentType.PRODUCT_DESCRIPTION: """
Provide the output in JSON format:
{
    "title": "Product title",
    "short_description": "Brief product summary",
    "detailed_description": "Full product description",
    "key_features": ["Feature 1", "Feature 2"],
    "benefits": ["Benefit 1", "Benefit 2"],
    "call_to_action": "Purchase CTA",
    "seo_keywords": ["keyword1", "keyword2"]
}
"""
        }
        
        return formats.get(content_type, "Provide well-structured, brand-consistent content.")
    
    def _parse_response(self, response_text: str, content_type: ContentType) -> Dict[str, Any]:
        """Parse Claude's response and extract structured content"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                return parsed
            else:
                # Fallback to basic text parsing
                return {
                    "raw_content": response_text,
                    "parsed": False,
                    "content_type": content_type.value
                }
        except json.JSONDecodeError:
            # If JSON parsing fails, return raw content
            return {
                "raw_content": response_text,
                "parsed": False,
                "content_type": content_type.value
            }
    
    async def generate_image_prompt(
        self,
        brand: Brand,
        content_description: str,
        style_preferences: Dict = None
    ) -> str:
        """
        Generate detailed image generation prompts based on brand guidelines
        """
        prompt_parts = [
            "Create a detailed image generation prompt for the following brand and content:",
            f"Brand: {brand.name}",
            f"Content: {content_description}",
        ]
        
        if brand.imagery_style:
            prompt_parts.extend([
                f"Brand imagery style: {brand.imagery_style}",
            ])
        
        if brand.color_palette:
            colors = self._format_color_palette(brand.color_palette)
            prompt_parts.extend([
                f"Brand colors: {colors}",
            ])
        
        if style_preferences:
            prompt_parts.extend([
                f"Style preferences: {style_preferences}",
            ])
        
        prompt_parts.extend([
            "",
            "Generate a detailed, specific prompt for AI image generation that will create a visual that perfectly represents the brand and content. Include style, composition, colors, mood, and technical specifications."
        ])
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.6,
                messages=[{"role": "user", "content": "\n".join(prompt_parts)}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Image prompt generation failed: {str(e)}")
            return f"Create an image for {brand.name} showing {content_description}"
    
    def _format_color_palette(self, colors: Dict) -> str:
        """Format color palette information"""
        if isinstance(colors, dict):
            return ", ".join([f"{k}: {v}" for k, v in colors.items()])
        return str(colors)
    
    async def analyze_brand_consistency(
        self,
        brand: Brand,
        content: str,
        content_type: ContentType
    ) -> Dict[str, Any]:
        """
        Analyze how well content aligns with brand guidelines
        """
        prompt = f"""
Analyze the following content for brand consistency:

BRAND: {brand.name}
BRAND VOICE: {brand.brand_voice or 'Not specified'}
BRAND VALUES: {self._format_json_list(brand.brand_values) if brand.brand_values else 'Not specified'}
CONTENT GUIDELINES: {self._format_content_guidelines(brand.content_guidelines) if brand.content_guidelines else 'Not specified'}

CONTENT TO ANALYZE:
{content}

Provide a detailed analysis in JSON format:
{{
    "overall_score": 85,
    "voice_alignment": 90,
    "values_alignment": 80,
    "guideline_compliance": 85,
    "strengths": ["Specific strength 1", "Specific strength 2"],
    "weaknesses": ["Specific weakness 1", "Specific weakness 2"],
    "suggestions": ["Specific improvement 1", "Specific improvement 2"],
    "brand_consistency": "high/medium/low"
}}
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return self._parse_response(response.content[0].text, content_type)
            
        except Exception as e:
            logger.error(f"Brand consistency analysis failed: {str(e)}")
            return {
                "error": str(e),
                "overall_score": 0
            }