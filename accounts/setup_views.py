"""
Setup views for initial admin creation (one-time use).
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from accounts.models import User
import os


@csrf_exempt
@require_http_methods(["POST"])
def create_initial_admin(request):
    """
    One-time endpoint to create initial admin user.
    Requires SETUP_TOKEN environment variable for security.
    
    Usage:
    curl -X POST https://your-site.com/setup/create-admin/ \
      -H "Content-Type: application/json" \
      -d '{"token": "your-setup-token", "username": "admin", "email": "admin@example.com", "password": "secure123"}'
    """
    # Get setup token from environment
    setup_token = os.environ.get('SETUP_TOKEN', '')
    
    # If no token is set, disable this endpoint
    if not setup_token:
        return JsonResponse({
            'error': 'Setup token not configured. This endpoint is disabled.'
        }, status=403)
    
    # Get token from request
    import json
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    provided_token = data.get('token', '')
    if provided_token != setup_token:
        return JsonResponse({'error': 'Invalid token'}, status=403)
    
    # Check if admin already exists
    if User.objects.filter(is_superuser=True).exists():
        return JsonResponse({
            'error': 'Admin user already exists. Use Django admin or shell to create more.'
        }, status=400)
    
    # Get user data
    username = data.get('username', 'admin')
    email = data.get('email', 'admin@cvplatform.com')
    password = data.get('password', '')
    
    if not password:
        return JsonResponse({'error': 'Password is required'}, status=400)
    
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return JsonResponse({
            'error': f'Username "{username}" already exists'
        }, status=400)
    
    # Create admin user
    try:
        admin = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='admin'
        )
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Admin user "{username}" created successfully!',
            'username': admin.username,
            'email': admin.email
        })
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to create admin: {str(e)}'
        }, status=500)

