from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import TEXT, NUMERIC, VARCHAR
from members.member_model import db, Member

class Claim(db.Model):
    __tablename__ = 'claims'
    
    # Primary Key
    claim_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key to Member
    # Update the Foreign Key to include cascade delete
    member_id = db.Column(db.Integer, 
                         db.ForeignKey('members.database_id', ondelete='CASCADE'), 
                         nullable=False)
    
    # Service Provider Information
    service_provider_id_qualifier = db.Column(db.TEXT, nullable=True)
    service_provider_id = db.Column(db.TEXT, nullable=True)
    
    # Other Payer Information
    other_payer_id_qualifier = db.Column(db.TEXT, nullable=True)
    other_payer_id = db.Column(db.TEXT, nullable=True)
    other_payer_amount_paid = db.Column(NUMERIC(10,2), nullable=True)
    
    # Diagnosis Information
    diagnosis_code_qualifier = db.Column(db.TEXT, nullable=True)
    diagnosis_code = db.Column(db.TEXT, nullable=True)
    clinical_information = db.Column(TEXT, nullable=True)
    
    # Claim Details (AM07)
    prescription_service_reference_number_qualifier = db.Column(TEXT, nullable=True)
    prescription_service_reference_number = db.Column(TEXT, nullable=True)
    product_service_id_qualifier = db.Column(TEXT, nullable=True)
    product_service_id = db.Column(TEXT, nullable=True)
    quantity_dispensed = db.Column(db.Integer, nullable=True)
    fill_number = db.Column(db.Integer, nullable=True)
    ndc_number = db.Column(TEXT, nullable=True)
    days_supply = db.Column(db.Integer, nullable=True)
    dispense_as_written = db.Column(db.Boolean, nullable=True)
    date_prescription_written = db.Column(db.Date, nullable=True)
    prescription_origin_code = db.Column(TEXT, nullable=True)
    other_coverage_code = db.Column(TEXT, nullable=True)
    special_packaging_indicator = db.Column(db.Boolean, nullable=True)
    unit_of_measure = db.Column(TEXT, nullable=True)
    
    # Pricing (AM11)
    ingredient_cost_submitted = db.Column(NUMERIC(10,2), nullable=True)
    dispensing_fee_submitted = db.Column(NUMERIC(10,2), nullable=True)
    patient_paid_amount_submitted = db.Column(NUMERIC(10,2), nullable=True)
    usual_and_customary_charge = db.Column(NUMERIC(10,2), nullable=True)
    gross_amount_due = db.Column(NUMERIC(10,2), nullable=True)
    basis_of_cost_determination = db.Column(TEXT, nullable=True)
    
    # Prescriber Information (AM03)
    prescriber_id_qualifier = db.Column(TEXT, nullable=True)
    prescriber_id = db.Column(TEXT, nullable=True)
    prescriber_last_name = db.Column(TEXT, nullable=True)
    prescriber_phone_number = db.Column(TEXT, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Claim {self.claim_id}: Member {self.member_id}>'