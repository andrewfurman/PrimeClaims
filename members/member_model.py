# this is a model for the members table that contains info about people that have Phamacy Insurance Coverage

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import TEXT

db = SQLAlchemy()

class Member(db.Model):
    __tablename__ = 'members'
    
    # Primary and Member IDs
    database_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(TEXT, nullable=True, unique=True)
    
    # Personal Information
    first_name = db.Column(TEXT, nullable=True)
    last_name = db.Column(TEXT, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.CHAR(1), nullable=True)
    address = db.Column(TEXT, nullable=True)
    city = db.Column(TEXT, nullable=True)
    state = db.Column(TEXT, nullable=True)
    zip_code = db.Column(TEXT, nullable=True)
    phone_number = db.Column(TEXT, nullable=True)
    
    # Insurance Information
    insurance_id_number = db.Column(TEXT, nullable=True)
    group_number = db.Column(TEXT, nullable=True)
    
    # Pharmacy Benefit Information
    rx_bin = db.Column(TEXT, nullable=True)
    rx_group = db.Column(TEXT, nullable=True)
    rx_pcn = db.Column(TEXT, nullable=True)
    
    # Copay Tiers
    copay_1_generic = db.Column(TEXT, nullable=True)
    copay_2_preferred = db.Column(TEXT, nullable=True)
    copay_3_non_preferred = db.Column(TEXT, nullable=True)
    copay_4_specialty = db.Column(TEXT, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    claims = db.relationship('Claim', 
        cascade="all, delete-orphan", 
        passive_deletes=True,
        backref='member')

    def __repr__(self):
        return f'<Member {self.database_id}: {self.member_id} - {self.first_name} {self.last_name}>'
