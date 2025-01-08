from django.utils.deprecation import MiddlewareMixin

class NoBackButtonMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Prevent caching of all pages that require authentication
        if request.user.is_authenticated:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response 