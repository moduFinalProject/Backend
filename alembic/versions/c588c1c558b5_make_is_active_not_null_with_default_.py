"""make is_active not null with default true in users and resumes

Revision ID: c588c1c558b5
Revises: b7995c8395fe
Create Date: 2025-11-17 12:38:39.631171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c588c1c558b5'
down_revision: Union[str, None] = 'b7995c8395fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get the database connection to check current state
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Tables to update
    tables = ['users', 'resumes']

    for table_name in tables:
        if table_name not in inspector.get_table_names():
            continue

        # Get column info
        columns = inspector.get_columns(table_name)
        is_active_column = next((col for col in columns if col['name'] == 'is_active'), None)

        if is_active_column:
            # Update all NULL values to TRUE before adding NOT NULL constraint
            op.execute(f"UPDATE {table_name} SET is_active = TRUE WHERE is_active IS NULL")

            # Alter column to NOT NULL with default TRUE
            op.alter_column(
                table_name,
                'is_active',
                existing_type=sa.Boolean(),
                nullable=False,
                existing_nullable=True,
                server_default=sa.sql.expression.literal(True)
            )


def downgrade() -> None:
    # Get the database connection to check current state
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Tables to revert
    tables = ['users', 'resumes']

    for table_name in tables:
        if table_name not in inspector.get_table_names():
            continue

        # Revert column to nullable
        op.alter_column(
            table_name,
            'is_active',
            existing_type=sa.Boolean(),
            nullable=True,
            existing_nullable=False,
            server_default=None
        )
