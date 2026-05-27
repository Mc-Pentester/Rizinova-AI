# apps/core/middleware.py
from django.utils.deprecation import MiddlewareMixin

class IgnoreBrokenPipeMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, (BrokenPipeError, ConnectionResetError)):
            # Ignore ces exceptions pour ne pas polluer les logs
            return None
        # Laisser passer les autres exceptions normalement
        return None
