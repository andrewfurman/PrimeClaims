import os, psycopg2
from auth_config import oauth, auth0, requires_auth
from functools import wraps
from flask import Flask, redirect, url_for, session, request, render_template
from datetime import datetime

# 💿 Models
from members.member_model import db
from auth.users_model import User
from claims.claim_model import Claim

# 🛣️ Routes 
from members.member_routes import members_bp
from claims.claim_routes import claims_bp
from ncpdp.ncpdp_routes import ncpdp_bp
from auth.auth_routes import auth_bp

# Database
from flask_migrate import Migrate
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from sqlalchemy.exc import OperationalError


app = Flask(__name__, template_folder='.')
# Configure database and secret key
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,  # Reasonable pool size for most applications
    'pool_timeout': 30,  # Seconds to wait before giving up on getting a connection
    'pool_recycle': 1800,  # Recycle connections after 30 minutes
    'max_overflow': 2,  # Allow up to 2 connections beyond pool_size
    'pool_pre_ping': True,  # Enable connection health checks
    'connect_args': {
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5,
        'connect_timeout': 10
    }
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("AUTH0_CLIENT_SECRET")  # Required for Auth0 sessions
# Initialize extensions
db.init_app(app)
oauth.init_app(app)  # Initialize OAuth with app
migrate = Migrate(app, db)  # Add this line

# Near the top of main.py, after app creation
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Auth routes

@app.route('/login')
def login():
    callback_url = url_for('callback', _external=True, _scheme='https')
    print(f"Callback URL being used: {callback_url}")
    # Generate and store state parameter
    return auth0.authorize_redirect(
        redirect_uri=callback_url,
        audience=f'https://{os.getenv("AUTH0_DOMAIN")}/userinfo'  # Add this line
    )

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    # Generate the return URL based on the current request host
    return_to_url = f"{request.scheme}://{request.host}/auth/logout"
    # Redirect to Auth0 logout endpoint
    auth0_logout_url = (f"https://{os.getenv('AUTH0_DOMAIN')}/v2/logout"
                        f"?client_id={os.getenv('AUTH0_CLIENT_ID')}&returnTo={return_to_url}")
    # Redirect to Auth0 logout
    return redirect(auth0_logout_url)

@app.route('/auth/logout', methods=['GET'])
def logout_page():
    # Clear the session
    session.clear()
    return render_template('auth/logout.html')  # Render the logout.html template

@app.route('/callback')
def callback():
    try:
        token = auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()
        
        # Save user info to database
        User.create_or_update_from_auth0(userinfo)
        
        # Store user info in session
        session['user'] = userinfo
        return redirect('/')
    except Exception as e:
        print(f"Auth error: {str(e)}")
        return redirect('/login')

def retry_database_operation():
    def decorator(f):
        @wraps(f)
        @retry(
            stop=stop_after_attempt(5),  # Increased attempts
            wait=wait_exponential(multiplier=1, min=4, max=30),  # Adjusted wait times
            retry=(
                retry_if_exception_type(OperationalError) |
                retry_if_exception_type(psycopg2.OperationalError)
            ),
            reraise=True
        )
        def wrapped(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except (OperationalError, psycopg2.OperationalError):
                # Ensure connection is closed and cleaned up
                db.session.remove()
                # Create new connection
                db.session.configure(bind=db.engine)
                # Re-raise to trigger retry
                raise
        return wrapped
    return decorator
    
# Create middleware to apply retry logic to all routes
class RetryMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        @retry_database_operation()
        def _retry_app(*args, **kwargs):
            try:
                return self.app(environ, start_response)
            except (OperationalError, psycopg2.OperationalError) as e:
                # Log the error if you have logging configured
                print(f"Database error occurred: {str(e)}")
                db.session.remove()
                # Return 503 Service Unavailable
                status = '503 Service Unavailable'
                response_headers = [('Content-type', 'text/plain')]
                start_response(status, response_headers)
                return [b'Database connection error. Please try again later.']
        return _retry_app()
# Apply middleware
app.wsgi_app = RetryMiddleware(app.wsgi_app)

# Add this decorator function before your route definitions
def route_retry():
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=(
            retry_if_exception_type(OperationalError) |
            retry_if_exception_type(psycopg2.OperationalError)
        )
    )

# Register blueprints
app.register_blueprint(members_bp)
app.register_blueprint(claims_bp)
app.register_blueprint(ncpdp_bp)
app.register_blueprint(auth_bp)


# Then modify your index route to use it
@app.route('/')
@route_retry()
def index():
    return redirect('/members')

# Add a context processor to ensure database connections are properly managed
@app.before_request
def before_request():
    if not hasattr(db.session, 'active'):
        db.session.active = True

@app.teardown_request
def teardown_request(exception=None):
    if hasattr(db.session, 'active'):
        db.session.remove()
        delattr(db.session, 'active')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)