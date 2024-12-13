from flask import Blueprint, render_template, request, jsonify
from .create_multi_claims_claude import create_multi_claims_claude

multi_claims_bp = Blueprint('multi_claims', __name__, template_folder='.')

@multi_claims_bp.route('/multi-claims')
def multi_claims():
    return render_template('multi_claims/create_multi_claim.html')

@multi_claims_bp.route('/multi-claims/generate', methods=['POST'])
def generate_multi_claims():
    try:
        # Add debug logging
        print("Received request for multi-claims generation")
        
        # Fix: Get data from request.json instead of request.args
        data = request.json
        prompt = data.get('prompt', '')
        member_database_id = data.get('member_database_id')
        
        print(f"Processing request with prompt: {prompt}, member_id: {member_database_id}")
        
        result = create_multi_claims_claude(prompt, member_database_id)
        
        # Debug log the result
        print(f"Generated result: {result}")
        
        # Return the result directly since it's already in the correct format
        return jsonify(result)
    except Exception as e:
        print(f"Error in generate_multi_claims: {str(e)}")
        return jsonify({"error": str(e)}), 400