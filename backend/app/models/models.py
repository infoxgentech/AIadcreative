from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CREATOR = "creator"
    VIEWER = "viewer"

class ContentType(str, enum.Enum):
    SOCIAL_POST = "social_post"
    BANNER_AD = "banner_ad"
    VIDEO_SCRIPT = "video_script"
    EMAIL_CAMPAIGN = "email_campaign"
    BLOG_POST = "blog_post"
    PRODUCT_DESCRIPTION = "product_description"

class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    PUBLISHED = "published"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.CREATOR)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brands = relationship("Brand", back_populates="owner")
    campaigns = relationship("Campaign", back_populates="creator")
    content_pieces = relationship("ContentPiece", back_populates="creator")

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Brand Guidelines
    brand_voice = Column(Text)  # Tone, personality, style
    color_palette = Column(JSON)  # Primary, secondary, accent colors
    typography = Column(JSON)  # Font families, sizes, weights
    logo_urls = Column(JSON)  # Different logo variations
    imagery_style = Column(Text)  # Photography/illustration guidelines
    messaging_pillars = Column(JSON)  # Key brand messages
    target_audience = Column(JSON)  # Demographics, psychographics
    brand_values = Column(JSON)  # Core values and beliefs
    competitors = Column(JSON)  # Competitor analysis
    
    # Content Guidelines
    content_guidelines = Column(JSON)  # Specific content rules
    approved_hashtags = Column(JSON)  # Brand hashtags
    banned_words = Column(JSON)  # Words to avoid
    style_guide_url = Column(String(500))  # External style guide
    
    # Metadata
    industry = Column(String(100))
    website_url = Column(String(500))
    social_media_handles = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="brands")
    campaigns = relationship("Campaign", back_populates="brand")
    content_pieces = relationship("ContentPiece", back_populates="brand")
    reference_materials = relationship("ReferenceMaterial", back_populates="brand")

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Campaign Details
    objective = Column(String(200))  # Campaign goal
    target_audience = Column(JSON)  # Specific audience for this campaign
    budget = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    platforms = Column(JSON)  # Social media platforms, channels
    
    # Content Requirements
    content_types = Column(JSON)  # Types of content needed
    content_count = Column(JSON)  # How many of each type
    content_specs = Column(JSON)  # Size, format requirements
    
    # Campaign Status
    status = Column(String(50), default="planning")
    progress = Column(Float, default=0.0)  # Percentage complete
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="campaigns")
    creator = relationship("User", back_populates="campaigns")
    content_pieces = relationship("ContentPiece", back_populates="campaign")

class ContentPiece(Base):
    __tablename__ = "content_pieces"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content_type = Column(Enum(ContentType), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content Data
    generated_text = Column(Text)
    generated_html = Column(Text)
    image_prompt = Column(Text)  # AI image generation prompt
    image_urls = Column(JSON)  # Generated/uploaded images
    video_script = Column(Text)
    metadata = Column(JSON)  # Additional content metadata
    
    # Generation Details
    ai_model_used = Column(String(100))
    generation_prompt = Column(Text)  # Full prompt sent to AI
    generation_parameters = Column(JSON)  # Model parameters used
    reference_materials_used = Column(JSON)  # Which references were used
    
    # Content Specifications
    platform = Column(String(50))  # Target platform
    dimensions = Column(String(50))  # Image/video dimensions
    duration = Column(Integer)  # Video duration in seconds
    word_count = Column(Integer)
    character_count = Column(Integer)
    
    # Workflow
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    approval_notes = Column(Text)
    revision_count = Column(Integer, default=0)
    
    # Performance (if published)
    engagement_metrics = Column(JSON)
    performance_score = Column(Float)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    published_at = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="content_pieces")
    campaign = relationship("Campaign", back_populates="content_pieces")
    creator = relationship("User", back_populates="content_pieces")

class ReferenceMaterial(Base):
    __tablename__ = "reference_materials"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # File Information
    file_type = Column(String(50))  # image, document, video, url
    file_url = Column(String(500))
    file_size = Column(Integer)
    original_filename = Column(String(255))
    
    # Content Analysis
    extracted_text = Column(Text)  # OCR or document text
    color_analysis = Column(JSON)  # Dominant colors
    style_analysis = Column(JSON)  # Visual style characteristics
    content_tags = Column(JSON)  # Auto-generated tags
    
    # Usage
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    brand = relationship("Brand", back_populates="reference_materials")

class ContentTemplate(Base):
    __tablename__ = "content_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    content_type = Column(Enum(ContentType), nullable=False)
    
    # Template Content
    template_text = Column(Text)
    template_structure = Column(JSON)  # Structured template data
    variables = Column(JSON)  # Placeholder variables
    
    # Usage
    is_global = Column(Boolean, default=False)  # Available to all brands
    brand_id = Column(Integer, ForeignKey("brands.id"))  # Brand-specific template
    usage_count = Column(Integer, default=0)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class GenerationJob(Base):
    __tablename__ = "generation_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    
    # Job Details
    job_type = Column(String(50))  # content_generation, batch_generation, etc.
    input_data = Column(JSON)  # Input parameters
    output_data = Column(JSON)  # Generated results
    
    # Status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)
    error_message = Column(Text)
    
    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Processing Details
    ai_model_used = Column(String(100))
    processing_time = Column(Float)  # Seconds
    tokens_used = Column(Integer)
    cost = Column(Float)