"""add default to created_at

Revision ID: 00c2eb73eb59
Revises: 26f9681d0325
Create Date: 2025-11-06 17:02:29.638879

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00c2eb73eb59'
down_revision: Union[str, None] = '26f9681d0325'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # ✅ 컬럼 이름 변경 (데이터 유지)
    op.alter_column('codes', 'title', new_column_name='code_detail')

def downgrade():
    # 원래대로 복구
    op.alter_column('codes', 'title', new_column_name='code_name')