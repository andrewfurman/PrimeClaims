# dysfunction will return a JSON object that contains all of the information about a member that is held on the member table. It will have one optional parameter as input, which will be the member database ID. This field will be optional and if the field is not included, it will return a JSON object for a random member that is found in the database.

from .member_model import Member
import random
from sqlalchemy.sql import func

def get_member(database_id=None):
    try:
        if database_id:
            # Get specific member
            member = Member.query.filter_by(database_id=database_id).first()
        else:
            # Get random member
            member = Member.query.order_by(func.random()).first()
        
        if not member:
            return {"error": "No member found"}
            
        # Convert member data to dictionary
        member_data = {
            "database_id": member.database_id,
            "member_id": member.member_id,
            "first_name": member.first_name,
            "last_name": member.last_name,
            "date_of_birth": member.date_of_birth.isoformat() if member.date_of_birth else None,
            "gender": member.gender,
            "address": member.address,
            "city": member.city,
            "state": member.state,
            "zip_code": member.zip_code,
            "phone_number": member.phone_number,
            "insurance_id_number": member.insurance_id_number,
            "group_number": member.group_number,
            "rx_bin": member.rx_bin,
            "rx_group": member.rx_group,
            "rx_pcn": member.rx_pcn,
            "copay_1_generic": member.copay_1_generic,
            "copay_2_preferred": member.copay_2_preferred,
            "copay_3_non_preferred": member.copay_3_non_preferred,
            "copay_4_specialty": member.copay_4_specialty,
            "created_at": member.created_at.isoformat(),
            "updated_at": member.updated_at.isoformat()
        }
        
        return member_data
        
    except Exception as e:
        return {"error": str(e)}