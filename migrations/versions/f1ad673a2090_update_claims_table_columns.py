"""update_claims_table_columns

Revision ID: f1ad673a2090
Revises: 8fdee414033b
Create Date: 2024-11-25 21:55:36.165982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1ad673a2090'
down_revision: Union[str, None] = '8fdee414033b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Convert CHAR/VARCHAR columns to TEXT
    op.alter_column('claims', 'service_provider_id_qualifier',
        type_=sa.TEXT(),
        existing_type=sa.CHAR(2),
        nullable=True)
    
    op.alter_column('claims', 'service_provider_id',
        type_=sa.TEXT(),
        existing_type=sa.VARCHAR(15),
        nullable=True)
    
    op.alter_column('claims', 'other_payer_id_qualifier',
        type_=sa.TEXT(),
        existing_type=sa.CHAR(2),
        nullable=True)
    
    op.alter_column('claims', 'other_payer_id',
        type_=sa.TEXT(),
        existing_type=sa.VARCHAR(15),
        nullable=True)
    
    op.alter_column('claims', 'diagnosis_code_qualifier',
        type_=sa.TEXT(),
        existing_type=sa.CHAR(2),
        nullable=True)
    
    op.alter_column('claims', 'diagnosis_code',
        type_=sa.TEXT(),
        existing_type=sa.VARCHAR(15),
        nullable=True)

def downgrade() -> None:
    # Revert TEXT columns back to CHAR/VARCHAR
    op.alter_column('claims', 'service_provider_id_qualifier',
        type_=sa.CHAR(2),
        existing_type=sa.TEXT(),
        nullable=False)
    
    op.alter_column('claims', 'service_provider_id',
        type_=sa.VARCHAR(15),
        existing_type=sa.TEXT(),
        nullable=False)
    
    op.alter_column('claims', 'other_payer_id_qualifier',
        type_=sa.CHAR(2),
        existing_type=sa.TEXT(),
        nullable=True)
    
    op.alter_column('claims', 'other_payer_id',
        type_=sa.VARCHAR(15),
        existing_type=sa.TEXT(),
        nullable=True)
    
    op.alter_column('claims', 'diagnosis_code_qualifier',
        type_=sa.CHAR(2),
        existing_type=sa.TEXT(),
        nullable=True)
    
    op.alter_column('claims', 'diagnosis_code',
        type_=sa.VARCHAR(15),
        existing_type=sa.TEXT(),
        nullable=True)