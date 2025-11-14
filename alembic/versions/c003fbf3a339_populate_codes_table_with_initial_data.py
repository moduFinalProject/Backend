"""populate codes table with initial data

Revision ID: c003fbf3a339
Revises: de7648f8f197
Create Date: 2025-11-14 23:12:40.581570

"""
from typing import Sequence, Union
import csv
import os

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c003fbf3a339'
down_revision: Union[str, None] = 'de7648f8f197'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Read CSV file and populate codes table
    csv_path = os.path.join(os.path.dirname(__file__), '../../seed_data/codes.csv')
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            op.execute(
                "INSERT INTO codes (code_id, detail_id, division, code_detail) "
                f"VALUES ({int(row['code_id'])}, {int(row['detail_id'])}, '{row['division']}', '{row['code_detail']}')"
            )


def downgrade() -> None:
    # Delete all codes data
    op.execute("DELETE FROM codes")
