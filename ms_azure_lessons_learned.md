# Microsoft Azure Deployment - Lessons Learned
## Database Connection Issues
### Error: AdminShutdown & SSL Connection Closure
**Error Message:**
This Session's transaction has been rolled back due to a previous exception during flush...
(psycopg2.errors.AdminShutdown) terminating connection due to administrator command
SSL connection has been closed unexpectedly

**Root Cause:**
- Multiple session management approaches conflicting
- Global sessions in individual function files
- Connection timeouts during write operations
- Improper session cleanup
**Solutions:**
1. Remove global sessions from individual files
2. Use Flask-SQLAlchemy's `db.session` consistently
3. Implement proper error handling and rollbacks
4. Add session cleanup on app context teardown

**Code Example:**
```python
# Incorrect (Don't do this)
engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)
session = Session()
# Correct (Do this)
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Use db.session in your routes/functions
Connection Management Best Practices
Database URL Configuration
DATABASE_URL = "postgresql://user:pass@host:5432/dbname?sslmode=require"
Connection Pooling Settings
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,
    'pool_timeout': 30,
    'pool_recycle': 1800,
    'pool_pre_ping': True
}
Proper Session Cleanup
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()
Error Prevention Checklist
Database Connections

```

 Remove all global sessions
 Use Flask-SQLAlchemy's db.session exclusively
 Implement try/except with rollbacks
 Add proper session cleanup
Azure Configuration

 Verify DATABASE_URL includes sslmode=require
 Configure appropriate connection timeouts
 Set up proper connection pooling
 Check firewall rules if connections fail
Code Structure

 Keep session management consistent
 Handle write operations with proper error catching
 Implement rollbacks for failed transactions


# 🚀 Deploying Flask to Azure App Service
## 📋 Prerequisites
- Azure account
- Azure CLI installed
- Git repository with Flask application
- Python 3.x
## 🛠️ Required Files
### 1. gunicorn.conf.py
```python
# Required for Azure deployment
bind = "0.0.0.0:8000"
workers = 4
timeout = 120
2. requirements.txt
Flask==2.0.1
gunicorn==20.1.0
python-dotenv==0.19.0
# Add your other dependencies
3. startup.txt
gunicorn --config gunicorn.conf.py main:app
🔧 Project Structure Changes
Rename app.py to main.py (Azure default)
Ensure main Flask instance is named app:
# main.py
from flask import Flask
app = Flask(__name__)  # Must be named 'app'
⚙️ Azure Configuration
1. Environment Variables
Create a .env file locally (DO NOT COMMIT THIS):

DATABASE_URL=your_database_connection_string
API_KEY=your_api_key
SECRET_KEY=your_secret_key
2. Azure Portal Settings
Application Settings:
SCM_DO_BUILD_DURING_DEPLOYMENT=true
WEBSITE_RUN_FROM_PACKAGE=1
Add environment variables under "Configuration":
FLASK_APP=main.py
FLASK_ENV=production
DATABASE_URL (from your Azure database)
API_KEY (your API key)
SECRET_KEY (your secret key)
3. Deployment Commands
# Login to Azure
az login
# Create resource group
az group create --name YOUR_GROUP_NAME --location eastus
# Create app service plan
az appservice plan create --name YOUR_PLAN_NAME --resource-group YOUR_GROUP_NAME --sku B1
# Create web app
az webapp create --name YOUR_APP_NAME --resource-group YOUR_GROUP_NAME --plan YOUR_PLAN_NAME --runtime "PYTHON:3.9"
# Deploy code
az webapp up --name YOUR_APP_NAME --resource-group YOUR_GROUP_NAME
🚨 Common Issues & Solutions
Module Not Found Errors
Verify all dependencies in requirements.txt
Check Python version matches Azure
Startup Errors
Confirm main.py exists
Verify app variable name is 'app'
Check gunicorn.conf.py settings
Database Connections
Use Azure connection strings (set in Azure Portal, not in code)
Add SSL certificates if required
Set proper timeouts:
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,
    'pool_timeout': 30,
    'pool_recycle': 1800,
}
```

✅ Deployment Checklist
 Renamed app.py to main.py
 Created gunicorn.conf.py
 Updated requirements.txt
 Created startup.txt
 Added Azure environment variables
 Set up SSL certificates (if needed)
 Configured database connection strings
 Set proper timeout values
🔒 Security Notes
Never commit .env files
Never commit API keys or secrets
Use Azure Key Vault for production secrets
Set up proper firewall rules
Enable SSL/TLS

## Database URL Format Change
### Old Format
postgresql://[user]:[password]@[host]/[dbname]?sslmode=require

### New Format (with endpoint option)
postgresql://[user]:[password]@[host]/[dbname]?options=endpoint%3D[endpoint-id]&sslmode=require

### Key Changes
- Added `options=endpoint%3D[endpoint-id]` parameter
- `%3D` is URL encoding for `=`
- Endpoint ID must match your Azure database endpoint
- Maintain `sslmode=require` for security
### Best Practice
Always store database URLs in environment variables or Azure Configuration settings, never in code.
Note: The above example uses placeholder values and is safe to commit to a public repository.