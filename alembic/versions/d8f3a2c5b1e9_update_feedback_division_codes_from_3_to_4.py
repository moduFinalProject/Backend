"""Update feedback_division codes from 3 options to 4 options

Revision ID: d8f3a2c5b1e9
Revises: c588c1c558b5
Create Date: 2025-11-17 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8f3a2c5b1e9'
down_revision: Union[str, None] = 'c588c1c558b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get the database connection to check current state
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Check if codes table exists
    if 'codes' not in inspector.get_table_names():
        return

    # 역순으로 업데이트 (뒤에서 앞으로)
    # 3 -> 4, 2 -> 3, 1 -> 2, 새로 1 추가

    # Step 1: 3(제안) -> 4(권장)로 변경
    op.execute("""
        UPDATE codes
        SET detail_id = '4', code_detail = '추가 권장사항'
        WHERE division = 'feedback_division' AND detail_id = '3'
    """)

    # Step 2: 2(권장) -> 3(개선)으로 변경
    op.execute("""
        UPDATE codes
        SET detail_id = '3', code_detail = '개선 제안사항'
        WHERE division = 'feedback_division' AND detail_id = '2'
    """)

    # Step 3: 1(필수) -> 2(필수수정)로 변경
    op.execute("""
        UPDATE codes
        SET detail_id = '2', code_detail = '필수 수정사항'
        WHERE division = 'feedback_division' AND detail_id = '1'
    """)

    # Step 4: 새로운 코드 추가 (잘된부분 = 1, code_id = 8)
    op.execute("""
        INSERT INTO codes (code_id, division, detail_id, code_detail)
        SELECT 8, 'feedback_division', '1', '잘된 부분'
        WHERE NOT EXISTS (
            SELECT 1 FROM codes
            WHERE division = 'feedback_division' AND detail_id = '1'
        )
    """)


def downgrade() -> None:
    # Get the database connection to check current state
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Check if codes table exists
    if 'codes' not in inspector.get_table_names():
        return

    # 역순: 새로운 값들을 기존 값들로 복원

    # Step 1: 잘된부분(1) 삭제
    op.execute("""
        DELETE FROM codes
        WHERE division = 'feedback_division' AND detail_id = '1'
    """)

    # Step 2: 필수수정(2) -> 필수(1)로 복원
    op.execute("""
        UPDATE codes
        SET detail_id = '1', code_detail = '필수'
        WHERE division = 'feedback_division' AND detail_id = '2'
    """)

    # Step 3: 개선(3) -> 권장(2)로 복원
    op.execute("""
        UPDATE codes
        SET detail_id = '2', code_detail = '권장'
        WHERE division = 'feedback_division' AND detail_id = '3'
    """)

    # Step 4: 추가권장(4) -> 제안(3)으로 복원
    op.execute("""
        UPDATE codes
        SET detail_id = '3', code_detail = '제안'
        WHERE division = 'feedback_division' AND detail_id = '4'
    """)
