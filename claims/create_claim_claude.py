# Create claim gpt (member.database_id int, string prompt) 

# This function will take in the database ID of a member along with a prompt, which is just a string as parameters and will then call the Anthropic Claude API to request all of the data. Fields needed to create a new claim in the claims table.

# This function will work exactly the same as the create_claim_gpt function in ../create_claim_gpt.py, except it will use the Claude API instead of GPT-4o-mini. This function will use the "claude-3-5-haiku-latest" as the model.

import os, sys, json
import anthropic
from datetime import datetime

# Add root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Now we can import from other directories
from claims.claim_model import db, Claim
from members.member_model import Member
from members.get_member import get_member


client = anthropic.Client(api_key=os.environ['ANTHROPIC_API_KEY'])

def create_claim_claude(member_database_id: int = None, prompt: str = None):
    # Set default empty prompt if none provided
    prompt = prompt or ""

    # Get member data using existing get_member function
    member_data = get_member(member_database_id)
    if "error" in member_data:
        raise ValueError(f"Error getting member data: {member_data['error']}")

    member_database_id = member_data['database_id']

    tools = [{
        "name": "create_claim",
        "description": "Creates pharmacy insurance claims based on provided information",
        "input_schema": {
            "type": "object",
            "properties": {
                "claim": {
                    "type": "object",
                    "properties": {
                        "member_id": {"type": "integer", "description": "Internal database identifier for the member"},
                        "service_provider_id_qualifier": {"type": "string", "description": "NCPDP field identifying type of pharmacy ID"},
                        "service_provider_id": {"type": "string", "description": "Unique identifier for the dispensing pharmacy"},
                        "diagnosis_code_qualifier": {"type": "string", "description": "Indicates diagnosis code format"},
                        "diagnosis_code": {"type": "string", "description": "ICD-10 or ICD-9 code"},
                        "clinical_information": {"type": "string", "description": "Relevant patient clinical data"},
                        "prescription_service_reference_number": {"type": "string", "description": "Unique prescription number"},
                        "product_service_id": {"type": "string", "description": "NDC code or compound code"},
                        "quantity_dispensed": {"type": "integer", "description": "Actual quantity of drug dispensed"},
                        "fill_number": {"type": "integer", "description": "Sequential number indicating fill number"},
                        "ndc_number": {"type": "string", "description": "11-digit National Drug Code"},
                        "days_supply": {"type": "integer", "description": "Number of days the dispensed quantity should last"},
                        "dispense_as_written": {"type": "boolean", "description": "DAW code indicator"},
                        "date_prescription_written": {"type": "string", "description": "Date prescriber wrote the prescription"},
                        "prescription_origin_code": {"type": "string", "description": "Code indicating prescription source"},
                        "ingredient_cost_submitted": {"type": "number", "description": "Pharmacy's submitted cost for the drug"},
                        "dispensing_fee_submitted": {"type": "number", "description": "Fee charged by pharmacy"},
                        "patient_paid_amount_submitted": {"type": "number", "description": "Amount collected from patient"},
                        "prescriber_id_qualifier": {"type": "string", "description": "Code identifying type of prescriber ID"},
                        "prescriber_id": {"type": "string", "description": "Prescriber's ID matching qualifier type"},
                        "prescriber_last_name": {"type": "string", "description": "Prescriber's last name"},
                        "prescriber_phone_number": {"type": "string", "description": "Prescriber's contact number"},
                        "other_payer_id_qualifier": {"type": "string", "description": "Code indicating type of other payer ID"},
                        "other_payer_id": {"type": "string", "description": "Identifier assigned by the other payer"},
                        "other_payer_amount_paid": {"type": "number", "description": "Amount paid by other payer"},
                        "prescription_service_reference_number_qualifier": {"type": "string", "description": "Code for prescription reference type"},
                        "product_service_id_qualifier": {"type": "string", "description": "Code for product/service identifier type"},
                        "other_coverage_code": {"type": "string", "description": "Code indicating other coverage"},
                        "special_packaging_indicator": {"type": "boolean", "description": "Indicates special packaging use"},
                        "unit_of_measure": {"type": "string", "description": "Unit of measure for quantity"},
                        "usual_and_customary_charge": {"type": "number", "description": "Pharmacy's usual charge"},
                        "gross_amount_due": {"type": "number", "description": "Total amount due before adjustments"},
                        "basis_of_cost_determination": {"type": "string", "description": "Code for cost determination method"},
                        "drug_name": {"type": "string", "description": "Name of drug dispensed"},
                        "drug_strength": {"type": "string", "description": "Strength of the drug"},
                        "drug_form": {"type": "string", "description": "Dosage form of the drug"},
                        "daw_code": {"type": "string", "description": "Dispense as Written code"},
                        "professional_service_code": {"type": "string", "description": "Code for pharmacist's service"},
                        "dur_pps_level_of_effort_value": {"type": "string", "description": "Complexity level of service"},
                        "reason_for_service_code": {"type": "string", "description": "Reason for service/action taken"},
                        "submission_clarification_code": {"type": "string", "description": "Additional context about submission"},
                        "result_of_service_code": {"type": "string", "description": "Outcome after service/conflict"},
                        "vaccine_administration_reimbursement_amount": {"type": "number", "description": "Amount for vaccine administration"},
                        "other_payer_patient_responsibility_amount": {"type": "number", "description": "Patient responsibility to other payer"},
                        "other_payer_reject_code": {"type": "string", "description": "Other payer's reject code"},
                        "other_payer_qualifier": {"type": "string", "description": "Type of other payer ID"},
                        "place_of_service": {"type": "string", "description": "Location of service"},
                        "pharmacy_service_type": {"type": "string", "description": "Type of pharmacy service"},
                        "patient_residence_code": {"type": "string", "description": "Code for patient's residence"}
                    },
                    "required": [
                        "member_id", "service_provider_id_qualifier", "service_provider_id",
                        "other_payer_id_qualifier", "other_payer_id", "other_payer_amount_paid",
                        "diagnosis_code_qualifier", "diagnosis_code", "clinical_information",
                        "prescription_service_reference_number_qualifier", "prescription_service_reference_number",
                        "product_service_id_qualifier", "product_service_id", "quantity_dispensed",
                        "fill_number", "ndc_number", "days_supply", "dispense_as_written",
                        "date_prescription_written", "prescription_origin_code", "other_coverage_code",
                        "special_packaging_indicator", "unit_of_measure", "ingredient_cost_submitted",
                        "dispensing_fee_submitted", "patient_paid_amount_submitted", "usual_and_customary_charge",
                        "gross_amount_due", "basis_of_cost_determination", "prescriber_id_qualifier",
                        "prescriber_id", "prescriber_last_name", "prescriber_phone_number",
                        "drug_name", "drug_strength", "drug_form", "daw_code",
                        "professional_service_code", "dur_pps_level_of_effort_value",
                        "reason_for_service_code", "submission_clarification_code",
                        "result_of_service_code", "vaccine_administration_reimbursement_amount",
                        "other_payer_patient_responsibility_amount", "other_payer_reject_code",
                        "other_payer_qualifier", "place_of_service", "pharmacy_service_type",
                        "patient_residence_code"
                    ]
                }
            },
            "required": ["claim"]
        }
    }]

    query = f"""Create the data for a claim that adheres to the requirements in this prompt: {prompt}
    Make sure the claim you're creating makes sense for the person listed below based on their demographics and insurance information:
    {member_data}"""

    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4096,
        tools=tools,
        tool_choice={"type": "tool", "name": "create_claim"},
        messages=[{
            "role": "user", 
            "content": query
        }]
    )

    # Extract the claim data from the tool use response
    claim_data = None
    for content in response.content:
        if content.type == "tool_use" and content.name == "create_claim":
            claim_data = content.input['claim']
            break

    if not claim_data:
        raise ValueError("Failed to generate claim data")

    # Ensure member_id is set to the provided database_id
    claim_data['member_id'] = member_database_id

    # Create and save the claim
    new_claim = Claim(**claim_data)
    db.session.add(new_claim)
    db.session.commit()

    return claim_data

if __name__ == "__main__":
    # Import Flask app and set up context
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from main import app
    
    with app.app_context():
        test_prompt = """Create a claim for a 30-day supply of Lisinopril 10mg tablets. 
        The prescription was written on 2024-01-15 and filled at CVS Pharmacy."""
        
        result = create_claim_claude(3, test_prompt)
        print("Created claim:", json.dumps(result, indent=2))