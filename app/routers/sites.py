"""
Site management endpoints for the Falcom Geofence API.

This router exposes CRUD operations for geofencing sites. Access is controlled
via role-based dependencies: admins can create, update and delete, managers
can list and view details, and employees have no access by default.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Site, UserRole
from ..schemas import SiteCreate, SiteRead, SiteUpdate
from ..dependencies import require_roles


router = APIRouter(prefix="/sites", tags=["Sites"])


@router.get("", response_model=list[SiteRead])
def list_sites(db: Session = Depends(get_db), user=Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER))):
    """Return a list of all sites. Accessible to admins and managers."""
    return db.query(Site).all()


@router.post("", response_model=SiteRead)
def create_site(
    site_in: SiteCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(UserRole.ADMIN)),
) -> Site:
    """Create a new site. Only admins may create."""
    site = Site(
        name=site_in.name,
        lat=site_in.lat,
        lng=site_in.lng,
        radius_m=site_in.radius_m,
        is_active=True,
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.get("/{site_id}", response_model=SiteRead)
def read_site(
    site_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user=Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
) -> Site:
    """Return a site by ID. Accessible to admins and managers."""
    site = db.get(Site, site_id)
    if site is None:
        raise HTTPException(status_code=404, detail="Site not found")
    return site


@router.put("/{site_id}", response_model=SiteRead)
def update_site(
    site_id: int,
    site_in: SiteUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(UserRole.ADMIN)),
) -> Site:
    """Update an existing site. Only admins may update."""
    site = db.get(Site, site_id)
    if site is None:
        raise HTTPException(status_code=404, detail="Site not found")
    # Update fields if provided
    for field, value in site_in.model_dump(exclude_unset=True).items():
        setattr(site, field, value)
    db.commit()
    db.refresh(site)
    return site


@router.delete("/{site_id}")
def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles(UserRole.ADMIN)),
) -> dict[str, str]:
    """Delete a site by ID. Only admins may delete."""
    site = db.get(Site, site_id)
    if site is None:
        raise HTTPException(status_code=404, detail="Site not found")
    db.delete(site)
    db.commit()
    return {"detail": "Deleted"}
