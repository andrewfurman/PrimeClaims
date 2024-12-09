# create NCPDP function will have no input parameters and will return a file with a .dat extension that it appears to the NCPDP file format standards. This file will use all of the existing data in the claims database table and the member database table to populate the claims on the NCPDP file and will use placeholder hardcoded values for the transaction header information. Make sure that the transaction header has includes the date and time clearly that the file was generated at.

# the file returned should follow as 'EMBLEM NCPDP Claim File 2024-11-26 119pm.dat'

from datetime import datetime
import os
from claims.claim_model import Claim
from members.member_model import Member
import tempfile

def create_ncpdp():
    try:
        # Get all claims with related member data
        claims = Claim.query.join(Member).all()
        
        # Generate timestamp for filename
        timestamp = datetime.now()
        filename = f'EMBLEM NCPDP Claim File {timestamp.strftime("%Y-%m-%d %I%M%p")}.dat'
        
        # Create temporary directory and file path
        temp_dir = tempfile.mkdtemp()
        filepath = os.path.join(temp_dir, filename)
        
        with open(filepath, 'w') as f:
            # Write file header once
            header = (
                f"␂00{'T123456789':20}"
                f"{timestamp.strftime('%Y%m%d%H%M%S'):>15}"
                f"{'P1234567WPS0000000':>20}␃\n"
            )
            f.write(header)
            
            # Write claims
            for idx, claim in enumerate(claims, 1):
                # Insurance Segment
                insurance = (
                    f"␂G1{claim.member.insurance_id_number or '':20}"
                    f"D1B101{' ' * 8}"
                    f"{claim.service_provider_id or '':15}"
                    f"{timestamp.strftime('%Y%m%d')}0000000100\n"
                )
                
                # Member segment with null checks
                member = (
                    f"␞␜AM04␜C2{claim.member.insurance_id_number or ''}␜"
                    f"CC{claim.member.first_name or ''}␜CD{claim.member.last_name or ''}␜"
                    f"FO{claim.member.group_number or ''}␜C90␜C1{claim.member.rx_group or ''}␜"
                    f"C3001␜C62\n"
                )
                
                # Claim details with null checks and safe type conversion
                quantity = int(float(claim.quantity_dispensed)) if claim.quantity_dispensed else 0
                fill_number = int(claim.fill_number) if claim.fill_number else 0
                days_supply = int(claim.days_supply) if claim.days_supply else 0
                
                claim_details = (
                    f"␞␜AM07␜EM1␜D2{claim.prescription_service_reference_number or ''}␜"
                    f"E103␜D7{claim.ndc_number or ''}␜E7{quantity:010d}␜"
                    f"D3{fill_number:02d}␜D5{days_supply:03d}␜"
                    f"D80␜DE{claim.date_prescription_written.strftime('%Y%m%d') if claim.date_prescription_written else ''}␜"
                    f"DJ{claim.prescription_origin_code or ''}␜C8{claim.other_coverage_code or ''}␜"
                    f"DT{claim.special_packaging_indicator or ''}␜28{claim.unit_of_measure or ''}\n"
                )
                
                # Pricing with null checks and safe conversion
                pricing = (
                    f"␞␜AM11␜D9{int(float(claim.ingredient_cost_submitted or 0)*100):08d}A␜"
                    f"DC{int(float(claim.dispensing_fee_submitted or 0)*100):08d}E␜"
                    f"DX{int(float(claim.patient_paid_amount_submitted or 0)*100):08d}B␜"
                    f"DQ{int(float(claim.usual_and_customary_charge or 0)*100):08d}␜"
                    f"DU{int(float(claim.gross_amount_due or 0)*100):08d}F␜DN07\n"
                )
                
                # Prescriber with null checks
                prescriber = (
                    f"␞␜AM03␜EZ{claim.prescriber_id_qualifier or ''}␜"
                    f"DB{claim.prescriber_id or ''}␜DR{claim.prescriber_last_name or ''}␜"
                    f"PM{claim.prescriber_phone_number or ''}␃\n"
                )
                
                f.write(insurance + member + claim_details + pricing + prescriber)
            
            # Write footer
            f.write(f"␂99{timestamp.strftime('%Y%m%d%H%M')}{idx:010d}END␃\n")
        
        return filepath
        
    except Exception as e:
        print(f"Error in create_ncpdp: {str(e)}")
        raise