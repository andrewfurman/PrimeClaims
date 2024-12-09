from flask import Blueprint, render_template, request, jsonify, send_file
from sqlalchemy import desc
from .claim_model import Claim
from .create_claim_gpt import create_claim_gpt
from .export_claims import export_claims

claims_bp = Blueprint('claims', __name__, 
                     template_folder='.')

# In claim_routes.py, update the claims route:
@claims_bp.route('/claims')
def claims():
    claims = Claim.query.order_by(desc(Claim.updated_at)).all()
    return render_template('claims.html', claims=claims)

@claims_bp.route('/claims/create-gpt', methods=['POST'])
def create_claim_gpt_route():
    try:
        member_database_id = request.args.get('member_database_id', type=int)
        prompt = request.args.get('prompt', '')
        
        result = create_claim_gpt(member_database_id, prompt)
        return jsonify({"success": True, "claim": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@claims_bp.route('/claims/export', methods=['GET'])
def export_claims_route():
    try:
        filepath = export_claims()
        return send_file(filepath,
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        as_attachment=True,
                        download_name='claims_export.xlsx')
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400