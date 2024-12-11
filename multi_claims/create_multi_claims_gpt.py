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
    member_database_id, prompt = args
    # Create application context for this thread
    with current_app.app_context():
        try:
            return create_claim_gpt(
                member_database_id=member_database_id,
                prompt=prompt
            )
        except Exception as e:
            print(f"Error creating claim: {e}")
            return None

def create_multi_claims_gpt(prompt: str = None, member_database_id: int = None):
    # Set default empty prompt if none provided
    prompt = prompt or ""

    # Create application context for the main function
    with current_app.app_context():
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
                "content": f"""Create an array of claim specifications based on this request: {prompt}
                {f'Consider member demographics: {member_data}' if member_data else 'Create diverse scenarios for any member.'}"""
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
                            "type":
                            "array",
                            "items": {
                                "type":
                                "object",
                                "properties": {
                                    "scenario_description": {
                                        "type":
                                        "string",
                                        "description":
                                        "Description of the senario that this claim will test"
                                    },
                                    "create_claim_prompt": {
                                        "type":
                                        "string",
                                        "description":
                                        "Prompt that contains all of the detail needed to create the claim."
                                    }
                                },
                                "required": [
                                    "scenario_description", "create_claim_prompt"
                                ],
                                "additionalProperties":
                                False
                            },
                            "description":
                            "List of claim specifications and prompts to create the claims."
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

    # Call the create_claim_gpt function to create the claims using each of the prompts in the result. Include the Member_database_id in the functon call to create claims.

    # Prepare arguments for parallel processing
    claim_args = [
        (member_database_id, spec['create_claim_prompt']) 
        for spec in result['claim_specification_prompts']
    ]

    # Create claims in parallel
    created_claims = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all tasks and wait for completion
        futures = list(executor.map(create_claim_wrapper, claim_args))

        # Filter out None results from failed claims
        created_claims = [claim for claim in futures if claim is not None]

    # Add created claims to result
    result['created_claims'] = created_claims

    return result

    except Exception as e:
        print(f"Error in create_multi_claims_gpt: {str(e)}")
        raise e

if __name__ == "__main__":
    test_prompt = """Create test claims for validating prior authorization logic:
    - One claim that should pass PA requirements
    - One claim that should fail PA requirements
    - One claim for a maintenance medication"""

    result = create_multi_claims_gpt(test_prompt)
    print("Generated claim prompts:", json.dumps(result, indent=2))


# Example Output

# ~/PrimeClaims$ python multi_claims/create_multi_claims_gpt.py
# Generated claim prompts: {
#   "claim_specification_prompts": [
#     {
#       "senario_description": "This claim is for a member who has a documented history of severe asthma and is receiving a high-cost inhaler. Prior authorization is approved based on the criteria of severe asthma requiring this specific medication.",
#       "edit_message": "Create a claim for a medication requiring prior authorization where the member has documented severe asthma history. The medication should be a high-cost inhaler that is deemed necessary by the physician. Ensure all relevant documentation is provided to reflect PA approval."
#     },
#     {
#       "senario_description": "This claim is for a member who is requesting a medication that is not covered under their plan without prior authorization, and they do not have a qualifying condition documented. The claim should be marked as denied due to lack of eligibility for PA.",
#       "edit_message": "Create a claim for a medication requesting prior authorization for a member who does not have a qualifying diagnosis. This claim should be automatically denied based on the PA requirements. Ensure all documentation reflects that there is no prior authorization eligibility."
#     },
#     {
#       "senario_description": "This claim is for a member who is on a specific maintenance medication for high blood pressure that requires prior authorization after the first three months of therapy. The member has been stable on the medication for six months with no adverse effects which satisfies PA requirements.",
#       "edit_message": "Create a claim for a maintenance medication for high blood pressure that requires prior authorization after three months. The member has been taking this medication consistently for six months without issues. Ensure that the claim reflects the criteria for maintenance therapy approval."
#     }
#   ]
# }