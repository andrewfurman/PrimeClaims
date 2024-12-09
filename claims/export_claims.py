# dysfunction will export all claims in the claims table, along with all of the membership information for the member related to this claim the claims should be joined to the member table using the member database ID field on both tables.

import pandas as pd
import os
from datetime import datetime
import tempfile
from .claim_model import Claim
from members.member_model import Member
from sqlalchemy import inspect

def export_claims():
    try:
        # Query claims with member join
        claims = Claim.query.join(Member).all()
        
        # Get all column names from both models
        claim_columns = [c.key for c in inspect(Claim).columns]
        member_columns = [c.key for c in inspect(Member).columns]
        
        # Convert to list of dictionaries
        claim_data = []
        for claim in claims:
            claim_dict = {}
            
            # Add all claim fields with 'claim_' prefix
            for col in claim_columns:
                value = getattr(claim, col)
                # Convert timezone-aware datetime to naive
                if isinstance(value, datetime):
                    value = value.replace(tzinfo=None)
                claim_dict[f'claim_{col}'] = value
                
            # Add all member fields with 'member_' prefix
            for col in member_columns:
                value = getattr(claim.member, col)
                # Convert timezone-aware datetime to naive
                if isinstance(value, datetime):
                    value = value.replace(tzinfo=None)
                claim_dict[f'member_{col}'] = value
            
            claim_data.append(claim_dict)
        
        # Create DataFrame
        df = pd.DataFrame(claim_data)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'claims_export_{timestamp}.xlsx'
        
        # Create temporary file
        temp_dir = tempfile.mkdtemp()
        filepath = os.path.join(temp_dir, filename)
        
        # Export to Excel
        writer = pd.ExcelWriter(filepath, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Claims')
        writer.close()
        
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            return filepath
        else:
            raise Exception("File was not created successfully")
            
    except Exception as e:
        print(f"Error in export_claims: {str(e)}")
        raise