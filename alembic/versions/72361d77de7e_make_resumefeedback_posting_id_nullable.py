"""make resumefeedback posting_id nullable

Revision ID: 72361d77de7e
Revises: d8f3a2c5b1e9
Create Date: 2025-11-18 17:30:22.144897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72361d77de7e'
down_revision: Union[str, None] = 'd8f3a2c5b1e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make posting_id nullable in resumefeedbacks table
    op.alter_column('resumefeedbacks', 'posting_id',
               existing_type=sa.INTEGER(),
               nullable=True)


def downgrade() -> None:
    # Revert posting_id back to not nullable
    op.alter_column('resumefeedbacks', 'posting_id',
               existing_type=sa.INTEGER(),
               nullable=False)
