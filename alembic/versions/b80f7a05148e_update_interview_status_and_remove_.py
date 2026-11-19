"""update interview status and remove interviewfeedback title

Revision ID: b80f7a05148e
Revises: 6f25695d25f0
Create Date: 2025-12-06 04:57:48.145979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b80f7a05148e'
down_revision: Union[str, None] = '6f25695d25f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove title column from interviewfeedbacks table
    op.drop_column('interviewfeedbacks', 'title')

    # Add INTERVIEW_STATUS codes to codes table
    op.execute(
        "INSERT INTO codes (code_id, detail_id, division, code_detail) VALUES "
        "(12, 1, 'INTERVIEW_STATUS', '진행중'), "
        "(12, 2, 'INTERVIEW_STATUS', '완료')"
    )


def downgrade() -> None:
    # Add back title column to interviewfeedbacks table
    op.add_column('interviewfeedbacks',
                  sa.Column('title', sa.VARCHAR(length=20), nullable=False))

    # Remove INTERVIEW_STATUS codes from codes table
    op.execute("DELETE FROM codes WHERE division = 'INTERVIEW_STATUS'")
