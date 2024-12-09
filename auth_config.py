import os
from dotenv import load_dotenv
from functools import wraps
from flask import redirect, session, url_for
from authlib.integrations.flask_client import OAuth

# Load environment variables
load_dotenv()

# OAuth setup
oauth = OAuth()

auth0 = oauth.register(
    'auth0',
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    api_base_url=f'https://{os.getenv("AUTH0_DOMAIN")}',
    access_token_url=f'https://{os.getenv("AUTH0_DOMAIN")}/oauth/token',
    authorize_url=f'https://{os.getenv("AUTH0_DOMAIN")}/authorize',
    jwks_uri=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/jwks.json',  # Add this line
    client_kwargs={
        'scope': 'openid profile email',
    },
)

# Auth decorator
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated