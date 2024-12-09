#this function will export all of the members in the member table with all columns to excel. the function will have no parameters and will return an excel xlsx file with all of the members using a readily available python library.

import pandas as pd
import os
from datetime import datetime
from .member_model import Member
import tempfile

def export_members():
    try:
        # Query all members
        members = Member.query.all()
        
        # Convert to list of dictionaries
        member_data = []
        for member in members:
            member_dict = {
                'Member ID': member.member_id,
                'First Name': member.first_name,
                'Last Name': member.last_name,
                'Date of Birth': member.date_of_birth,
                'Gender': member.gender,
                'Address': member.address,
                'City': member.city,
                'State': member.state,
                'Zip Code': member.zip_code,
                'Phone Number': member.phone_number,
                'Insurance ID': member.insurance_id_number,
                'Group Number': member.group_number,
                'RX BIN': member.rx_bin,
                'RX Group': member.rx_group,
                'RX PCN': member.rx_pcn,
                'Generic Copay': member.copay_1_generic,
                'Preferred Copay': member.copay_2_preferred,
                'Non-Preferred Copay': member.copay_3_non_preferred,
                'Specialty Copay': member.copay_4_specialty
            }
            member_data.append(member_dict)
        
        # Create DataFrame
        df = pd.DataFrame(member_data)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'members_export_{timestamp}.xlsx'
        
        # Create temporary file
        temp_dir = tempfile.mkdtemp()
        filepath = os.path.join(temp_dir, filename)
        
        # Export to Excel
        writer = pd.ExcelWriter(filepath, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Members')
        writer.close()
        
        # Verify file exists and has content
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            return filepath
        else:
            raise Exception("File was not created successfully")
            
    except Exception as e:
        print(f"Error in export_members: {str(e)}")
        raise