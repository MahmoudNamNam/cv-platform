#!/usr/bin/env python
"""
Script to create an admin user for CV Platform.
Usage: python create_admin.py
"""
import os
import sys
import django

# Add parent directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cv_platform.settings')
django.setup()

from accounts.models import User

def create_admin():
    """Create an admin user."""
    username = input("Enter admin username (default: admin): ").strip() or "admin"
    email = input("Enter admin email (default: admin@cvplatform.com): ").strip() or "admin@cvplatform.com"
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"❌ User '{username}' already exists!")
        response = input("Do you want to update this user to admin? (y/n): ").strip().lower()
        if response != 'y':
            print("Cancelled.")
            return
        user = User.objects.get(username=username)
    else:
        # Get password
        import getpass
        password = getpass.getpass("Enter password: ")
        password_confirm = getpass.getpass("Confirm password: ")
        
        if password != password_confirm:
            print("❌ Passwords don't match!")
            return
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ User '{username}' created!")
    
    # Set admin privileges
    user.role = 'admin'
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    
    print(f"\n✅ Admin user '{username}' is ready!")
    print(f"   Email: {user.email}")
    print(f"   Role: {user.role}")
    print(f"   Staff: {user.is_staff}")
    print(f"   Superuser: {user.is_superuser}")
    print(f"\nYou can now login at: http://127.0.0.1:8000/admin/")

if __name__ == '__main__':
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

