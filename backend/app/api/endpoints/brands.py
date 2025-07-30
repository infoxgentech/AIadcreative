from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.database.database import get_db
from app.api.dependencies.auth import get_current_active_user
from app.models.models import User, Brand

router = APIRouter()

# Pydantic models
class BrandCreate(BaseModel):
    name: str
    description: Optional[str] = None
    industry: Optional[str] = None
    website_url: Optional[str] = None
    brand_voice: Optional[str] = None
    color_palette: Optional[Dict] = None
    typography: Optional[Dict] = None
    logo_urls: Optional[List[str]] = None
    imagery_style: Optional[str] = None
    messaging_pillars: Optional[List[str]] = None
    target_audience: Optional[Dict] = None
    brand_values: Optional[List[str]] = None
    competitors: Optional[List[str]] = None
    content_guidelines: Optional[Dict] = None
    approved_hashtags: Optional[List[str]] = None
    banned_words: Optional[List[str]] = None
    style_guide_url: Optional[str] = None
    social_media_handles: Optional[Dict] = None

class BrandUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    website_url: Optional[str] = None
    brand_voice: Optional[str] = None
    color_palette: Optional[Dict] = None
    typography: Optional[Dict] = None
    logo_urls: Optional[List[str]] = None
    imagery_style: Optional[str] = None
    messaging_pillars: Optional[List[str]] = None
    target_audience: Optional[Dict] = None
    brand_values: Optional[List[str]] = None
    competitors: Optional[List[str]] = None
    content_guidelines: Optional[Dict] = None
    approved_hashtags: Optional[List[str]] = None
    banned_words: Optional[List[str]] = None
    style_guide_url: Optional[str] = None
    social_media_handles: Optional[Dict] = None
    is_active: Optional[bool] = None

class BrandResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    industry: Optional[str]
    website_url: Optional[str]
    brand_voice: Optional[str]
    color_palette: Optional[Dict]
    typography: Optional[Dict]
    logo_urls: Optional[List[str]]
    imagery_style: Optional[str]
    messaging_pillars: Optional[List[str]]
    target_audience: Optional[Dict]
    brand_values: Optional[List[str]]
    competitors: Optional[List[str]]
    content_guidelines: Optional[Dict]
    approved_hashtags: Optional[List[str]]
    banned_words: Optional[List[str]]
    style_guide_url: Optional[str]
    social_media_handles: Optional[Dict]
    is_active: bool
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True

@router.post("/", response_model=BrandResponse)
def create_brand(
    brand: BrandCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new brand"""
    
    # Check if brand name already exists for this user
    existing_brand = db.query(Brand).filter(
        Brand.name == brand.name,
        Brand.owner_id == current_user.id
    ).first()
    
    if existing_brand:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand name already exists"
        )
    
    # Create new brand
    db_brand = Brand(
        name=brand.name,
        description=brand.description,
        owner_id=current_user.id,
        industry=brand.industry,
        website_url=brand.website_url,
        brand_voice=brand.brand_voice,
        color_palette=brand.color_palette,
        typography=brand.typography,
        logo_urls=brand.logo_urls,
        imagery_style=brand.imagery_style,
        messaging_pillars=brand.messaging_pillars,
        target_audience=brand.target_audience,
        brand_values=brand.brand_values,
        competitors=brand.competitors,
        content_guidelines=brand.content_guidelines,
        approved_hashtags=brand.approved_hashtags,
        banned_words=brand.banned_words,
        style_guide_url=brand.style_guide_url,
        social_media_handles=brand.social_media_handles
    )
    
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    
    return db_brand

@router.get("/", response_model=List[BrandResponse])
def list_brands(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all brands for the current user"""
    
    brands = db.query(Brand).filter(
        Brand.owner_id == current_user.id,
        Brand.is_active == True
    ).offset(skip).limit(limit).all()
    
    return brands

@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(
    brand_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific brand"""
    
    brand = db.query(Brand).filter(
        Brand.id == brand_id,
        Brand.owner_id == current_user.id
    ).first()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )
    
    return brand

@router.put("/{brand_id}", response_model=BrandResponse)
def update_brand(
    brand_id: int,
    brand_update: BrandUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a brand"""
    
    brand = db.query(Brand).filter(
        Brand.id == brand_id,
        Brand.owner_id == current_user.id
    ).first()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )
    
    # Check if new name conflicts with existing brands
    if brand_update.name and brand_update.name != brand.name:
        existing_brand = db.query(Brand).filter(
            Brand.name == brand_update.name,
            Brand.owner_id == current_user.id,
            Brand.id != brand_id
        ).first()
        
        if existing_brand:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brand name already exists"
            )
    
    # Update brand fields
    update_data = brand_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(brand, field, value)
    
    db.commit()
    db.refresh(brand)
    
    return brand

@router.delete("/{brand_id}")
def delete_brand(
    brand_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a brand (soft delete)"""
    
    brand = db.query(Brand).filter(
        Brand.id == brand_id,
        Brand.owner_id == current_user.id
    ).first()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )
    
    # Soft delete
    brand.is_active = False
    db.commit()
    
    return {"message": "Brand deleted successfully"}

@router.get("/{brand_id}/analytics")
def get_brand_analytics(
    brand_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a brand"""
    
    brand = db.query(Brand).filter(
        Brand.id == brand_id,
        Brand.owner_id == current_user.id
    ).first()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )
    
    # Get content statistics
    from app.models.models import ContentPiece, Campaign
    
    total_content = db.query(ContentPiece).filter(
        ContentPiece.brand_id == brand_id
    ).count()
    
    total_campaigns = db.query(Campaign).filter(
        Campaign.brand_id == brand_id
    ).count()
    
    # Content by type
    content_by_type = db.query(
        ContentPiece.content_type,
        db.func.count(ContentPiece.id).label('count')
    ).filter(
        ContentPiece.brand_id == brand_id
    ).group_by(ContentPiece.content_type).all()
    
    # Content by status
    content_by_status = db.query(
        ContentPiece.status,
        db.func.count(ContentPiece.id).label('count')
    ).filter(
        ContentPiece.brand_id == brand_id
    ).group_by(ContentPiece.status).all()
    
    return {
        "brand_id": brand_id,
        "brand_name": brand.name,
        "total_content_pieces": total_content,
        "total_campaigns": total_campaigns,
        "content_by_type": [{"type": ct.content_type, "count": ct.count} for ct in content_by_type],
        "content_by_status": [{"status": cs.status, "count": cs.count} for cs in content_by_status]
    }

@router.post("/{brand_id}/duplicate")
def duplicate_brand(
    brand_id: int,
    new_name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Duplicate a brand with a new name"""
    
    original_brand = db.query(Brand).filter(
        Brand.id == brand_id,
        Brand.owner_id == current_user.id
    ).first()
    
    if not original_brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )
    
    # Check if new name already exists
    existing_brand = db.query(Brand).filter(
        Brand.name == new_name,
        Brand.owner_id == current_user.id
    ).first()
    
    if existing_brand:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand name already exists"
        )
    
    # Create duplicate brand
    new_brand = Brand(
        name=new_name,
        description=original_brand.description,
        owner_id=current_user.id,
        industry=original_brand.industry,
        website_url=original_brand.website_url,
        brand_voice=original_brand.brand_voice,
        color_palette=original_brand.color_palette,
        typography=original_brand.typography,
        logo_urls=original_brand.logo_urls,
        imagery_style=original_brand.imagery_style,
        messaging_pillars=original_brand.messaging_pillars,
        target_audience=original_brand.target_audience,
        brand_values=original_brand.brand_values,
        competitors=original_brand.competitors,
        content_guidelines=original_brand.content_guidelines,
        approved_hashtags=original_brand.approved_hashtags,
        banned_words=original_brand.banned_words,
        style_guide_url=original_brand.style_guide_url,
        social_media_handles=original_brand.social_media_handles
    )
    
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    
    return {
        "message": "Brand duplicated successfully",
        "new_brand": new_brand
    }