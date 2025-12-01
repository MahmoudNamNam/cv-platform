"""
URL configuration for CV Platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.http import HttpResponseRedirect
from django.utils import translation
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from accounts.setup_views import create_initial_admin

@csrf_exempt  # Language switching should be CSRF exempt (like Django's built-in view)
@require_http_methods(["POST"])
def custom_set_language(request):
    """
    Custom set_language view that ensures proper redirect and language activation.
    Prevents caching to ensure language applies immediately.
    """
    from django.urls import reverse
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    
    language = request.POST.get('language')
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    
    # Clean up next_url - remove any existing language prefix
    if next_url:
        parsed = urlparse(next_url)
        # Remove language prefix from path (e.g., /ar/accounts/login/ -> /accounts/login/)
        path_parts = parsed.path.strip('/').split('/')
        if path_parts and path_parts[0] in [lang[0] for lang in settings.LANGUAGES]:
            # Remove language prefix
            path_parts = path_parts[1:]
        clean_path = '/' + '/'.join(path_parts) if path_parts else '/'
        
        # Remove language parameters from query string
        if parsed.query:
            params = parse_qs(parsed.query)
            params.pop('lang', None)
            params.pop('language', None)
            new_query = urlencode(params, doseq=True)
        else:
            new_query = ''
        
        next_url = urlunparse((parsed.scheme, parsed.netloc, clean_path, parsed.params, new_query, parsed.fragment))
    
    # Validate language
    if language and language in [lang[0] for lang in settings.LANGUAGES]:
        # Activate language immediately
        translation.activate(language)
        
        # Store in session
        request.session['django_language'] = language
        request.session.modified = True
        request.session.save()  # Force save
        
        # Add language prefix to next_url if using i18n_patterns
        # With prefix_default_language=False, default language doesn't need prefix
        if next_url and next_url.startswith('/') and not next_url.startswith('/static/') and not next_url.startswith('/media/') and not next_url.startswith('/i18n/'):
            # Check if URL already has a language prefix
            path_parts = next_url.strip('/').split('/')
            has_lang_prefix = path_parts and path_parts[0] in [lang[0] for lang in settings.LANGUAGES]
            
            # Add language prefix only if needed and not default language
            if not has_lang_prefix:
                # Only add prefix for non-default languages
                # Default language works without prefix when prefix_default_language=False
                if language != settings.LANGUAGE_CODE:
                    next_url = f'/{language}{next_url}'
        
        # Create response with cache-busting headers
        response = HttpResponseRedirect(next_url)
        
        # Prevent caching
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        # Set cookie - use explicit name
        cookie_name = getattr(settings, 'LANGUAGE_COOKIE_NAME', 'django_language')
        # Delete old cookie first to ensure it's updated
        response.delete_cookie(cookie_name, path='/')
        # Set new cookie
        response.set_cookie(
            cookie_name,
            language,
            max_age=365*24*60*60,  # 1 year
            path='/',
            domain=None,  # Use default domain
            samesite='Lax',
            httponly=False,  # Allow JavaScript access if needed
            secure=False  # Set to True in production with HTTPS
        )
        
        return response
    
    # Fallback to default
    response = HttpResponseRedirect(next_url)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

def health_check(request):
    """Simple health check endpoint for deployment debugging."""
    from django.http import JsonResponse
    from django.db import connection
    from accounts.models import User
    import os
    
    health_data = {
        'status': 'ok',
        'database': 'unknown',
        'migrations': 'unknown',
        'environment': {
            'DEBUG': os.getenv('DEBUG', 'Not set'),
            'ALLOWED_HOSTS': os.getenv('ALLOWED_HOSTS', 'Not set'),
        }
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_data['database'] = 'connected'
            
            # Check if User table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts_user'")
            user_table_exists = cursor.fetchone() is not None
            
            # Check if django_session table exists (required for sessions)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_session'")
            session_table_exists = cursor.fetchone() is not None
            
            if user_table_exists and session_table_exists:
                health_data['migrations'] = 'All tables exist'
                # Try to count users
                try:
                    user_count = User.objects.count()
                    health_data['user_count'] = user_count
                except Exception as e:
                    health_data['migrations'] = f'Tables exist but error: {str(e)}'
            elif not user_table_exists:
                health_data['migrations'] = 'User table NOT found - migrations needed!'
                health_data['status'] = 'error'
            elif not session_table_exists:
                health_data['migrations'] = 'django_session table NOT found - migrations needed!'
                health_data['status'] = 'error'
    except Exception as e:
        health_data['database'] = f'Error: {str(e)}'
        health_data['status'] = 'error'
    
    return JsonResponse(health_data)

@csrf_exempt
@require_http_methods(["POST"])
def run_migrations_endpoint(request):
    """Run migrations via web endpoint (for free plans without shell access)."""
    from django.http import JsonResponse
    from django.core.management import call_command
    from django.db import connection
    import os
    import io
    
    # Security: Require SETUP_TOKEN (same as admin creation)
    setup_token = os.environ.get('SETUP_TOKEN', '')
    if not setup_token:
        return JsonResponse({
            'error': 'SETUP_TOKEN not configured. This endpoint is disabled.'
        }, status=403)
    
    # Get token from request
    import json
    try:
        data = json.loads(request.body) if request.body else {}
    except:
        data = request.POST.dict() if hasattr(request, 'POST') else {}
    
    provided_token = data.get('token', '')
    if provided_token != setup_token:
        return JsonResponse({'error': 'Invalid token'}, status=403)
    
    # Run migrations
    try:
        output = io.StringIO()
        call_command('migrate', '--noinput', stdout=output, stderr=output)
        migration_output = output.getvalue()
        
        # Check if User table exists now
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accounts_user'")
            table_exists = cursor.fetchone() is not None
        
        return JsonResponse({
            'success': True,
            'message': 'Migrations completed',
            'output': migration_output,
            'user_table_exists': table_exists
        })
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': f'Migration failed: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)

urlpatterns = [
    # Health check endpoint (for debugging)
    path('health/', health_check, name='health_check'),
    # Run migrations endpoint (for free plans without shell)
    path('setup/run-migrations/', run_migrations_endpoint, name='run_migrations'),
    # Use custom set_language for better control
    path('i18n/setlang/', custom_set_language, name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
    # Setup endpoint (one-time admin creation)
    path('setup/create-admin/', create_initial_admin, name='create_initial_admin'),
]

# No root redirect needed - i18n_patterns handles root URL automatically

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('cv_extraction.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

