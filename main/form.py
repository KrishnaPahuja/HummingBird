import re
from flask import flash
from main.models import User, Post
from main import app, db

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

def check_email(email):
    if(re.fullmatch(regex, email)):
        return True
    return False

def validated(username, email, password, confirm_password):
    valid = True
    if len(username) < 2:
        flash(f'Username must contain atleast 2 characters', 'danger')
        valid = False
    if not check_email(email):
        flash(f'Invalid Email', 'danger')
        valid = False
    if confirm_password!=password:
        flash(f'Confirm Password and Password do not match', 'danger')
        valid = False
    
    with app.app_context():
        if User.query.filter_by(username=username).first():
            flash("Username already taken", 'info')
            valid = False
        if User.query.filter_by(email=email).first():
            flash("Email already taken", 'info')
            valid = False
        
    return valid


def validate_username(username):
    valid = True
    if len(username) < 2:
        flash(f'Username must contain atleast 2 characters', 'danger')
        valid = False
    with app.app_context():
        if User.query.filter_by(username=username).first():
            flash("Username already taken", 'info')
            valid = False
    return valid

def validate_email(email):
    valid = True
    if not check_email(email):
        flash(f'Invalid Email', 'danger')
        valid = False
    with app.app_context():
        if User.query.filter_by(email=email).first():
            flash("Email already taked", 'info')
            valid = False
    return valid

def validate_post(title, content):
    valid = True
    if len(title) < 2:
        flash(f'Title must contain atleast 2 characters', 'info')
        valid = False
    if len(content) < 5:
        flash(f'Content must contain atleast 5 characters', 'info')
        valid = False
    return valid