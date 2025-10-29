from __future__ import annotations
import asyncio
from fastapi import FastAPI

from .db import Base, engine, SessionLocal
from .models import User, UserRole, Site
from .auth import get_password_hash
from .routers import auth as auth_router, sites as sites_router
from .routers import tracking as tracking_router  # NEW

app = FastAPI(title="Falcom Geofence API")

def _site_kwargs(
    name_en: str,
    name_ar: str,
    desc_en: str,
    desc_ar: str,
    lat: float,
    lng: float,
    radius_m: float = 150.0,
    is_active: bool = True,
) -> dict:
    """
    يبني kwargs للموديل Site بحيث:
    - لو الحقول العربية/الإنجليزية موجودة بالموديل: يحطها + يضبط name = name_en
    - لو غير موجودة (توافق خلفي): يكتفي بـ name فقط
    """
    kw = dict(lat=lat, lng=lng, radius_m=radius_m, is_active=is_active)

    has_bilingual = all(
        hasattr(Site, attr)
        for attr in ("name_ar", "name_en", "description_ar", "description_en")
    )

    if has_bilingual:
        kw.update(
            name=name_en,  # نحتفظ بعمود name للأمام/التوافق
            name_en=name_en,
            name_ar=name_ar,
            description_en=desc_en,
            description_ar=desc_ar,
        )
    else:
        kw.update(name=name_en)

    return kw


def seed() -> None:
    """
    تهيئة بيانات البداية (Idempotent):
    - إنشاء مستخدم أدمن إن لم يوجد.
    - زرع مواقع افتراضية AR/EN إن كانت الحقول موجودة، وإلا يستخدم name فقط.
    """
    db = SessionLocal()
    try:
        # 1) Admin user (employee_id=220220) إن لم يوجد
        admin = db.query(User).filter_by(employee_id="220220").first()
        if not admin:
            admin = User(
                employee_id="220220",
                full_name="Falcom Admin",
                email=None,
                role=UserRole.admin,          # ✅ lowercase enum
                password_hash=get_password_hash("admin"),  # ≤ 72 bytes
                is_active=True,
            )
            db.add(admin)

        # 2) Seed مواقع افتراضية مرة واحدة
        if db.query(Site).count() == 0:
            sites_data = [
                _site_kwargs(
                    name_en="Headquarters",
                    name_ar="المقر الرئيسي",
                    desc_en="Administrative headquarters",
                    desc_ar="موقع المقر الإداري الرئيسي",
                    lat=24.7136, lng=46.6753, radius_m=150.0,
                ),
                _site_kwargs(
                    name_en="Tabuk Crusher",
                    name_ar="كسارة تبوك",
                    desc_en="Tabuk Crusher site",
                    desc_ar="موقع كسارة تبوك",
                    lat=28.08554, lng=36.87086, radius_m=150.0,
                ),
                _site_kwargs(
                    name_en="Dammam Asphalt Plant",
                    name_ar="مصنع أسفلت الدمام",
                    desc_en="Dammam asphalt plant",
                    desc_ar="مصنع الأسفلت في الدمام",
                    lat=26.650523, lng=49.995995, radius_m=150.0,
                ),
                _site_kwargs(
                    name_en="As-Summan Crusher",
                    name_ar="كسارة الصمان",
                    desc_en="As-Summan Crusher site",
                    desc_ar="موقع كسارة الصمان",
                    lat=25.528727, lng=48.392180, radius_m=150.0,
                ),
            ]
            db.add_all(Site(**s) for s in sites_data)

        db.commit()
    finally:
        db.close()


@app.on_event("startup")
async def on_startup():
    # إنشاء الجداول (لا يضر حتى لو Alembic يعمل migrations)
    Base.metadata.create_all(bind=engine)
    # شغّل seeding في ثريد منفصل (بدون استخدام get_db كـ context manager)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, seed)

# تسجيل الراوترات (نفس القواعد اللي ثبتناها)
app.include_router(auth_router.router)
app.include_router(sites_router.router)
app.include_router(tracking_router.router)  # NEW

@app.get("/health")
def health():
    return {"status": "ok"}
