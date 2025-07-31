from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from app.database.database import get_db
from app.api.dependencies.auth import get_current_active_user
from app.models.models import User, Brand, Campaign

router = APIRouter()

# Pydantic models
class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    brand_id: int
    objective: Optional[str] = None
    target_audience: Optional[Dict] = None
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    platforms: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    content_count: Optional[Dict] = None
    content_specs: Optional[Dict] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    objective: Optional[str] = None
    target_audience: Optional[Dict] = None
    budget: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    platforms: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    content_count: Optional[Dict] = None
    content_specs: Optional[Dict] = None
    status: Optional[str] = None
    progress: Optional[float] = None
    is_active: Optional[bool] = None

class CampaignResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    brand_id: int
    creator_id: int
    objective: Optional[str]
    target_audience: Optional[Dict]
    budget: Optional[float]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    platforms: Optional[List[str]]
    content_types: Optional[List[str]]
    content_count: Optional[Dict]
    content_specs: Optional[Dict]
    status: str
    progress: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

@router.post("/", response_model=CampaignResponse)
def create_campaign(
    campaign: CampaignCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new campaign"""
    
    # Verify brand ownership
    brand = db.query(Brand).filter(
        Brand.id == campaign.brand_id,
        Brand.owner_id == current_user.id
    ).first()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found or access denied"
        )
    
    # Check if campaign name already exists for this brand
    existing_campaign = db.query(Campaign).filter(
        Campaign.name == campaign.name,
        Campaign.brand_id == campaign.brand_id
    ).first()
    
    if existing_campaign:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign name already exists for this brand"
        )
    
    # Create new campaign
    db_campaign = Campaign(
        name=campaign.name,
        description=campaign.description,
        brand_id=campaign.brand_id,
        creator_id=current_user.id,
        objective=campaign.objective,
        target_audience=campaign.target_audience,
        budget=campaign.budget,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        platforms=campaign.platforms,
        content_types=campaign.content_types,
        content_count=campaign.content_count,
        content_specs=campaign.content_specs
    )
    
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    
    return db_campaign

@router.get("/", response_model=List[CampaignResponse])
def list_campaigns(
    brand_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List campaigns with optional filtering"""
    
    query = db.query(Campaign).filter(Campaign.creator_id == current_user.id)
    
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
        query = query.filter(Campaign.brand_id == brand_id)
    
    if status:
        query = query.filter(Campaign.status == status)
    
    campaigns = query.filter(Campaign.is_active == True).offset(skip).limit(limit).all()
    return campaigns

@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific campaign"""
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.creator_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return campaign

@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: int,
    campaign_update: CampaignUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a campaign"""
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.creator_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if new name conflicts with existing campaigns in the same brand
    if campaign_update.name and campaign_update.name != campaign.name:
        existing_campaign = db.query(Campaign).filter(
            Campaign.name == campaign_update.name,
            Campaign.brand_id == campaign.brand_id,
            Campaign.id != campaign_id
        ).first()
        
        if existing_campaign:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign name already exists for this brand"
            )
    
    # Update campaign fields
    update_data = campaign_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(campaign, field, value)
    
    db.commit()
    db.refresh(campaign)
    
    return campaign

@router.delete("/{campaign_id}")
def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a campaign (soft delete)"""
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.creator_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Soft delete
    campaign.is_active = False
    db.commit()
    
    return {"message": "Campaign deleted successfully"}

@router.get("/{campaign_id}/content")
def get_campaign_content(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all content pieces for a campaign"""
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.creator_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    from app.models.models import ContentPiece
    
    content_pieces = db.query(ContentPiece).filter(
        ContentPiece.campaign_id == campaign_id
    ).all()
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "content_pieces": content_pieces,
        "total_content": len(content_pieces)
    }

@router.get("/{campaign_id}/analytics")
def get_campaign_analytics(
    campaign_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a campaign"""
    
    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.creator_id == current_user.id
    ).first()
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    from app.models.models import ContentPiece
    
    # Get content statistics
    total_content = db.query(ContentPiece).filter(
        ContentPiece.campaign_id == campaign_id
    ).count()
    
    # Content by type
    content_by_type = db.query(
        ContentPiece.content_type,
        db.func.count(ContentPiece.id).label('count')
    ).filter(
        ContentPiece.campaign_id == campaign_id
    ).group_by(ContentPiece.content_type).all()
    
    # Content by status
    content_by_status = db.query(
        ContentPiece.status,
        db.func.count(ContentPiece.id).label('count')
    ).filter(
        ContentPiece.campaign_id == campaign_id
    ).group_by(ContentPiece.status).all()
    
    # Content by platform
    content_by_platform = db.query(
        ContentPiece.platform,
        db.func.count(ContentPiece.id).label('count')
    ).filter(
        ContentPiece.campaign_id == campaign_id,
        ContentPiece.platform.isnot(None)
    ).group_by(ContentPiece.platform).all()
    
    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "campaign_status": campaign.status,
        "campaign_progress": campaign.progress,
        "total_content_pieces": total_content,
        "content_by_type": [{"type": ct.content_type, "count": ct.count} for ct in content_by_type],
        "content_by_status": [{"status": cs.status, "count": cs.count} for cs in content_by_status],
        "content_by_platform": [{"platform": cp.platform, "count": cp.count} for cp in content_by_platform]
    }

@router.post("/{campaign_id}/duplicate")
def duplicate_campaign(
    campaign_id: int,
    new_name: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Duplicate a campaign with a new name"""
    
    original_campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id,
        Campaign.creator_id == current_user.id
    ).first()
    
    if not original_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if new name already exists for the same brand
    existing_campaign = db.query(Campaign).filter(
        Campaign.name == new_name,
        Campaign.brand_id == original_campaign.brand_id
    ).first()
    
    if existing_campaign:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign name already exists for this brand"
        )
    
    # Create duplicate campaign
    new_campaign = Campaign(
        name=new_name,
        description=original_campaign.description,
        brand_id=original_campaign.brand_id,
        creator_id=current_user.id,
        objective=original_campaign.objective,
        target_audience=original_campaign.target_audience,
        budget=original_campaign.budget,
        platforms=original_campaign.platforms,
        content_types=original_campaign.content_types,
        content_count=original_campaign.content_count,
        content_specs=original_campaign.content_specs,
        status="planning"  # Reset to planning status
    )
    
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    
    return {
        "message": "Campaign duplicated successfully",
        "new_campaign": new_campaign
    }