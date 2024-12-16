import os, sys, json
import anthropic
import concurrent.futures
import time
from flask import current_app

# Add the root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Now we can import from other directories
from members.get_member import get_member
from claims.create_claim_claude import create_claim_claude

client = anthropic.Client(api_key=os.environ['ANTHROPIC_API_KEY'])

def create_claim_wrapper(args):
    member_database_id, prompt, index, app = args
    with app.app_context():
        try:
            result = create_claim_claude(
                member_database_id=member_database_id,
                prompt=prompt
            )
            print(f"Claim {index + 1}: Success")
            return result
        except Exception as e:
            print(f"Claim {index + 1}: Error - {str(e)}")
            return None

def create_multi_claims_claude(prompt: str = None, member_database_id: int = None):
    try:
        app = current_app._get_current_object()
        # Set default empty prompt if none provided
        prompt = prompt or ""

        # Get member data using get_member function
        member_data = get_member(member_database_id)
        if "error" in member_data:
            raise ValueError(f"Error getting member data: {member_data['error']}")

        tools = [{
            "name": "create_multi_claims",
            "description": "This is a tool that creates specifications for pharmacy insurance test claims. Do not include details about the insured member, but instead include realistic information that would appear on each claim based on the prompt like the name of the drug, amount, date of service, quantity, what condition the drug is used to treat. Be specific but aim to keep the prompts as susinct as possible (less than 30 words). Make sure that the number of claims in the array of claim_specification_prompts exactly matches what was requested. If the prompt above requests N claims, your final array must contain exactly N claims. Do not include fewer or more.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "claim_specification_prompts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "create_claim_prompt": {
                                    "type": "string",
                                    "description": "Prompt containing details needed to create the claim"
                                }
                            },
                            "required": ["create_claim_prompt"]
                        }
                    }
                },
                "required": ["claim_specification_prompts"]
            }
        }]

        query = f"""Create an array of claim specifications based on this prompt: {prompt}
        Make sure the number of claims exactly matches what was requested.
        {f'Consider member demographics: {member_data}' if member_data else 'Create diverse scenarios for a generic person that has health insurance from their employer.'}"""

        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=8192,
            tools=tools,
            tool_choice={"type": "tool", "name": "create_multi_claims"},
            messages=[{
                "role": "user",
                "content": query
            }]
        )

        # Extract the result from the tool use response
        result = None
        for content in response.content:
            if content.type == "tool_use" and content.name == "create_multi_claims":
                result = content.input
                break

        if not result:
            raise ValueError("Failed to generate claim specifications")

        # Prepare arguments for parallel processing
        claim_args = [
            (member_database_id, spec['create_claim_prompt'], i, app)
            for i, spec in enumerate(result['claim_specification_prompts'])
        ]

        print(f"\nAttempting to create {len(claim_args)} claims... with CLAUDE")

        # Create claims in parallel
        created_claims = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Process in batches of 50
            batch_size = 50
            for i in range(0, len(claim_args), batch_size):
                batch = claim_args[i:i + batch_size]
                futures = list(executor.map(create_claim_wrapper, batch))
                created_claims.extend([claim for claim in futures if claim is not None])
                time.sleep(1)  # Add delay between batches

        # Add created claims to result
        result['created_claims'] = created_claims

        print(f"\nCreated {len(created_claims)} out of {len(claim_args)} claims successfully using CLAUDE")
        return result

    except Exception as e:
        print(f"Error in create_multi_claims_claude: {str(e)}")
        raise e

if __name__ == "__main__":
    # Import Flask app and set up context
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from main import app

    with app.app_context():
        test_prompt = "create two claims for a generic drug"
        try:
            result = create_multi_claims_claude(prompt=test_prompt)
            print("\nGenerated Claims:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error: {str(e)}")