from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./survey.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Pydantic models for request body
class IdealPrices(BaseModel):
    singleSpiritMixer: Optional[int] = Field(None, ge=0, le=1000)
    doubleSpiritMixer: Optional[int] = Field(None, ge=0, le=1000)
    pint: Optional[int] = Field(None, ge=0, le=1000)
    bottleCan: Optional[int] = Field(None, ge=0, le=1000)

class SurveyResponse(BaseModel):
    eventTypes: List[str] = Field(..., max_length=10)
    frequency: Optional[str] = Field(None, max_length=50)
    toiletImportance: Optional[str] = Field(None, max_length=50)
    seatingImportance: Optional[str] = Field(None, max_length=50)
    fastEntryImportance: Optional[str] = Field(None, max_length=50)
    securityImportance: Optional[str] = Field(None, max_length=50)
    barPriorities: List[str] = Field(..., max_length=10)
    idealPrices: IdealPrices
    soundSystemQuality: Optional[int] = Field(None, ge=1, le=5)
    lightingLasers: Optional[int] = Field(None, ge=1, le=5)
    stageVisualsScreens: Optional[int] = Field(None, ge=1, le=5)
    smokeHazeEffects: Optional[int] = Field(None, ge=1, le=5)
    roomAtmosphere: Optional[int] = Field(None, ge=1, le=5)
    goodSoundSystemFeatures: List[str] = Field(..., max_length=20)
    djValues: List[str] = Field(..., max_length=20)
    genresMoreOf: str = Field(..., max_length=1000)
    respectfulCrowd: Optional[int] = Field(None, ge=1, le=5)
    cleanEnvironment: Optional[int] = Field(None, ge=1, le=5)
    temperatureVentilation: Optional[int] = Field(None, ge=1, le=5)
    zeroDramaAtmosphere: Optional[int] = Field(None, ge=1, le=5)
    feelingSafe: Optional[str] = Field(None, max_length=50)
    averageEventPrice: Optional[str] = Field(None, max_length=50)
    premiumEventPrice: Optional[str] = Field(None, max_length=50)
    addOns: List[str] = Field(..., max_length=20)
    clubsNeverGetRight: str = Field(..., max_length=2000)
    clubsDoMore: str = Field(..., max_length=2000)
    loyalAttendee: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)

# SQLAlchemy model for database table
class DBSurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(Integer, primary_key=True, index=True)
    eventTypes = Column(JSON)
    frequency = Column(String)
    toiletImportance = Column(String)
    seatingImportance = Column(String)
    fastEntryImportance = Column(String)
    securityImportance = Column(String)
    barPriorities = Column(JSON)
    idealPrices = Column(JSON)
    soundSystemQuality = Column(Integer)
    lightingLasers = Column(Integer)
    stageVisualsScreens = Column(Integer)
    smokeHazeEffects = Column(Integer)
    roomAtmosphere = Column(Integer)
    goodSoundSystemFeatures = Column(JSON)
    djValues = Column(JSON)
    genresMoreOf = Column(String)
    respectfulCrowd = Column(Integer)
    cleanEnvironment = Column(Integer)
    temperatureVentilation = Column(Integer)
    zeroDramaAtmosphere = Column(Integer)
    feelingSafe = Column(String)
    averageEventPrice = Column(String)
    premiumEventPrice = Column(String)
    addOns = Column(JSON)
    clubsNeverGetRight = Column(String)
    clubsDoMore = Column(String)
    loyalAttendee = Column(String)
    email = Column(String, unique=True, index=True, nullable=True)

Base.metadata.create_all(bind=engine)

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

# Initialize FastAPI app
app = FastAPI(
    title="Survey API",
    description="Club/Event Survey API with security features",
    version="1.0.0"
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    max_age=3600,
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/submit")
@limiter.limit("5/minute")  # 5 submissions per minute per IP
async def submit_survey(request: Request, response: SurveyResponse, db: Session = Depends(get_db)):
    """
    Submit a survey response with rate limiting and error handling
    """
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Survey submission attempt from IP: {client_ip}")

    try:
        db_response = DBSurveyResponse(
            eventTypes=response.eventTypes,
            frequency=response.frequency,
            toiletImportance=response.toiletImportance,
            seatingImportance=response.seatingImportance,
            fastEntryImportance=response.fastEntryImportance,
            securityImportance=response.securityImportance,
            barPriorities=response.barPriorities,
            idealPrices=response.idealPrices.dict(),
            soundSystemQuality=response.soundSystemQuality,
            lightingLasers=response.lightingLasers,
            stageVisualsScreens=response.stageVisualsScreens,
            smokeHazeEffects=response.smokeHazeEffects,
            roomAtmosphere=response.roomAtmosphere,
            goodSoundSystemFeatures=response.goodSoundSystemFeatures,
            djValues=response.djValues,
            genresMoreOf=response.genresMoreOf,
            respectfulCrowd=response.respectfulCrowd,
            cleanEnvironment=response.cleanEnvironment,
            temperatureVentilation=response.temperatureVentilation,
            zeroDramaAtmosphere=response.zeroDramaAtmosphere,
            feelingSafe=response.feelingSafe,
            averageEventPrice=response.averageEventPrice,
            premiumEventPrice=response.premiumEventPrice,
            addOns=response.addOns,
            clubsNeverGetRight=response.clubsNeverGetRight,
            clubsDoMore=response.clubsDoMore,
            loyalAttendee=response.loyalAttendee,
            email=response.email,
        )

        db.add(db_response)
        db.commit()
        db.refresh(db_response)

        logger.info(f"Survey submitted successfully with ID: {db_response.id} from IP: {client_ip}")
        return {"message": "Survey submitted successfully!", "response_id": db_response.id}

    except IntegrityError as e:
        db.rollback()
        logger.warning(f"Duplicate submission attempt from IP: {client_ip} - {str(e)}")

        # Check if it's a duplicate email error
        if "email" in str(e.orig).lower() or "unique" in str(e.orig).lower():
            raise HTTPException(
                status_code=400,
                detail="This email address has already been used to submit a survey. Each email can only be used once."
            )

        raise HTTPException(
            status_code=400,
            detail="A submission with this information already exists."
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error processing survey submission from IP: {client_ip} - {str(e)}", exc_info=True)

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your submission. Please try again later."
        )

@app.get("/")
async def read_root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to the Survey API",
        "version": "1.0.0",
        "endpoints": {
            "submit": "/submit",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "survey-api"
    }
