import os
from flask import Blueprint, send_file, jsonify
from .create_ncpdp import create_ncpdp

ncpdp_bp = Blueprint('ncpdp', __name__)

@ncpdp_bp.route('/ncpdp/export', methods=['GET'])
def export_ncpdp_route():
    filepath = None
    try:
        filepath = create_ncpdp()
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': 'Export failed - File not created'}), 500
            
        return send_file(
            filepath,
            mimetype='text/plain',
            as_attachment=True,
            download_name='ncpdp_claims.dat'
        )
        
    except Exception as e:
        print(f"Error in export_ncpdp_route: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        # Clean up temporary file
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                os.rmdir(os.path.dirname(filepath))
            except Exception as e:
                print(f"Error cleaning up file: {str(e)}")