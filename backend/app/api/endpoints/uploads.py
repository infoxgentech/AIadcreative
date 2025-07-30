from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
import shutil
from PIL import Image
import json
from app.database.database import get_db
from app.api.dependencies.auth import get_current_active_user
from app.models.models import User, Brand, ReferenceMaterial
from app.core.config import settings

router = APIRouter()

# Ensure upload directory exists
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "brands"), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_DIR, "reference"), exist_ok=True)

# Pydantic models
class ReferenceMaterialResponse(BaseModel):
    id: int
    brand_id: int
    name: str
    description: Optional[str]
    file_type: str
    file_url: str
    file_size: Optional[int]
    original_filename: str
    extracted_text: Optional[str]
    color_analysis: Optional[dict]
    style_analysis: Optional[dict]
    content_tags: Optional[List[str]]
    usage_count: int
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True

def allowed_file(filename: str, allowed_types: List[str]) -> bool:
    """Check if file type is allowed"""
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_types

def get_file_type(filename: str) -> str:
    """Determine file type based on extension"""
    if '.' not in filename:
        return "unknown"
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension in settings.allowed_image_types:
        return "image"
    elif extension in settings.allowed_document_types:
        return "document"
    else:
        return "other"

def analyze_image_colors(image_path: str) -> dict:
    """Extract dominant colors from an image"""
    try:
        from PIL import Image
        import numpy as np
        from sklearn.cluster import KMeans
        
        # Open and resize image for faster processing
        image = Image.open(image_path)
        image = image.convert('RGB')
        image = image.resize((150, 150))
        
        # Convert to numpy array
        data = np.array(image)
        data = data.reshape((-1, 3))
        
        # Use KMeans to find dominant colors
        kmeans = KMeans(n_clusters=5, random_state=42)
        kmeans.fit(data)
        
        # Get colors and convert to hex
        colors = kmeans.cluster_centers_.astype(int)
        hex_colors = ['#%02x%02x%02x' % (r, g, b) for r, g, b in colors]
        
        return {
            "dominant_colors": hex_colors,
            "color_count": len(hex_colors)
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/reference-material", response_model=ReferenceMaterialResponse)
async def upload_reference_material(
    brand_id: int,
    name: str,
    description: str = "",
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload reference material for a brand"""
    
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
    
    # Check file type
    allowed_types = settings.allowed_image_types + settings.allowed_document_types
    if not allowed_file(file.filename, allowed_types):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Check file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
        )
    
    # Generate unique filename
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, "reference", unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Determine file type
    file_type = get_file_type(file.filename)
    
    # Analyze file content
    extracted_text = None
    color_analysis = None
    style_analysis = None
    content_tags = []
    
    if file_type == "image":
        # Analyze image colors
        color_analysis = analyze_image_colors(file_path)
        
        # Basic image analysis
        try:
            with Image.open(file_path) as img:
                style_analysis = {
                    "dimensions": f"{img.width}x{img.height}",
                    "format": img.format,
                    "mode": img.mode
                }
                
                # Generate basic content tags
                if img.width > img.height:
                    content_tags.append("landscape")
                elif img.height > img.width:
                    content_tags.append("portrait")
                else:
                    content_tags.append("square")
                
                if img.width >= 1920 or img.height >= 1920:
                    content_tags.append("high-resolution")
                
        except Exception as e:
            style_analysis = {"error": str(e)}
    
    # Create reference material record
    reference_material = ReferenceMaterial(
        brand_id=brand_id,
        name=name,
        description=description if description else None,
        file_type=file_type,
        file_url=f"/uploads/reference/{unique_filename}",
        file_size=file_size,
        original_filename=file.filename,
        extracted_text=extracted_text,
        color_analysis=color_analysis,
        style_analysis=style_analysis,
        content_tags=content_tags if content_tags else None
    )
    
    db.add(reference_material)
    db.commit()
    db.refresh(reference_material)
    
    return reference_material

@router.get("/reference-materials", response_model=List[ReferenceMaterialResponse])
def list_reference_materials(
    brand_id: int,
    file_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List reference materials for a brand"""
    
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
    
    query = db.query(ReferenceMaterial).filter(
        ReferenceMaterial.brand_id == brand_id,
        ReferenceMaterial.is_active == True
    )
    
    if file_type:
        query = query.filter(ReferenceMaterial.file_type == file_type)
    
    materials = query.offset(skip).limit(limit).all()
    return materials

@router.get("/reference-materials/{material_id}", response_model=ReferenceMaterialResponse)
def get_reference_material(
    material_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific reference material"""
    
    material = db.query(ReferenceMaterial).filter(
        ReferenceMaterial.id == material_id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference material not found"
        )
    
    # Verify brand ownership
    brand = db.query(Brand).filter(
        Brand.id == material.brand_id,
        Brand.owner_id == current_user.id
    ).first()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access denied"
        )
    
    # Increment usage count
    material.usage_count += 1
    db.commit()
    
    return material

@router.delete("/reference-materials/{material_id}")
def delete_reference_material(
    material_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a reference material"""
    
    material = db.query(ReferenceMaterial).filter(
        ReferenceMaterial.id == material_id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference material not found"
        )
    
    # Verify brand ownership
    brand = db.query(Brand).filter(
        Brand.id == material.brand_id,
        Brand.owner_id == current_user.id
    ).first()
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Access denied"
        )
    
    # Delete file from filesystem
    if material.file_url.startswith("/uploads/"):
        file_path = material.file_url[1:]  # Remove leading slash
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Soft delete from database
    material.is_active = False
    db.commit()
    
    return {"message": "Reference material deleted successfully"}

@router.post("/brand-logo")
async def upload_brand_logo(
    brand_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a brand logo"""
    
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
    
    # Check if file is an image
    if not allowed_file(file.filename, settings.allowed_image_types):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only image files are allowed. Allowed types: {', '.join(settings.allowed_image_types)}"
        )
    
    # Check file size
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
        )
    
    # Generate unique filename
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"logo_{brand_id}_{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, "brands", unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Update brand logo URLs
    logo_url = f"/uploads/brands/{unique_filename}"
    
    if brand.logo_urls:
        brand.logo_urls.append(logo_url)
    else:
        brand.logo_urls = [logo_url]
    
    db.commit()
    
    return {
        "message": "Logo uploaded successfully",
        "logo_url": logo_url,
        "brand_id": brand_id
    }

@router.get("/file-info")
def get_upload_info():
    """Get upload configuration information"""
    return {
        "max_file_size_mb": settings.max_file_size_mb,
        "allowed_image_types": settings.allowed_image_types,
        "allowed_document_types": settings.allowed_document_types,
        "upload_limits": {
            "images": f"{settings.max_file_size_mb}MB",
            "documents": f"{settings.max_file_size_mb}MB"
        }
    }