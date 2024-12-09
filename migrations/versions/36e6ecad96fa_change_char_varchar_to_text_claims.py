"""change_char_varchar_to_text_claims

Revision ID: 36e6ecad96fa
Revises: 
Create Date: 2024-11-25 21:33:10.321469

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
# revision identifiers
revision = '8fdee414033b'
down_revision = '9f371a4befb2'  # Make sure this points to the claims table migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
