Todo List: 
Make logout work
Make protect all routes
add user fields

# 🚀 RxClaims Development Guide

## 📋 Overview
This is a Python Flask application with a modern front-end implementation using Tailwind CSS.

## 🎨 Design Guidelines

### Layout Requirements
- Content should extend edge-to-edge with a consistent 20px margin
- Modern visual design incorporating shadows and 2024 design principles
- Responsive layout supporting large displays

### Header Design
- Fixed header pinned to top of page
- Logo/title positioned on left side
- Navigation links aligned to right side
- Consistent 20px margin maintained

### UI Elements
- Section headers should include relevant emojis
- Interactive elements should provide loading state feedback
- Button states should display loading indicator when processing

### CSS Framework
- Tailwind CSS is used for all styling
- Utilize modern Tailwind features for shadows and visual effects
- Maintain responsive design principles

### Loading States
When buttons are clicked and waiting for response, they should display a loading indicator.

## 🔌 Database Connection Handling

### Error Handling & Reconnection Logic
To handle database connection issues gracefully, use the following logic in your routes:

1. Implement error handling in your route to catch exceptions related to database connections. For example, in your `/members` route, you could do the following:

   ```python
   @members_bp.route('/members')
   def members():
       try:
           members = Member.query.order_by(desc(Member.updated_at)).all()
           return render_template('members/members.html', members=members, error=None)
       except Exception as e:
           return render_template('members/members.html', 
                                members=[], 
                                error="Database connection is being refreshed. Please wait a moment and refresh the page.")  ```

Ensure your HTML template displays any error messages nicely:

{% if error %}
<div class="mt-20 mx-auto max-w-7xl px-4 py-6">
    <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
        <div class="flex">
            <div class="flex-shrink-0">
                <!-- Heroicon name: mini/exclamation-triangle -->
                <svg class="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd" />
                </svg>
            </div>
            <div class="ml-3">
                <p class="text-sm text-yellow-700">
                    {{ error }}
                </p>
            </div>
        </div>
    </div>
</div>
{% endif %}

Database Connection Best Practices
Always implement proper session cleanup.
Use Flask-SQLAlchemy's db.session for all database interactions.
Implement retry logic and handling for OperationalError exceptions.
By applying the above logic, your application will gracefully handle database connection errors, informing users that the database connection is being refreshed without crashing the application.

## Protecting All Routes with Middleware

To ensure that all routes in your Flask application are protected and require user authentication, you can implement middleware that checks for user authentication before processing any requests.

### Steps to Implement Authentication Middleware:

1. **Create the Authentication Middleware**: Create a class that wraps your Flask app and checks if a user is authenticated by verifying the session.

    ```python
    class AuthMiddleware:
        def __init__(self, app):
            self.app = app

        def __call__(self, environ, start_response):
            # Check if the user is logged in by checking the session
            if 'user' not in session:
                return redirect('/login')(environ, start_response)  # Redirect to login
            return self.app(environ, start_response)
    ```

2. **Apply the Middleware**: Assign the `AuthMiddleware` to your Flask application. This should be done after initializing your app but before running it.

    ```python
    app.wsgi_app = AuthMiddleware(app.wsgi_app)
    ```

3. **Protect Routes Automatically**: With the middleware in place, all routes will now check for user authentication automatically. You no longer need to apply the `requires_auth` decorator on individual routes, as the middleware will enforce authentication globally.

### Summary

By using this middleware approach, you effectively protect all routes in your Flask application with minimal changes to your route definitions. If a user is not authenticated, they will be redirected to the login page, ensuring that only authorized users can access your application.