from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.database.database import get_db
from app.api.dependencies.auth import get_current_active_user
from app.models.models import User, Brand, ContentType, ContentPiece, ContentStatus, Campaign, ReferenceMaterial
from app.services.ai_service import AIContentGenerator, AIProvider

router = APIRouter()

# Initialize AI service
ai_generator = AIContentGenerator()

# Pydantic models
class ContentGenerationRequest(BaseModel):
    brand_id: int
    content_type: ContentType
    brief: str
    platform: Optional[str] = None
    campaign_id: Optional[int] = None
    target_audience: Optional[Dict] = None
    additional_context: Optional[Dict] = None
    reference_material_ids: Optional[List[int]] = None
    preferred_ai_provider: Optional[str] = None

class ContentPieceResponse(BaseModel):
    id: int
    title: str
    content_type: ContentType
    brand_id: int
    campaign_id: Optional[int]
    generated_text: Optional[str]
    generated_html: Optional[str]
    image_prompt: Optional[str]
    image_urls: Optional[List[str]]
    video_script: Optional[str]
    metadata: Optional[Dict]
    ai_model_used: Optional[str]
    platform: Optional[str]
    status: ContentStatus
    created_at: str

    class Config:
        from_attributes = True

class ContentAnalysisRequest(BaseModel):
    content_piece_id: int

class ContentAnalysisResponse(BaseModel):
    overall_score: int
    voice_alignment: int
    values_alignment: int
    guideline_compliance: int
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    brand_consistency: str

class ImagePromptRequest(BaseModel):
    brand_id: int
    content_description: str
    style_preferences: Optional[Dict] = None

@router.post("/generate", response_model=ContentPieceResponse)
async def generate_content(
    request: ContentGenerationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate brand-consistent content using AI"""
    
    # Verify brand ownership
    brand = db.query(Brand).filter(
        Brand.id == request.brand_id,
        Brand.owner_id == current_user.id
    ).first()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found or access denied"
        )
    
    # Verify campaign if provided
    campaign = None
    if request.campaign_id:
        campaign = db.query(Campaign).filter(
            Campaign.id == request.campaign_id,
            Campaign.brand_id == request.brand_id
        ).first()
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
    
    # Get reference materials if provided
    reference_materials = []
    if request.reference_material_ids:
        reference_materials = db.query(ReferenceMaterial).filter(
            ReferenceMaterial.id.in_(request.reference_material_ids),
            ReferenceMaterial.brand_id == request.brand_id
        ).all()
    
    # Determine AI provider
    preferred_provider = None
    if request.preferred_ai_provider:
        try:
            preferred_provider = AIProvider(request.preferred_ai_provider.lower())
        except ValueError:
            pass  # Use default provider selection
    
    # Generate content using AI
    try:
        result = await ai_generator.generate_content(
            brand=brand,
            content_type=request.content_type,
            brief=request.brief,
            platform=request.platform,
            target_audience=request.target_audience,
            reference_materials=reference_materials,
            additional_context=request.additional_context,
            preferred_provider=preferred_provider
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Content generation failed: {result.get('error', 'Unknown error')}"
            )
        
        # Extract content data
        content_data = result["content"]
        
        # Create content piece record
        content_piece = ContentPiece(
            title=f"{request.content_type.value.replace('_', ' ').title()} - {brand.name}",
            content_type=request.content_type,
            brand_id=request.brand_id,
            campaign_id=request.campaign_id,
            creator_id=current_user.id,
            generated_text=content_data.get("raw_content") if not content_data.get("parsed") else None,
            image_prompt=content_data.get("image_prompt"),
            video_script=content_data.get("script"),
            metadata=content_data if content_data.get("parsed") else None,
            ai_model_used=result.get("model_used"),
            generation_prompt=result.get("prompt_used"),
            generation_parameters={"provider": result.get("provider"), "tokens_used": result.get("tokens_used")},
            reference_materials_used=[rm.id for rm in reference_materials],
            platform=request.platform,
            status=ContentStatus.GENERATED
        )
        
        # Set word and character counts if text content is available
        if content_data.get("main_text"):
            content_piece.word_count = len(content_data["main_text"].split())
            content_piece.character_count = len(content_data["main_text"])
        elif content_data.get("raw_content"):
            content_piece.word_count = len(content_data["raw_content"].split())
            content_piece.character_count = len(content_data["raw_content"])
        
        db.add(content_piece)
        db.commit()
        db.refresh(content_piece)
        
        return content_piece
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )

@router.get("/", response_model=List[ContentPieceResponse])
def list_content(
    brand_id: Optional[int] = None,
    campaign_id: Optional[int] = None,
    content_type: Optional[ContentType] = None,
    status: Optional[ContentStatus] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List content pieces with filtering options"""
    
    query = db.query(ContentPiece).filter(ContentPiece.creator_id == current_user.id)
    
    if brand_id:
        # Verify brand ownership
        brand = db.query(Brand).filter(
            Brand.id == brand_id,
            Brand.owner_id == current_user.id
        ).first()
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Brand not found or access denied"
            )
        query = query.filter(ContentPiece.brand_id == brand_id)
    
    if campaign_id:
        query = query.filter(ContentPiece.campaign_id == campaign_id)
    
    if content_type:
        query = query.filter(ContentPiece.content_type == content_type)
    
    if status:
        query = query.filter(ContentPiece.status == status)
    
    content_pieces = query.offset(offset).limit(limit).all()
    return content_pieces

@router.get("/{content_id}", response_model=ContentPieceResponse)
def get_content(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific content piece"""
    
    content_piece = db.query(ContentPiece).filter(
        ContentPiece.id == content_id,
        ContentPiece.creator_id == current_user.id
    ).first()
    
    if not content_piece:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content piece not found"
        )
    
    return content_piece

@router.put("/{content_id}/status")
def update_content_status(
    content_id: int,
    new_status: ContentStatus,
    approval_notes: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update content piece status"""
    
    content_piece = db.query(ContentPiece).filter(
        ContentPiece.id == content_id,
        ContentPiece.creator_id == current_user.id
    ).first()
    
    if not content_piece:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content piece not found"
        )
    
    content_piece.status = new_status
    if approval_notes:
        content_piece.approval_notes = approval_notes
    
    db.commit()
    
    return {"message": "Status updated successfully", "new_status": new_status}

@router.post("/analyze-consistency", response_model=ContentAnalysisResponse)
async def analyze_brand_consistency(
    request: ContentAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze how well content aligns with brand guidelines"""
    
    content_piece = db.query(ContentPiece).filter(
        ContentPiece.id == request.content_piece_id,
        ContentPiece.creator_id == current_user.id
    ).first()
    
    if not content_piece:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content piece not found"
        )
    
    brand = db.query(Brand).filter(Brand.id == content_piece.brand_id).first()
    
    # Get content text for analysis
    content_text = ""
    if content_piece.metadata and isinstance(content_piece.metadata, dict):
        content_text = content_piece.metadata.get("main_text", "")
        if not content_text:
            content_text = str(content_piece.metadata)
    elif content_piece.generated_text:
        content_text = content_piece.generated_text
    
    if not content_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No content text available for analysis"
        )
    
    try:
        analysis_result = await ai_generator.analyze_brand_consistency(
            brand=brand,
            content=content_text,
            content_type=content_piece.content_type
        )
        
        if "error" in analysis_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {analysis_result['error']}"
            )
        
        return ContentAnalysisResponse(**analysis_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/generate-image-prompt")
async def generate_image_prompt(
    request: ImagePromptRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate detailed image prompts based on brand guidelines"""
    
    # Verify brand ownership
    brand = db.query(Brand).filter(
        Brand.id == request.brand_id,
        Brand.owner_id == current_user.id
    ).first()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found or access denied"
        )
    
    try:
        image_prompt = await ai_generator.generate_image_prompt(
            brand=brand,
            content_description=request.content_description,
            style_preferences=request.style_preferences
        )
        
        return {
            "image_prompt": image_prompt,
            "brand_name": brand.name,
            "content_description": request.content_description
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image prompt generation failed: {str(e)}"
        )

@router.delete("/{content_id}")
def delete_content(
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a content piece"""
    
    content_piece = db.query(ContentPiece).filter(
        ContentPiece.id == content_id,
        ContentPiece.creator_id == current_user.id
    ).first()
    
    if not content_piece:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content piece not found"
        )
    
    db.delete(content_piece)
    db.commit()
    
    return {"message": "Content piece deleted successfully"}

@router.get("/providers/available")
def get_available_providers():
    """Get list of available AI providers"""
    return {
        "available_providers": [provider.value for provider in ai_generator.get_available_providers()],
        "provider_details": {
            "claude": {
                "name": "Claude (Anthropic)",
                "available": ai_generator.is_provider_available(AIProvider.CLAUDE)
            },
            "gemini": {
                "name": "Google Gemini",
                "available": ai_generator.is_provider_available(AIProvider.GEMINI)
            }
        }
    }