import os

from flask import Blueprint, render_template, request, jsonify, send_file, Blueprint

# Database Imports
from .member_model import Member, db
from sqlalchemy import desc

# Function Imports
from .create_member_gpt import create_member_gpt
from .export_members import export_members
from .search_member import search_member

members_bp = Blueprint('members', __name__, template_folder='.')

@members_bp.route('/members')
def members():
    members = Member.query.order_by(desc(Member.updated_at)).all()
    return render_template('members/members.html', members=members)

@members_bp.route('/members/<member_id>')
def view_member(member_id):
    member = Member.query.filter_by(member_id=member_id).first_or_404()
    return render_template('members/view_member.html', member=member)

@members_bp.route('/members/create-gpt', methods=['POST'])
def create_member_with_gpt():
    prompt = request.json.get('prompt', '')
    try:
        result = create_member_gpt(prompt)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@members_bp.route('/members/export', methods=['GET'])
def export_members_route():
    filepath = None
    try:
        filepath = export_members()
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': 'Export failed - File not created'}), 500
            
        return send_file(
            filepath,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='members_export.xlsx'
        )
        
    except Exception as e:
        print(f"Error in export_members_route: {str(e)}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        # Clean up temporary file
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                os.rmdir(os.path.dirname(filepath))
            except Exception as e:
                print(f"Error cleaning up file: {str(e)}")

@members_bp.route('/members/search', methods=['GET'])
def search_members_route():
    search_string = request.args.get('q', '')
    if not search_string:
        return jsonify({'error': 'No search string provided'}), 400

    try:
        results = search_member(search_string)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@members_bp.route('/members/<member_id>/delete', methods=['DELETE'])
def delete_member(member_id):
    try:
        member = Member.query.filter_by(member_id=member_id).first_or_404()
        db.session.delete(member)
        db.session.commit()
        return jsonify({'message': 'Member deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500