# app/routers/tracking.py
from __future__ import annotations
import math
import datetime as dt
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import TrackingPoint, Site, UserRole
from ..schemas import TrackingPointCreate, TrackingPointRead
from ..dependencies import require_roles, get_current_user

router = APIRouter(prefix="/tracking", tags=["Tracking"])

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)
    return 2*R*math.asin(math.sqrt(a))

@router.post("", response_model=TrackingPointRead)
def post_tracking(
    payload: TrackingPointCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # employees can only submit for themselves
    if user.role == UserRole.employee and payload.employee_id != user.employee_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    # auto-detect nearest active site within radius
    nearest_site = None
    nearest_dist = None
    for site in db.query(Site).filter_by(is_active=True).all():
        d = haversine_m(payload.lat, payload.lng, site.lat, site.lng)
        if d <= site.radius_m and (nearest_dist is None or d < nearest_dist):
            nearest_dist, nearest_site = d, site

    tp = TrackingPoint(
        employee_id=payload.employee_id,
        timestamp=payload.timestamp or dt.datetime.utcnow(),
        lat=payload.lat,
        lng=payload.lng,
        accuracy=payload.accuracy,
        site_id=nearest_site.id if nearest_site else None,
        site_name_ar=nearest_site.name_ar if nearest_site else None,
        site_name_en=nearest_site.name_en if nearest_site else None,
    )
    db.add(tp)
    db.commit()
    db.refresh(tp)
    return tp

@router.get("/report", response_model=list[TrackingPointRead])
def tracking_report(
    employee_id: str = Query(...),
    start_date: dt.date = Query(...),
    end_date: dt.date = Query(...),
    limit: int = Query(1000, ge=1, le=10000),
    db: Session = Depends(get_db),
    user=Depends(require_roles(UserRole.admin, UserRole.manager)),
):
    start_dt = dt.datetime.combine(start_date, dt.time.min, tzinfo=None)
    end_dt = dt.datetime.combine(end_date, dt.time.max, tzinfo=None)
    q = (
        db.query(TrackingPoint)
        .filter(TrackingPoint.employee_id == employee_id)
        .filter(TrackingPoint.timestamp >= start_dt)
        .filter(TrackingPoint.timestamp <= end_dt)
        .order_by(TrackingPoint.timestamp.asc())
        .limit(limit)
    )
    return q.all()
