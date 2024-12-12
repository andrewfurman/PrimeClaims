# the create member GPT function will take in a single string variable, which is a prompt with specifications needed for creating a member. Then the prompt will be sent to ChatGPT and ChatGPT will produce a JSON payload. This chase on payload can then be used to create a new member in the member database table.

import os
import json
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .member_model import Member, db

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def create_member_gpt(prompt):
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "You are an assistant that creates member profiles for pharmacy insurance coverage based on provided information. Generate only valid insurance-related data that matches the provided information.  These profiles will be used as examples of members with coverage from Prime Therapeutics. Obey the prompt, but if limited information is given, create coverage similar to what is seen here:  ..."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "member_profile",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "member_profile": {
                            "type": "object",
                            "properties": {
                                "member_id": {
                                    "type": "string",
                                    "description": "12 random non sequential digits"
                                },
                                "first_name": {
                                    "type": "string",
                                    "description": "Member's legal first name. If no name is given in the prompt, use a common name, but do not use the most common names like John Jane Liam Clara Lucas unless specified in the prompt. If the prompt expicitely requests a common name, please use that name provided in the prompt"
                                },
                                "last_name": {
                                    "type": "string",
                                    "description": "Member's legal last name. Do not use the most common names like Smith or Jones unless requested in the prompt. If the prompt expicitely requests a name like Smith, please use that name provided in the prompt"
                                },
                                "date_of_birth": {
                                    "type": "string",
                                    "description": "Member's date of birth in YYYY-MM-DD format. Pick a random date in the year, not use january 1st unless specified in the prompt, If the prompt expicitely requests a January 1st birthday, please use that birthday provided in the prompt"
                                },
                                "gender": {
                                    "type": "string",
                                    "description": "Member's gender coded as single character (M/F/X)"
                                },
                                "address": {
                                    "type": "string",
                                    "description": "Member's street address. make this line look like a real street in the city selected, not 123 Main St. Do not use Maple, Park, Elmwood, Brook, Willow as street names. Make sure to select random street number, not sequential numbers like 456, 9876 or 1234. Ignore this if the prompt explicitly requests a specific street address"
                                },
                                "city": {
                                    "type": "string",
                                    "description": "City of member's residence. If the city or location isn't specified in the prompt, make sure that the city is in one of these counties unless specified otherwise in the prompt: Albany Bronx Broome Columbia Delaware Dutchess Fulton Greene Kings (Brooklyn) Montgomery Nassau New York (Manhattan) Orange Otsego Putnam Queens Rensselaer Richmond (Staten Island) Rockland Saratoga Schenectady Schoharie Suffolk Sullivan Ulster Warren Washington Westchester. If the city or location is specified in the prompt, ignore the counties and just use that."
                                },
                                "state": {
                                    "type": "string",
                                    "description": "Two-letter state code of member's residence"
                                },
                                "zip_code": {
                                    "type": "string",
                                    "description": "Postal zip code of member's residence"
                                },
                                "phone_number": {
                                    "type": "string",
                                    "description": "Member's contact phone number"
                                },
                                "insurance_id_number": {
                                    "type": "string",
                                    "description": "Primary insurance identification number. Example: '2435898157' "
                                },
                                "group_number": {
                                    "type": "string",
                                    "description": "Insurance group number identifying the benefit plan. Example: 23584"
                                },
                                "rx_bin": {
                                    "type": "string",
                                    "description": "Pharmacy benefit BIN (Bank Identification Number). Example: 004336."
                                },
                                "rx_group": {
                                    "type": "string",
                                    "description": "Pharmacy benefit group identifier. Example: PRPLAT"
                                },
                                "rx_pcn": {
                                    "type": "string",
                                    "description": "Pharmacy benefit Processor Control Number. Example PCN: 'ADV' "
                                },
                                "copay_1_generic": {
                                    "type": "string",
                                    "description": "Copay amount for generic medications (Tier 1). Example: '$10'"
                                },
                                "copay_2_preferred": {
                                    "type": "string",
                                    "description": "Copay amount for preferred brand medications (Tier 2) Example: '$30'"
                                },
                                "copay_3_non_preferred": {
                                    "type": "string",
                                    "description": "Copay amount for non-preferred brand medications (Tier 3) Example: '$50'"
                                },
                                "copay_4_specialty": {
                                    "type": "string",
                                    "description": "Copay amount for specialty medications (Tier 4).  Example: '$100'"
                                }
                            },
                            "required": [
                                "member_id", "first_name", "last_name", "date_of_birth", 
                                "gender", "address", "city", "state", "zip_code", 
                                "phone_number", "insurance_id_number", "group_number",
                                "rx_bin", "rx_group", "rx_pcn", "copay_1_generic",
                                "copay_2_preferred", "copay_3_non_preferred", "copay_4_specialty"
                            ],
                            "additionalProperties": False
                        }
                    },
                    "required": ["member_profile"],
                    "additionalProperties": False
                }
            }
        }
    }

    response = client.chat.completions.create(**payload)
    member_data = json.loads(response.choices[0].message.content)['member_profile']
  
    # Use the global db instance
    new_member = Member(**member_data)
    db.session.add(new_member)
    db.session.commit()
    return member_data

if __name__ == "__main__":
    test_prompt = """Create a member profile for a random person."""

    result = create_member_gpt(test_prompt)
    print("Created member:", json.dumps(result, indent=2))