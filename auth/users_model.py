# The users database table will store information from the users after each user has logged in using Auth0 for authentication.

# Can you create the users table so that it stores all data attributues that are able to be captured from Auth0.  All attributiues should be optional (nullable) unless absolutely required.

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import TEXT, JSONB
from members.member_model import db  # Import db from member_model

class User(db.Model):
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Auth0 Essential Fields
    auth0_id = db.Column(TEXT, unique=True, nullable=False)  # sub claim from Auth0
    email = db.Column(TEXT, unique=True, nullable=True)
    
    # Profile Information
    first_name = db.Column(TEXT, nullable=True)
    last_name = db.Column(TEXT, nullable=True)
    nickname = db.Column(TEXT, nullable=True)
    picture = db.Column(TEXT, nullable=True)  # URL to profile picture
    
    # Additional Auth0 Fields
    email_verified = db.Column(db.Boolean, nullable=True)
    locale = db.Column(TEXT, nullable=True)
    given_name = db.Column(TEXT, nullable=True)
    family_name = db.Column(TEXT, nullable=True)
    name = db.Column(TEXT, nullable=True)
    
    # Custom Claims and Extra Data
    custom_claims = db.Column(JSONB, nullable=True)
    
    # Access Information
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)
    login_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add a class method to create or update user
    @classmethod
    def create_or_update_from_auth0(cls, userinfo):
        user = cls.query.filter_by(auth0_id=userinfo['sub']).first()
        
        if user:
            # Update existing user
            user.email = userinfo.get('email')
            user.first_name = userinfo.get('given_name')
            user.last_name = userinfo.get('family_name')
            user.nickname = userinfo.get('nickname')
            user.picture = userinfo.get('picture')
            user.email_verified = userinfo.get('email_verified')
            user.locale = userinfo.get('locale')
            user.name = userinfo.get('name')
            user.last_login = datetime.utcnow()
            user.login_count += 1
        else:
            # Create new user
            user = cls(
                auth0_id=userinfo['sub'],
                email=userinfo.get('email'),
                first_name=userinfo.get('given_name'),
                last_name=userinfo.get('family_name'),
                nickname=userinfo.get('nickname'),
                picture=userinfo.get('picture'),
                email_verified=userinfo.get('email_verified'),
                locale=userinfo.get('locale'),
                name=userinfo.get('name'),
                last_login=datetime.utcnow(),
                login_count=1
            )
            db.session.add(user)
            
        db.session.commit()
        return user

  
    def __repr__(self):
        return f'<User {self.id}: {self.email}>'