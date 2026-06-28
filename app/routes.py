from fastapi import APIRouter, FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone

from app.database import get_db
from app.models import URL
from app.schemas import ShortenRequest, ShortenResponse, StatsResponse
from app.idgen import generate_short_code
from app.cache import get_cached_url, cache_url, invalidate_url
from app.tasks import increment_click_count

router = APIRouter()

@router.post("/api/v1/shorten_url", response_model=ShortenResponse, status_code=201)
def shorten_url(request:ShortenRequest, db: Session = Depends(get_db)):
    if request.custom_alias:

        existing = db.query(URL).filter(URL.short_code == request.custom_alias).first()
        if existing:
            raise HTTPException(status_code=409, detail="Custom alias already in use")
        
        short_code = request.custom_alias
    else:
        short_code = generate_short_code()

    expires_at = None
    if request.expires_in_days:
        expires_at = (datetime.now(timezone.utc) + timedelta(days=request.expires_in_days))
    
    url_record = URL(
        short_code=short_code,
        long_url=str(request.long_url),
        expires_at=expires_at
    )

    db.add(url_record)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="short code collision, try again")
    
    db.refresh(url_record)
    cache_url(short_code, str(request.long_url))

    return ShortenResponse(
        short_code=short_code,
        short_url=f"https://short.ly/{short_code}",
        long_url=str(request.long_url),
        created_at=url_record.created_at,
        expires_at=url_record.expires_at
    )

@router.get("/{short_code}")
def redirect_url(short_code:str, db: Session = Depends(get_db)):

    long_url = get_cached_url(short_code)

    if long_url is None:

        url_record = db.query(URL).filter(
            URL.short_code == short_code,
            URL.is_active == True
        ).first()

        if not url_record:
            raise HTTPException(status_code=404, detail="Not found")
        
        if url_record.expires_at and url_record.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=410, detail="Expired")
        
        long_url = url_record.long_url
        cache_url(short_code, long_url)
    
    increment_click_count.delay(short_code)

    return RedirectResponse(url=long_url, status_code=302)

@router.get("/api/v1/{short_code}/stats")
def get_stats(short_code: str, db: Session = Depends(get_db)):
    url_record = db.query(URL).filter(URL.short_code==short_code).first()

    if not url_record:
        raise HTTPException(status_code=404, detail="Short url not found")
    
    return StatsResponse(
        short_code=url_record.short_code,
        long_url=url_record.long_url,
        click_count=url_record.click_count,
        created_at=url_record.created_at,
        expires_at=url_record.expires_at,
        is_active=url_record.is_active
    )