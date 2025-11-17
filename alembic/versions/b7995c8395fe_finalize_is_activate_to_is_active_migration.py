"""Finalize is_activate to is_active migration - handles both dev and prod environments

Revision ID: b7995c8395fe
Revises: 974b0b6876b3
Create Date: 2025-11-17 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7995c8395fe'
down_revision: Union[str, None] = '974b0b6876b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get the database connection to check current state
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Tables that may have is_activate column
    tables_to_check = ['users', 'jobpostings', 'resumes', 'studyguides', 'interviewfeedbacks']

    for table_name in tables_to_check:
        if table_name not in inspector.get_table_names():
            continue

        columns = {col['name'] for col in inspector.get_columns(table_name)}

        # If is_activate exists and is_active doesn't, rename it
        if 'is_activate' in columns and 'is_active' not in columns:
            op.alter_column(table_name, 'is_activate', new_column_name='is_active')
        # If both exist, drop is_activate and keep is_active
        elif 'is_activate' in columns and 'is_active' in columns:
            op.drop_column(table_name, 'is_activate')
        # If only is_activate exists, rename it
        elif 'is_activate' in columns:
            op.alter_column(table_name, 'is_activate', new_column_name='is_active')


def downgrade() -> None:
    # Get the database connection to check current state
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Tables that should have is_active column
    tables_to_check = ['users', 'jobpostings', 'resumes', 'studyguides', 'interviewfeedbacks']

    for table_name in tables_to_check:
        if table_name not in inspector.get_table_names():
            continue

        columns = {col['name'] for col in inspector.get_columns(table_name)}

        # Rename is_active back to is_activate
        if 'is_active' in columns:
            op.alter_column(table_name, 'is_active', new_column_name='is_activate')
