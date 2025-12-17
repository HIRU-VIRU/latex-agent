"""
Authentication Routes
====================
User authentication and GitHub OAuth.
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel, EmailStr, Field
import httpx
import structlog

from app.core.database import get_db
from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    token_encryptor,
)
from app.models.user import User, GithubConnection
from app.api.deps import get_current_user
from app.services.document_parser import DocumentParserService
from app.services.gemini_client import gemini_client

logger = structlog.get_logger()


router = APIRouter()


# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str = Field(default=None)
    full_name: str = Field(default=None)
    
    def get_name(self) -> str:
        return self.name or self.full_name or "User"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: Optional[str]
    is_verified: bool

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """Complete user profile with all fields"""
    id: str
    email: str
    name: Optional[str]
    headline: Optional[str]
    summary: Optional[str]
    location: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    linkedin_url: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    country: Optional[str]
    institution: Optional[str]
    degree: Optional[str]
    field_of_study: Optional[str]
    graduation_year: Optional[str]
    skills: Optional[list]
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """Fields that can be updated in user profile"""
    name: Optional[str] = None
    headline: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    graduation_year: Optional[str] = None
    skills: Optional[list] = None


class GitHubCallbackRequest(BaseModel):
    code: str


# Routes
@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user with email and password."""
    # Check if user exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user
    user = User(
        email=user_data.email,
        name=user_data.get_name(),
        hashed_password=get_password_hash(user_data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Generate token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login with email and password."""
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        avatar_url=current_user.avatar_url,
        is_verified=current_user.is_verified,
    )


@router.get("/github/authorize")
async def github_authorize():
    """Get GitHub OAuth authorization URL."""
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth not configured",
        )
    
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_CALLBACK_URL,
        "scope": "read:user user:email repo",
        "state": "random_state_string",  # Should be random + stored
    }
    
    url = "https://github.com/login/oauth/authorize?" + "&".join(
        f"{k}={v}" for k, v in params.items()
    )
    
    return {"authorization_url": url}


@router.post("/github/callback", response_model=TokenResponse)
async def github_callback(
    callback_data: GitHubCallbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """Handle GitHub OAuth callback."""
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GitHub OAuth not configured",
        )
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": callback_data.code,
            },
            headers={"Accept": "application/json"},
        )
        token_data = token_response.json()
    
    if "error" in token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub OAuth error: {token_data.get('error_description', token_data['error'])}",
        )
    
    github_token = token_data["access_token"]
    
    # Get GitHub user info
    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {github_token}"},
        )
        github_user = user_response.json()
        
        # Get primary email
        emails_response = await client.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"token {github_token}"},
        )
        emails = emails_response.json()
        primary_email = next(
            (e["email"] for e in emails if e["primary"]),
            github_user.get("email")
        )
    
    if not primary_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not get email from GitHub",
        )
    
    # Check if GitHub connection exists
    result = await db.execute(
        select(GithubConnection).where(
            GithubConnection.github_user_id == github_user["id"]
        )
    )
    github_conn = result.scalar_one_or_none()
    
    if github_conn:
        # Update token
        github_conn.encrypted_token = token_encryptor.encrypt(github_token)
        user = await db.get(User, github_conn.user_id)
    else:
        # Check if user exists with this email
        result = await db.execute(
            select(User).where(User.email == primary_email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                email=primary_email,
                name=github_user.get("name") or github_user["login"],
                avatar_url=github_user.get("avatar_url"),
                is_verified=True,
            )
            db.add(user)
            await db.flush()
        
        # Create GitHub connection
        github_conn = GithubConnection(
            user_id=user.id,
            github_user_id=github_user["id"],
            github_username=github_user["login"],
            github_avatar_url=github_user.get("avatar_url"),
            encrypted_token=token_encryptor.encrypt(github_token),
            is_primary=True,
            scopes=["read:user", "user:email", "repo"],
        )
        db.add(github_conn)
    
    await db.commit()
    
    # Generate JWT
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    return TokenResponse(access_token=access_token)


# Next-auth compatibility endpoints
@router.get("/session")
async def get_session():
    """Next-auth session endpoint - returns null for our JWT-based auth."""
    return None


@router.post("/_log")
async def auth_log():
    """Next-auth logging endpoint - no-op for our implementation."""
    return {"ok": True}


@router.post("/upload-resume")
async def upload_resume_for_profile(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload an existing resume to extract profile information.
    Uses AI to parse the resume and populate user profile fields.
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    ext = file.filename.lower().split(".")[-1]
    if ext not in ["pdf", "docx", "doc", "txt"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Please upload PDF, DOCX, or TXT files."
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Extract text from document
        parser = DocumentParserService()
        text = await parser.extract_text(file.filename, content)
        
        if not text or len(text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract meaningful text from the document"
            )
        
        logger.info(f"Extracted {len(text)} characters from resume")
        
        # Use Gemini to parse resume and extract structured data
        prompt = f"""Extract profile information from this resume text:

{text[:3500]}

Return a JSON object with these fields (use null for any field not found):
- name: Full name
- email: Email address  
- phone: Phone number
- location: City and state
- city: City
- state: State
- country: Country
- headline: Professional title
- summary: Brief professional summary
- institution: Educational institution name
- degree: Degree name
- field_of_study: Major or field
- graduation_year: Year only
- linkedin_url: LinkedIn URL
- website: Portfolio URL
- skills: Array of skills

Extract only information clearly present."""
        
        try:
            logger.info(f"Attempting to parse resume with Gemini...")
            gemini_client.initialize()
            
            # Try the generate_json method first
            try:
                extracted_data = await gemini_client.generate_json(
                    prompt=prompt,
                    system_instruction="You are a professional resume parser. Return valid JSON only.",
                    temperature=0.1,
                )
                logger.info(f"Successfully parsed resume with {len(extracted_data)} fields")
                
            except Exception as json_error:
                logger.warning(f"generate_json failed: {json_error}, trying generate_content...")
                
                # Fallback to generate_content with manual JSON parsing
                import json
                import re
                
                response_text = await gemini_client.generate_content(
                    prompt=f"{prompt}\n\nReturn ONLY a valid JSON object, no markdown, no extra text.",
                    system_instruction="You are a professional resume parser.",
                    temperature=0.1,
                    max_tokens=1500,
                )
                
                # Clean and extract JSON
                cleaned = response_text.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                elif cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                
                # Extract JSON using regex
                json_match = re.search(r'\{[\s\S]*\}', cleaned)
                if json_match:
                    cleaned = json_match.group(0)
                
                extracted_data = json.loads(cleaned)
                logger.info(f"Successfully parsed with fallback method")
            
        except Exception as e:
            logger.error(f"All parsing attempts failed: {type(e).__name__}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse resume with AI. Error: {str(e)[:100]}. Please try again."
            )
        
        # Update user profile with extracted data (only non-null values)
        update_values = {}
        for field, value in extracted_data.items():
            if value is not None and value != "" and hasattr(User, field):
                # Don't overwrite email if already set
                if field == "email" and current_user.email:
                    continue
                # Don't overwrite name if already set and extracted name is generic
                if field == "name" and current_user.name and value.lower() in ["user", "name"]:
                    continue
                update_values[field] = value
        
        if update_values:
            await db.execute(
                update(User)
                .where(User.id == current_user.id)
                .values(**update_values)
            )
            await db.commit()
            await db.refresh(current_user)
        
        logger.info(f"Updated {len(update_values)} profile fields for user {current_user.id}")
        
        return {
            "message": "Resume parsed successfully",
            "fields_updated": len(update_values),
            "extracted_data": extracted_data,
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing resume: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """Get the current user's complete profile."""
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        headline=current_user.headline,
        summary=current_user.summary,
        location=current_user.location,
        phone=current_user.phone,
        website=current_user.website,
        linkedin_url=current_user.linkedin_url,
        address_line1=current_user.address_line1,
        address_line2=current_user.address_line2,
        city=current_user.city,
        state=current_user.state,
        zip_code=current_user.zip_code,
        country=current_user.country,
        institution=current_user.institution,
        degree=current_user.degree,
        field_of_study=current_user.field_of_study,
        graduation_year=current_user.graduation_year,
        skills=current_user.skills,
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile."""
    # Build update dict with only provided fields
    update_values = {}
    for field, value in profile_data.model_dump(exclude_unset=True).items():
        if value is not None:
            update_values[field] = value
    
    if update_values:
        await db.execute(
            update(User)
            .where(User.id == current_user.id)
            .values(**update_values)
        )
        await db.commit()
        await db.refresh(current_user)
    
    logger.info(f"Updated {len(update_values)} profile fields for user {current_user.id}")
    
    return UserProfileResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        headline=current_user.headline,
        summary=current_user.summary,
        location=current_user.location,
        phone=current_user.phone,
        website=current_user.website,
        linkedin_url=current_user.linkedin_url,
        address_line1=current_user.address_line1,
        address_line2=current_user.address_line2,
        city=current_user.city,
        state=current_user.state,
        zip_code=current_user.zip_code,
        country=current_user.country,
        institution=current_user.institution,
        degree=current_user.degree,
        field_of_study=current_user.field_of_study,
        graduation_year=current_user.graduation_year,
        skills=current_user.skills,
    )