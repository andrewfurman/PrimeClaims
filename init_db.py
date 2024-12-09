from flask import Flask
from members.member_model import db
from members.member_model import Member
from claims.claim_model import Claim
from auth.users_model import User
import os
from sqlalchemy.exc import SQLAlchemyError
import logging

def init_database():
    # Create Flask app
    app = Flask(__name__)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize the database
        with app.app_context():
            logger.info("Initializing database...")
            db.init_app(app)
            
            # Create all tables
            logger.info("Creating database tables...")
            db.create_all()
            
            logger.info("Database initialization completed successfully!")
            
    except SQLAlchemyError as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    init_database()