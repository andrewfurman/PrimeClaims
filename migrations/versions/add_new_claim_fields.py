
"""add_new_claim_fields

Revision ID: add_new_claim_fields
Revises: 0c97d08b89ab
Create Date: 2024-01-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import TEXT, NUMERIC

# revision identifiers, used by Alembic.
revision: str = 'add_new_claim_fields'
down_revision: Union[str, None] = '0c97d08b89ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drug Information Fields
    op.add_column('claims', sa.Column('drug_name', TEXT, nullable=True))
    op.add_column('claims', sa.Column('drug_strength', TEXT, nullable=True))
    op.add_column('claims', sa.Column('drug_form', TEXT, nullable=True))
    
    # DAW & Related Codes
    op.add_column('claims', sa.Column('daw_code', TEXT, nullable=True))
    op.add_column('claims', sa.Column('professional_service_code', TEXT, nullable=True))
    op.add_column('claims', sa.Column('dur_pps_level_of_effort_value', TEXT, nullable=True))
    op.add_column('claims', sa.Column('reason_for_service_code', TEXT, nullable=True))
    op.add_column('claims', sa.Column('submission_clarification_code', TEXT, nullable=True))
    op.add_column('claims', sa.Column('result_of_service_code', TEXT, nullable=True))
    
    # Payment and Amount Fields
    op.add_column('claims', sa.Column('vaccine_administration_reimbursement_amount', NUMERIC(10,2), nullable=True))
    op.add_column('claims', sa.Column('other_payer_patient_responsibility_amount', NUMERIC(10,2), nullable=True))
    op.add_column('claims', sa.Column('other_payer_reject_code', TEXT, nullable=True))
    
    # Other Payer and Coverage Details
    op.add_column('claims', sa.Column('other_payer_qualifier', TEXT, nullable=True))
    
    # Context and Location Fields
    op.add_column('claims', sa.Column('place_of_service', TEXT, nullable=True))
    op.add_column('claims', sa.Column('pharmacy_service_type', TEXT, nullable=True))
    op.add_column('claims', sa.Column('patient_residence_code', TEXT, nullable=True))


def downgrade() -> None:
    # Drop all new columns in reverse order
    op.drop_column('claims', 'patient_residence_code')
    op.drop_column('claims', 'pharmacy_service_type')
    op.drop_column('claims', 'place_of_service')
    op.drop_column('claims', 'other_payer_qualifier')
    op.drop_column('claims', 'other_payer_reject_code')
    op.drop_column('claims', 'other_payer_patient_responsibility_amount')
    op.drop_column('claims', 'vaccine_administration_reimbursement_amount')
    op.drop_column('claims', 'result_of_service_code')
    op.drop_column('claims', 'submission_clarification_code')
    op.drop_column('claims', 'reason_for_service_code')
    op.drop_column('claims', 'dur_pps_level_of_effort_value')
    op.drop_column('claims', 'professional_service_code')
    op.drop_column('claims', 'daw_code')
    op.drop_column('claims', 'drug_form')
    op.drop_column('claims', 'drug_strength')
    op.drop_column('claims', 'drug_name')
