"""add bilingual fields to sites and create tracking_points
Revision ID: 0002_bilingual_and_tracking
Revises: 0001_create_users_and_sites
Create Date: 2025-10-29
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_bilingual_and_tracking"
down_revision = "0001_create_users_and_sites"
branch_labels = None
depends_on = None

def upgrade():
    # Add bilingual columns to sites (nullable)
    op.add_column("sites", sa.Column("name_ar", sa.String(length=255), nullable=True))
    op.add_column("sites", sa.Column("name_en", sa.String(length=255), nullable=True))
    op.add_column("sites", sa.Column("description_ar", sa.String(length=1000), nullable=True))
    op.add_column("sites", sa.Column("description_en", sa.String(length=1000), nullable=True))

    # Create tracking_points
    op.create_table(
        "tracking_points",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("employee_id", sa.String(length=32), nullable=False, index=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("lat", sa.Float, nullable=False),
        sa.Column("lng", sa.Float, nullable=False),
        sa.Column("accuracy", sa.Float, nullable=True),
        sa.Column("site_id", sa.Integer, sa.ForeignKey("sites.id"), nullable=True),
        sa.Column("site_name_ar", sa.String(length=255), nullable=True),
        sa.Column("site_name_en", sa.String(length=255), nullable=True),
    )
    # explicit indexes for portability
    op.create_index("ix_tracking_points_employee_timestamp", "tracking_points", ["employee_id", "timestamp"])

def downgrade():
    op.drop_index("ix_tracking_points_employee_timestamp", table_name="tracking_points")
    op.drop_table("tracking_points")
    op.drop_column("sites", "description_en")
    op.drop_column("sites", "description_ar")
    op.drop_column("sites", "name_en")
    op.drop_column("sites", "name_ar")
