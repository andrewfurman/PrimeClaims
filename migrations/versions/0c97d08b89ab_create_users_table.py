"""create_users_table

Revision ID: 0c97d08b89ab
Revises: 3cfcf4d3cd8d
Create Date: 2024-12-06 19:37:19.312241

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TEXT, JSONB


# revision identifiers, used by Alembic.
revision: str = '0c97d08b89ab'
down_revision: Union[str, None] = '3cfcf4d3cd8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('auth0_id', TEXT, nullable=False),
        sa.Column('email', TEXT, nullable=True),
        sa.Column('first_name', TEXT, nullable=True),
        sa.Column('last_name', TEXT, nullable=True),
        sa.Column('nickname', TEXT, nullable=True),
        sa.Column('picture', TEXT, nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=True),
        sa.Column('locale', TEXT, nullable=True),
        sa.Column('given_name', TEXT, nullable=True),
        sa.Column('family_name', TEXT, nullable=True),
        sa.Column('name', TEXT, nullable=True),
        sa.Column('custom_claims', JSONB, nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('login_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('auth0_id'),
        sa.UniqueConstraint('email')
    )
def downgrade() -> None:
    op.drop_table('users')