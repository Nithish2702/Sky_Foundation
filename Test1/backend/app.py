"""
Qatar Foundation Admin Portal - Backend API
Flask application with authentication and opportunity management
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime, timedelta
from functools import wraps
import secrets
import re
import os

from models import db, Admin, Opportunity, PasswordResetToken
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
# CORS configuration for cookie-based authentication
# Allow both local development and production frontend URLs
allowed_origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    os.environ.get('FRONTEND_URL', '')  # Will be set in Render
]
# Remove empty strings
allowed_origins = [origin for origin in allowed_origins if origin]

CORS(app, 
     resources={
         r"/api/*": {
             "origins": allowed_origins,
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }
     })
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()


# ==================== HELPER FUNCTIONS ====================

def validate_email(email):
    """Validate email format"""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None


def login_required(f):
    """Decorator to require login for protected routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """
    US-1.1: Admin Sign Up
    Create a new admin account with validation
    """
    try:
        data = request.get_json()
        
        # Extract and validate fields
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validation: All fields required
        if not all([full_name, email, password, confirm_password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Validation: Email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validation: Password length
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Validation: Passwords match
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        # Check if email already exists
        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            return jsonify({'error': 'An account with this email already exists'}), 409
        
        # Create new admin
        new_admin = Admin(
            full_name=full_name,
            email=email
        )
        new_admin.set_password(password)
        
        db.session.add(new_admin)
        db.session.commit()
        
        return jsonify({
            'message': 'Account created successfully',
            'admin': {
                'id': new_admin.id,
                'full_name': new_admin.full_name,
                'email': new_admin.email
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred during signup'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """
    US-1.2: Admin Login
    Authenticate admin and create session
    """
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember_me = data.get('remember_me', False)
        
        # Validation
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Find admin
        admin = Admin.query.filter_by(email=email).first()
        
        # Generic error message for security
        if not admin or not admin.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Update last login
        admin.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create session
        session['admin_id'] = admin.id
        session['email'] = admin.email
        session.modified = True  # Force session save
        
        # Set session duration based on remember_me
        if remember_me:
            session.permanent = True
            app.permanent_session_lifetime = timedelta(days=30)
        else:
            session.permanent = False
        
        return jsonify({
            'message': 'Login successful',
            'admin': {
                'id': admin.id,
                'full_name': admin.full_name,
                'email': admin.email
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred during login'}), 500


@app.route('/api/auth/logout', methods=['POST'])
@login_required
def logout():
    """Logout admin and clear session"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """
    US-1.3: Forgot Password
    Generate password reset token (always show success message)
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        # Validation
        if not email or not validate_email(email):
            return jsonify({'error': 'Please enter a valid email address'}), 400
        
        # Always show success message for security
        # But only generate token if email exists
        admin = Admin.query.filter_by(email=email).first()
        
        if admin:
            # Delete any existing tokens for this admin
            PasswordResetToken.query.filter_by(admin_id=admin.id).delete()
            
            # Generate new token
            token = secrets.token_urlsafe(32)
            reset_token = PasswordResetToken(
                admin_id=admin.id,
                token=token,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            
            db.session.add(reset_token)
            db.session.commit()
            
            # In production, send email here
            # For now, log the reset link
            reset_link = f"http://localhost:5000/reset-password?token={token}"
            print(f"Password reset link for {email}: {reset_link}")
        
        # Always return success message
        return jsonify({
            'message': 'If an account exists with this email, a password reset link has been sent'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred'}), 500


@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    try:
        data = request.get_json()
        token = data.get('token', '')
        new_password = data.get('new_password', '')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Find valid token
        reset_token = PasswordResetToken.query.filter_by(
            token=token,
            used=False
        ).first()
        
        if not reset_token:
            return jsonify({'error': 'Invalid or expired reset link'}), 400
        
        # Check if token expired
        if reset_token.expires_at < datetime.utcnow():
            return jsonify({'error': 'This reset link has expired. Please request a new one'}), 400
        
        # Update password
        admin = Admin.query.get(reset_token.admin_id)
        admin.set_password(new_password)
        
        # Mark token as used
        reset_token.used = True
        
        db.session.commit()
        
        return jsonify({'message': 'Password reset successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred'}), 500


@app.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_admin():
    """Get current logged-in admin info"""
    admin = Admin.query.get(session['admin_id'])
    if not admin:
        return jsonify({'error': 'Admin not found'}), 404
    
    return jsonify({
        'admin': {
            'id': admin.id,
            'full_name': admin.full_name,
            'email': admin.email,
            'created_at': admin.created_at.isoformat()
        }
    }), 200


# ==================== OPPORTUNITY ROUTES ====================

@app.route('/api/opportunities', methods=['GET'])
@login_required
def get_opportunities():
    """
    US-2.1: View All Opportunities
    Get all opportunities for the logged-in admin
    """
    try:
        admin_id = session['admin_id']
        opportunities = Opportunity.query.filter_by(admin_id=admin_id).order_by(Opportunity.created_at.desc()).all()
        
        return jsonify({
            'opportunities': [opp.to_dict() for opp in opportunities]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500


@app.route('/api/opportunities', methods=['POST'])
@login_required
def create_opportunity():
    """
    US-2.2: Add a New Opportunity
    Create a new opportunity with validation
    """
    try:
        data = request.get_json()
        admin_id = session['admin_id']
        
        # Extract fields
        name = data.get('name', '').strip()
        duration = data.get('duration', '').strip()
        start_date = data.get('start_date', '').strip()
        description = data.get('description', '').strip()
        skills = data.get('skills', '').strip()
        category = data.get('category', '').strip()
        future_opportunities = data.get('future_opportunities', '').strip()
        max_applicants = data.get('max_applicants')
        
        # Validation: Required fields
        if not all([name, duration, start_date, description, skills, category, future_opportunities]):
            return jsonify({'error': 'All required fields must be filled'}), 400
        
        # Validation: Category
        valid_categories = ['technology', 'business', 'design', 'marketing', 'data', 'other']
        if category.lower() not in valid_categories:
            return jsonify({'error': 'Invalid category'}), 400
        
        # Validation: Max applicants (if provided)
        if max_applicants is not None:
            try:
                max_applicants = int(max_applicants)
                if max_applicants < 0:
                    return jsonify({'error': 'Maximum applicants must be a positive number'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Maximum applicants must be a valid number'}), 400
        
        # Create opportunity
        opportunity = Opportunity(
            admin_id=admin_id,
            name=name,
            duration=duration,
            start_date=start_date,
            description=description,
            skills=skills,
            category=category,
            future_opportunities=future_opportunities,
            max_applicants=max_applicants
        )
        
        db.session.add(opportunity)
        db.session.commit()
        
        return jsonify({
            'message': 'Opportunity created successfully',
            'opportunity': opportunity.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while creating opportunity'}), 500


@app.route('/api/opportunities/<int:opportunity_id>', methods=['GET'])
@login_required
def get_opportunity(opportunity_id):
    """
    US-2.4: View Opportunity Details
    Get details of a specific opportunity
    """
    try:
        admin_id = session['admin_id']
        opportunity = Opportunity.query.filter_by(id=opportunity_id, admin_id=admin_id).first()
        
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        return jsonify({
            'opportunity': opportunity.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'An error occurred'}), 500


@app.route('/api/opportunities/<int:opportunity_id>', methods=['PUT'])
@login_required
def update_opportunity(opportunity_id):
    """
    US-2.5: Edit an Opportunity
    Update an existing opportunity
    """
    try:
        admin_id = session['admin_id']
        opportunity = Opportunity.query.filter_by(id=opportunity_id, admin_id=admin_id).first()
        
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        data = request.get_json()
        
        # Extract fields
        name = data.get('name', '').strip()
        duration = data.get('duration', '').strip()
        start_date = data.get('start_date', '').strip()
        description = data.get('description', '').strip()
        skills = data.get('skills', '').strip()
        category = data.get('category', '').strip()
        future_opportunities = data.get('future_opportunities', '').strip()
        max_applicants = data.get('max_applicants')
        
        # Validation: Required fields
        if not all([name, duration, start_date, description, skills, category, future_opportunities]):
            return jsonify({'error': 'All required fields must be filled'}), 400
        
        # Validation: Category
        valid_categories = ['technology', 'business', 'design', 'marketing', 'data', 'other']
        if category.lower() not in valid_categories:
            return jsonify({'error': 'Invalid category'}), 400
        
        # Validation: Max applicants (if provided)
        if max_applicants is not None and max_applicants != '':
            try:
                max_applicants = int(max_applicants)
                if max_applicants < 0:
                    return jsonify({'error': 'Maximum applicants must be a positive number'}), 400
            except (ValueError, TypeError):
                return jsonify({'error': 'Maximum applicants must be a valid number'}), 400
        else:
            max_applicants = None
        
        # Update opportunity
        opportunity.name = name
        opportunity.duration = duration
        opportunity.start_date = start_date
        opportunity.description = description
        opportunity.skills = skills
        opportunity.category = category
        opportunity.future_opportunities = future_opportunities
        opportunity.max_applicants = max_applicants
        opportunity.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Opportunity updated successfully',
            'opportunity': opportunity.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while updating opportunity'}), 500


@app.route('/api/opportunities/<int:opportunity_id>', methods=['DELETE'])
@login_required
def delete_opportunity(opportunity_id):
    """
    US-2.6: Delete an Opportunity
    Permanently delete an opportunity
    """
    try:
        admin_id = session['admin_id']
        opportunity = Opportunity.query.filter_by(id=opportunity_id, admin_id=admin_id).first()
        
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        db.session.delete(opportunity)
        db.session.commit()
        
        return jsonify({
            'message': 'Opportunity deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while deleting opportunity'}), 500


# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
