
# The Create_multi_claim_gpt function will be used to create an array of prompts to specify what is needed in test claims that can be created using the create_claim_gpt function.

# This function uses the new structured outputs feature of OpenAI's GPT-4o-mini API to create an array of prompts that can be used to create test claims. Make sure that all fields requested in the array of prompts are listed as required in the schema requested.

# Parameters: take in two parameters (both optional). The first is a chatgpt prompt specifying what test claims are needed. The second parameter is a member_database_id that is used to specify which member the claims will be created for. If no member_database_id is provided, the claims will be created for a random member.

# Return: Returns a JSON object with an array of prompts that have specifications for individual claims to create a veriety of test scenarios.

import os, sys, json
from openai import OpenAI
import concurrent.futures
from flask import current_app

# Add the root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Now we can import from other directories
from members.get_member import get_member
from claims.create_claim_gpt import create_claim_gpt

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def create_claim_wrapper(args):
    member_database_id, prompt, index, app = args
    with app.app_context():
        try:
            result = create_claim_gpt(
                member_database_id=member_database_id,
                prompt=prompt
            )
            print(f"Claim {index + 1}: Success")
            return result
        except Exception as e:
            print(f"Claim {index + 1}: Error - {str(e)}")
            return None

def create_multi_claims_gpt(prompt: str = None, member_database_id: int = None):
    try:
        app = current_app._get_current_object()
        # Set default empty prompt if none provided
        prompt = prompt or ""

        # Get member data using get_member function (will return random member if no ID provided)
        member_data = get_member(member_database_id)
        if "error" in member_data:
            raise ValueError(f"Error getting member data: {member_data['error']}")

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an assistant that creates specifications for pharmacy insurance test claims. Generate an array of detailed prompts that can be used to create diverse test scenarios."
                },
                {
                    "role": "user",
                    "content": f"""Create an array of claim specifications based on this prompt: {prompt} . Make sure that the number of claims in the array of claim_specification_prompts exactly matches what was requested. If the prompt above requests N claims, your final array must contain exactly N claims. Do not include fewer or more."

.
                    {f'Consider member demographics: {member_data}' if member_data else 'Create diverse scenarios for a generic person that has health insurance from their employer.'}"""
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "claim_prompt_schema",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "claim_specification_prompts": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "create_claim_prompt": {
                                            "type": "string",
                                            "description": "Prompt that contains all of the detail needed to create the claim. Do not inclued member information, but instead focus on information about the individual claim and any additional details specified in the prompt"
                                        }
                                    },
                                    "required": ["create_claim_prompt"],
                                    "additionalProperties": False
                                },
                                "description": "List of claim descriptions and ChatGPT prompts to create the claims. Make sure that the amount of claims in the array exactly matches the number of claims specified in the prompt."
                            }
                        },
                        "required": ["claim_specification_prompts"],
                        "additionalProperties": False
                    }
                }
            }
        }

        response = client.chat.completions.create(**payload)
        result = json.loads(response.choices[0].message.content)

        # Prepare arguments for parallel processing
        claim_args = [
            (member_database_id, spec['create_claim_prompt'], i, app) 
            for i, spec in enumerate(result['claim_specification_prompts'])
        ]

        print(f"\nAttempting to create {len(claim_args)} claims...")

        # Create claims in parallel
        created_claims = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = list(executor.map(create_claim_wrapper, claim_args))
            created_claims = [claim for claim in futures if claim is not None]

        # Add created claims to result
        result['created_claims'] = created_claims

        print(f"\nCreated {len(created_claims)} out of {len(claim_args)} claims successfully")
        return result

    except Exception as e:
        print(f"Error in create_multi_claims_gpt: {str(e)}")
        raise e