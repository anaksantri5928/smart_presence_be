"""
Custom authentication for token-based authentication
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class CustomTokenAuthentication(BaseAuthentication):
    """
    Custom token authentication that works with our User model token field
    """
    
    def authenticate(self, request):
        # Get the Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None  # No authentication provided
            
        # Check if it's a Bearer token
        try:
            auth_type, token = auth_header.split(' ')
            if auth_type.lower() != 'bearer':
                return None  # Not a Bearer token
        except ValueError:
            return None  # Invalid header format
            
        if not token:
            return None  # No token provided
            
        # Validate the token
        try:
            user = User.objects.get(token=token)
            
            # Check if token is still valid (optional: add expiration)
            if hasattr(user, 'token_created') and user.token_created:
                # Example: tokens expire after 24 hours
                from datetime import timedelta
                if timezone.now() - user.token_created > timedelta(hours=24):
                    raise AuthenticationFailed('Token has expired')
            
            return (user, token)
            
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid token')
    
    def authenticate_header(self, request):
        return 'Bearer realm="api"'