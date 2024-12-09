# the search_member function will take in a string and return a JSON list of possible member matches for that member. The string could be the members first name the member's last name or the members first name and last name a.k.a. their full name or it could be their member ID or it could be their date of birth, or it could be their group number, or it could be their ZIP Code or city or address that they live in. Can you have this function taken in the string and then search all of those fields on the member table and then return a Jason result with possible matches?

from .member_model import Member, db
from sqlalchemy import or_, cast, Date
from datetime import datetime

def search_member(search_string):
    try:
        # Try to parse date if the search string is a date
        try:
            search_date = datetime.strptime(search_string, '%Y-%m-%d').date()
        except ValueError:
            search_date = None

        # Handle full name searches
        first_name = None
        last_name = None

        # Check for "First Last" format
        if ' ' in search_string:
            parts = [p.strip() for p in search_string.split(' ', 1)]
            if len(parts) == 2:
                first_name, last_name = parts

        # Create base search query
        query = Member.query.filter(
            or_(
                Member.first_name.ilike(f'%{search_string}%'),
                Member.last_name.ilike(f'%{search_string}%'),
                Member.member_id.ilike(f'%{search_string}%'),
                Member.group_number.ilike(f'%{search_string}%'),
                Member.zip_code.ilike(f'%{search_string}%'),
                Member.city.ilike(f'%{search_string}%'),
                Member.address.ilike(f'%{search_string}%')
            )
        )

        # Add full name search if applicable
        if first_name and last_name:
            full_name_query = Member.query.filter(
                db.and_(
                    Member.first_name.ilike(f'%{first_name}%'),
                    Member.last_name.ilike(f'%{last_name}%')
                )
            )
            query = query.union(full_name_query)

        # Add date search if valid date was provided
        if search_date:
            query = query.union(
                Member.query.filter(Member.date_of_birth == search_date)
            )

        # Execute query and get results
        members = query.all()

        # Convert results to list of dictionaries
        results = []
        for member in members:
            results.append({
                "database_id": member.database_id,
                "member_id": member.member_id,
                "first_name": member.first_name,
                "last_name": member.last_name,
                "date_of_birth": member.date_of_birth.isoformat() if member.date_of_birth else None,
                "city": member.city,
                "state": member.state,
                "group_number": member.group_number
            })

        return results

    except Exception as e:
        return {"error": str(e)}