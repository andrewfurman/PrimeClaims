# Create claim gpt (member.database_id int, string prompt) 

# dysfunction will take in the database ID of a member along with a prompt, which is just a string as parameters and will then call the ChatGPT API to request all of the data. Fields needed to create a new claim in the claims table.

import os, sys, json
from openai import OpenAI
from datetime import datetime
from members.get_member import get_member

# Add root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Now we can import from other directories
from claims.claim_model import db, Claim
from members.member_model import Member

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def create_claim_gpt(member_database_id: int = None, prompt: str = None):
    # Set default empty prompt if none provided
    prompt = prompt or ""

    # Get member data using existing get_member function
    member_data = get_member(member_database_id)
    if "error" in member_data:
        raise ValueError(f"Error getting member data: {member_data['error']}")

    member_database_id = member_data['database_id']

    payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "system",
            "content": "You are an assistant that creates pharmacy insurance claims based on provided information. Generate only valid pharmacy claim data that matches the provided information. Include appropriate service provider IDs, diagnosis codes, and pricing information that would be typical for pharmacy claims."
        },
        {
            "role": "user",
            "content": f"""Create the data for a claim that adheres to the requirements in this prompt: {prompt}
        Make sure the claim you're creating makes sense for the person listed below based on their demographics and insurance information:
        {member_data}"""
        }
    ],
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "claim_data",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "claim": {
                        "type": "object",
                        "properties": {
                            "member_id": {
                                "type": "integer",
                                "description": "Internal database identifier for the member. Not to be confused with the NCPDP Member ID/Cardholder ID. Example: 12345"
                            },
                            "service_provider_id_qualifier": {
                                "type": "string",
                                "description": "NCPDP field identifying type of pharmacy ID being submitted. Common values: '01' = NPI, '05' = Medicaid ID, '07' = NCPDP Provider ID, '08' = State License. Example: '01'"
                            },
                            "service_provider_id": {
                                "type": "string",
                                "description": "Unique identifier for the dispensing pharmacy. If NPI, must be 10 digits. Example NPI: '1234567890', Example NCPDP: 'AB12345'"
                            },
                            "diagnosis_code_qualifier": {
                                "type": "string",
                                "description": "Indicates diagnosis code format. '01' = ICD-9, '02' = ICD-10. Use '02' for ICD-10 per guide. Example: '02'"
                            },
                            "diagnosis_code": {
                                "type": "string",
                                "description": "ICD-10 or ICD-9 code justifying medical necessity. Must match qualifier format. Example ICD-10: 'E11.9' (Type 2 Diabetes)"
                            },
                            "clinical_information": {
                                "type": "string",
                                "description": "Free-form text containing relevant patient clinical data, often used for prior authorization or step therapy documentation. Example: 'Patient failed formulary alternative lisinopril due to cough'"
                            },
                            "prescription_service_reference_number": {
                                "type": "string",
                                "description": "Unique prescription number assigned by pharmacy. Maximum 12 characters, must be unique per pharmacy location. Example: 'RX123456789'"
                            },
                            "product_service_id": {
                                "type": "string",
                                "description": "Typically the NDC code but can include compound codes. 11 digits without hyphens for NDC. Example NDC: '00071015523'"
                            },
                            "quantity_dispensed": {
                                "type": "integer",
                                "description": "Actual quantity of drug dispensed. For tablets/capsules, must be whole numbers. For liquids/creams can include up to 3 decimal places. Example: 30"
                            },
                            "fill_number": {
                                "type": "integer",
                                "description": "Sequential number indicating fill number of the prescription. '0' = new, '1-99' = refill number. Example: 0 (new), 1 (first refill)"
                            },
                            "ndc_number": {
                                "type": "string",
                                "description": "11-digit National Drug Code identifying specific manufacturer, product, and package size. Must be a valid FDA NDC. Example: '00071015523' (Lipitor 10mg tablets)"
                            },
                            "days_supply": {
                                "type": "integer",
                                "description": "Number of days the dispensed quantity should last based on prescribed directions. Must be >0 and typically ≤90. Example: 30"
                            },
                            "dispense_as_written": {
                                "type": "boolean",
                                "description": "DAW code indicator. True = DAW 1 (Physician written DAW), False = DAW 0 (No product selection indicated). Example: true"
                            },
                            "date_prescription_written": {
                                "type": "string",
                                "description": "Date prescriber wrote the prescription. Cannot be a future date, typically within last year. Format: YYYY-MM-DD. Example: '2024-01-15'"
                            },
                            "prescription_origin_code": {
                                "type": "string",
                                "description": "Code indicating prescription source. '0' = Not specified, '1' = Written, '2' = Telephone, '3' = Electronic, '4' = Facsimile, '5' = Pharmacy. Example: '3'"
                            },
                            "ingredient_cost_submitted": {
                                "type": "number",
                                "description": "Pharmacy's submitted cost for the drug, excluding dispensing fee. Up to 2 decimal places. Example: 105.99"
                            },
                            "dispensing_fee_submitted": {
                                "type": "number",
                                "description": "Fee charged by pharmacy for professional services. Typically $0.01-$15.00. Up to 2 decimal places. Example: 1.50"
                            },
                            "patient_paid_amount_submitted": {
                                "type": "number",
                                "description": "Amount collected from patient (copay/coinsurance). Up to 2 decimal places. Must be ≥0.00. Example: 10.00"
                            },
                            "prescriber_id_qualifier": {
                                "type": "string",
                                "description": "Code identifying type of prescriber ID. '01' = NPI (most common), '12' = DEA, '14' = State License. Example: '01'"
                            },
                            "prescriber_id": {
                                "type": "string",
                                "description": "Prescriber's ID matching qualifier type. NPI must be 10 digits, DEA must be 9 characters. Example NPI: '2958205828'"
                            },
                            "prescriber_last_name": {
                                "type": "string",
                                "description": "Prescriber's last name as registered with their NPI/DEA. Max 35 chars. Generate unique last name unless specified. Example: 'Lombardi'"
                            },
                            "prescriber_phone_number": {
                                "type": "string",
                                "description": "Prescriber's contact number. 10 digits, no formatting. Example: '8003250395'"
                            },
                            "other_payer_id_qualifier": {
                                "type": "string",
                                "description": "Code indicating type of other payer ID. '03' = BIN. Example: '03'"
                            },
                            "other_payer_id": {
                                "type": "string",
                                "description": "Identifier assigned by the other payer, e.g., a BIN. Example: '003858'"
                            },
                            "other_payer_amount_paid": {
                                "type": "number",
                                "description": "The dollar amount paid by the other payer for the claim. Example: 50.00"
                            },
                            "prescription_service_reference_number_qualifier": {
                                "type": "string",
                                "description": "Code indicating type of reference number for prescription service. '1' represents pharmacy's prescription number. Example: '1'"
                            },
                            "product_service_id_qualifier": {
                                "type": "string",
                                "description": "Code specifying the product/service identifier type. '03' = NDC. Example: '03'"
                            },
                            "other_coverage_code": {
                                "type": "string",
                                "description": "Code indicating existence/type of other coverage. '1' = no other coverage. Example: '1'"
                            },
                            "special_packaging_indicator": {
                                "type": "boolean",
                                "description": "Indicates if special packaging was used. false = no special packaging. Example: false"
                            },
                            "unit_of_measure": {
                                "type": "string",
                                "description": "Unit of measure for quantity dispensed. 'EA' = each. Example: 'EA'"
                            },
                            "usual_and_customary_charge": {
                                "type": "number",
                                "description": "Pharmacy's usual and customary charge to the public. Example: 125.99"
                            },
                            "gross_amount_due": {
                                "type": "number",
                                "description": "Total amount due from all payers and the patient before adjustments. Example: 135.99"
                            },
                            "basis_of_cost_determination": {
                                "type": "string",
                                "description": "Code indicating cost determination method. '01' = AWP. Example: '01'"
                            },

                            "drug_name": {
                                "type": "string",
                                "description": "The name of the drug dispensed. According to the guide: Use a known drug name, e.g., 'Amoxicillin'."
                            },
                            "drug_strength": {
                                "type": "string",
                                "description": "The strength or potency of the drug. From the guide example: '125MG/5ML'."
                            },
                            "drug_form": {
                                "type": "string",
                                "description": "The dosage form of the drug. From the guide example: 'Suspension Reconstituted'."
                            },
                            "daw_code": {
                                "type": "string",
                                "description": "The Dispense as Written code (0–9) indicating prescriber/patient instructions on substitution. Possible values per the guide:\n" +
                                               "0: No product selection indicated\n" +
                                               "1: Substitution not allowed by prescriber\n" +
                                               "2: Substitution allowed - patient requested product dispensed\n" +
                                               "3: Substitution allowed - pharmacy selected product\n" +
                                               "4: Substitution allowed - generic not in stock\n" +
                                               "5: Substitution allowed - brand dispensed as generic\n" +
                                               "6: Undefined\n" +
                                               "7: Substitution not allowed - brand mandated by law\n" +
                                               "8: Substitution not allowed - generic not available in marketplace\n" +
                                               "9: Undefined"
                            },
                            "professional_service_code": {
                                "type": "string",
                                "description": "Code representing pharmacist’s professional service. Used for vaccine administration fees or cDUR edits (reject 88). Possible values per guide include:\n" +
                                               "00 - No intervention\n" +
                                               "MA - Medication Administration\n" +
                                               "M0 - Prescriber Consultation\n" +
                                               "MR - Medication Review\n" +
                                               "P0 - Patient Consultation\n" +
                                               "AS - Patient Assessment\n" +
                                               "PE - Patient Education\n" +
                                               "PH - Patient Medication History\n" +
                                               "PM - Patient Monitoring\n" +
                                               "PT - Perform Laboratory Test\n" +
                                               "CC - Coordination of Care\n" +
                                               "DE - Dosing Evaluation\n" +
                                               "FE - Formulary Enforcement\n" +
                                               "GP - Generic Product Selection\n" +
                                               "R0 - Consultation with Other Pharmacist\n" +
                                               "RT - Recommend Laboratory Test\n" +
                                               "SC - Self-Care Consultation\n" +
                                               "SW - Literature Search\n" +
                                               "TC - Payer/Processor Consultation\n" +
                                               "Use codes as appropriate to the intervention performed."
                            },
                            "dur_pps_level_of_effort_value": {
                                "type": "string",
                                "description": "Indicates complexity level of pharmacist’s professional service. Possible values:\n" +
                                               "11: Level 1 (1-4 min, minimal complexity)\n" +
                                               "12: Level 2 (5-14 min, low complexity)\n" +
                                               "13: Level 3 (15-29 min, moderate complexity)\n" +
                                               "14: Level 4 (30-59 min, high complexity)\n" +
                                               "15: Level 5 (≥60 min, highest complexity)."
                            },
                            "reason_for_service_code": {
                                "type": "string",
                                "description": "Explains why a particular action was taken in response to a DUR issue or override. Possible values per guide:\n" +
                                               "NA (Drug Not Available), NF (Non-Formulary), NN (Unnecessary Drug), NP (New Patient), NR (Lactation/Nursing Interaction), NS (Insufficient Quantity), OH (Alcohol Conflict), PA (Drug-Age), PC (Patient Concern), PG (Drug-Pregnancy), PH (Preventive Health), PN (Prescriber Consultation), PP (Plan Protocol), PR (Prior Adverse Reaction), PS (Product Selection), RF (Provider Referral), SC (Suboptimal Compliance), SD (Suboptimal Drug/Indication), SE (Side Effect), SF (Suboptimal Dosage Form), SR (Suboptimal Regimen), SX (Drug-Gender), TD (Therapeutic), TN (Lab Test Needed), TP (Payer/Processor Question). Choose the code that best describes the scenario."
                            },
                            "submission_clarification_code": {
                                "type": "string",
                                "description": "Provides additional context about the submission (e.g., emergency fill, lost medication). Use codes as directed by payer or scenario. Example: '52' might indicate a specific clarification event. Include any known SCC code that applies."
                            },
                            "result_of_service_code": {
                                "type": "string",
                                "description": "Indicates outcome after identifying a conflict or performing a professional service. Possible values:\n" +
                                               "00: Not specified\n" +
                                               "1A: Filled As Is, False Positive\n" +
                                               "1B: Filled Prescription As Is\n" +
                                               "1C: Filled With Different Dose\n" +
                                               "1D: Filled With Different Directions\n" +
                                               "1E: Filled With Different Drug\n" +
                                               "1F: Filled With Different Quantity\n" +
                                               "1G: Filled With Prescriber Approval\n" +
                                               "1H: Brand-to-Generic Change\n" +
                                               "1J: Rx-to-OTC Change\n" +
                                               "1K: Filled with Different Dosage Form\n" +
                                               "2A: Prescription Not Filled\n" +
                                               "2B: Not Filled, Directions Clarified\n" +
                                               "3A: Recommendation Accepted\n" +
                                               "3B: Recommendation Not Accepted\n" +
                                               "3C: Discontinued Drug\n" +
                                               "3D: Regimen Changed\n" +
                                               "3E: Therapy Changed\n" +
                                               "3F: Therapy Changed - cost increase acknowledged\n" +
                                               "3G: Therapy Unchanged\n" +
                                               "3H: Follow-Up/Report\n" +
                                               "3J: Patient Referral\n" +
                                               "3K: Instructions Understood\n" +
                                               "3M: Compliance Aid Provided\n" +
                                               "3N: Medication Administered."
                            },
                            "vaccine_administration_reimbursement_amount": {
                                "type": "number",
                                "description": "The amount requested for administering a vaccine. Use this when the provider supplies and administers a vaccine. Example: 25.48"
                            },
                            "other_payer_patient_responsibility_amount": {
                                "type": "number",
                                "description": "Amount of cost responsibility patient had under another payer. For scenarios where patient paid an amount to another payer. Example: 10.00"
                            },
                            "other_payer_reject_code": {
                                "type": "string",
                                "description": "The reject code returned by another payer when the claim is denied. For example, 'MR' could indicate a specific denial reason."
                            },
                            "other_payer_qualifier": {
                                "type": "string",
                                "description": "Identifies the type of other payer ID submitted. Use '03' for BIN. Example: '03'"
                            },
                            "place_of_service": {
                                "type": "string",
                                "description": "Location where the service was performed. For Part B drugs: doctor's office or hospital outpatient. For Part D drugs: pharmacy. Example: 'doctor’s office', 'hospital outpatient', or 'pharmacy' as appropriate."
                            },
                            "pharmacy_service_type": {
                                "type": "string",
                                "description": "Type of pharmacy dispensing the prescription. Codes per guide:\n" +
                                               "01: Community/retail\n" +
                                               "02: Compounding\n" +
                                               "03: Home infusion\n" +
                                               "04: Institutional\n" +
                                               "05: Long-term care (bypasses certain opioid restrictions)\n" +
                                               "06: Mail order\n" +
                                               "07: MCO pharmacy\n" +
                                               "08: Specialty care\n" +
                                               "99: Other"
                            },
                            "patient_residence_code": {
                                "type": "string",
                                "description": "Code indicating patient’s residence at dispensing. Codes per guide:\n" +
                                               "0: Not specified\n" +
                                               "1: Home\n" +
                                               "3: Nursing home/facility\n" +
                                               "4: Assisted living\n" +
                                               "6: Group home\n" +
                                               "9: Intermediate care facility\n" +
                                               "11: Hospice"
                            }
                        },
                        "required": [
                            "member_id",
                            "service_provider_id_qualifier",
                            "service_provider_id",
                            "other_payer_id_qualifier",
                            "other_payer_id",
                            "other_payer_amount_paid",
                            "diagnosis_code_qualifier",
                            "diagnosis_code",
                            "clinical_information",
                            "prescription_service_reference_number_qualifier",
                            "prescription_service_reference_number",
                            "product_service_id_qualifier",
                            "product_service_id",
                            "quantity_dispensed",
                            "fill_number",
                            "ndc_number",
                            "days_supply",
                            "dispense_as_written",
                            "date_prescription_written",
                            "prescription_origin_code",
                            "other_coverage_code",
                            "special_packaging_indicator",
                            "unit_of_measure",
                            "ingredient_cost_submitted",
                            "dispensing_fee_submitted",
                            "patient_paid_amount_submitted",
                            "usual_and_customary_charge",
                            "gross_amount_due",
                            "basis_of_cost_determination",
                            "prescriber_id_qualifier",
                            "prescriber_id",
                            "prescriber_last_name",
                            "prescriber_phone_number",
                            "drug_name",
                            "drug_strength",
                            "drug_form",
                            "daw_code",
                            "professional_service_code",
                            "dur_pps_level_of_effort_value",
                            "reason_for_service_code",
                            "submission_clarification_code",
                            "result_of_service_code",
                            "vaccine_administration_reimbursement_amount",
                            "other_payer_patient_responsibility_amount",
                            "other_payer_reject_code",
                            "other_payer_qualifier",
                            "place_of_service",
                            "pharmacy_service_type",
                            "patient_residence_code"
                        ],
                        "additionalProperties": False
                    }
                },
                "required": ["claim"],
                "additionalProperties": False
            }
        }
    }
}

    response = client.chat.completions.create(**payload)
    claim_data = json.loads(response.choices[0].message.content)['claim']
    
    # Ensure member_id is set to the provided database_id
    claim_data['member_id'] = member_database_id

    new_claim = Claim(**claim_data)
    db.session.add(new_claim)
    db.session.commit()
    return claim_data

if __name__ == "__main__":
    test_prompt = """Create a claim for a 30-day supply of Lisinopril 10mg tablets. 
    The prescription was written on 2024-01-15 and filled at CVS Pharmacy."""
    
    result = create_claim_gpt(3, test_prompt)
    print("Created claim:", json.dumps(result, indent=2))