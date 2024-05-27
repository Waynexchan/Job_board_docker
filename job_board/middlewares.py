import logging
from django.utils.deprecation import MiddlewareMixin

class IgnoreHEADRequestsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'HEAD':
            logging.getLogger('django.request').setLevel(logging.CRITICAL)

    def process_response(self, request, response):
        if request.method == 'HEAD':
            logging.getLogger('django.request').setLevel(logging.DEBUG)
        return response