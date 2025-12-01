"""
Views for authentication and role-based redirects.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import UserRegistrationForm, UserProfileEditForm
from .mixins import get_role_redirect_url


def register_view(request):
    """User registration view."""
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                logger.info(f'User {user.username} created successfully')
                
                # Login the user
                try:
                    login(request, user)
                    logger.info(f'User {user.username} logged in after registration')
                except Exception as login_error:
                    logger.error(f'Login error after registration: {str(login_error)}', exc_info=True)
                    messages.warning(request, 'Account created but login failed. Please login manually.')
                    return redirect('accounts:login')
                
                messages.success(request, 'Registration successful!')
                
                # Redirect based on role
                try:
                    redirect_url = get_role_redirect_url(user)
                    logger.info(f'Redirecting user {user.username} to {redirect_url}')
                    return redirect(redirect_url)
                except Exception as redirect_error:
                    logger.error(f'Redirect error: {str(redirect_error)}', exc_info=True)
                    # Fallback to home page
                    return redirect('cv_extraction:home')
                    
            except Exception as e:
                # Log the full error for debugging
                logger.error(f'Registration error: {str(e)}', exc_info=True)
                import traceback
                logger.error(f'Traceback: {traceback.format_exc()}')
                
                # Provide user-friendly error message
                error_msg = str(e)
                if 'UNIQUE constraint' in error_msg or 'duplicate' in error_msg.lower():
                    messages.error(request, 'Username or email already exists. Please choose different credentials.')
                elif 'role' in error_msg.lower() or 'field' in error_msg.lower():
                    messages.error(request, 'Registration failed due to invalid data. Please check your information and try again.')
                else:
                    messages.error(request, 'Registration failed. Please try again or contact support.')
        else:
            # Log form errors
            logger.warning(f'Registration form invalid: {form.errors}')
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    """Custom login view with role-based redirect."""
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        """Redirect based on user role after login."""
        from django.urls import reverse
        return reverse(get_role_redirect_url(self.request.user))


@login_required
def profile_view(request):
    """User profile view."""
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    """Edit user personal information."""
    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = UserProfileEditForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

