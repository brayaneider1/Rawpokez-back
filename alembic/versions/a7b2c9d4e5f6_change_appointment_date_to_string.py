"""add missing quotation fields: appointment_date, size_category, allergies, discount

Revision ID: a7b2c9d4e5f6
Revises: 2461a3998b27
Create Date: 2026-05-20 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a7b2c9d4e5f6'
down_revision: Union[str, None] = '2461a3998b27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Campos que el modelo tiene pero que NUNCA se migraron a la BD
    op.add_column('quotation', sa.Column('size_category', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('quotation', sa.Column('allergies', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('quotation', sa.Column('discount_code', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('quotation', sa.Column('discount_evidence_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    # appointment_date como VARCHAR — el frontend envía "Lunes", "Martes", etc.
    op.add_column('quotation', sa.Column('appointment_date', sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade() -> None:
    op.drop_column('quotation', 'appointment_date')
    op.drop_column('quotation', 'discount_evidence_url')
    op.drop_column('quotation', 'discount_code')
    op.drop_column('quotation', 'allergies')
    op.drop_column('quotation', 'size_category')
