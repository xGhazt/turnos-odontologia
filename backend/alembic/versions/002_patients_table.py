"""Add patients table

Revision ID: 002_patients_table
Revises: e6f9e85a897f
Create Date: 2026-11-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "002_patients_table"
down_revision: Union[str, Sequence[str], None] = "e6f9e85a897f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("dni", sa.String(length=20), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=150), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("insurance_provider", sa.String(length=100), nullable=True),
        sa.Column("insurance_number", sa.String(length=50), nullable=True),
        sa.Column("medical_history", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.create_index("ix_patients_dni", "patients", ["dni"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_patients_dni", table_name="patients")
    op.drop_table("patients")
