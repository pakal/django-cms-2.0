from django.conf import settings
import django.core.exceptions
from django.http import HttpResponsePermanentRedirect, HttpResponse
from django.utils import translation
# TODO importing undocumented function
from django.utils.translation.trans_real import parse_accept_lang_header
from localeurl import settings as localeurl_settings
from localeurl import utils
import sys, os
# Make sure the default language is in the list of supported languages
assert utils.supported_language(settings.LANGUAGE_CODE) is not None, \
        "Please ensure that settings.LANGUAGE_CODE is in settings.LANGUAGES."

class LocaleURLMiddleware(object):
    """
    Middleware that sets the language based on the request path prefix and
    strips that prefix from the path. It will also automatically redirect any
    path without a prefix, unless PREFIX_DEFAULT_LOCALE is set to True.
    Exceptions are paths beginning with MEDIA_URL (if
    settings.LOCALE_INDEPENDENT_MEDIA_URL is set) or matching any regular
    expression from LOCALE_INDEPENDENT_PATHS from the project settings.

    For example, the path '/en/admin/' will set request.LANGUAGE_CODE to 'en'
    and request.path to '/admin/'.

    If you use this middleware the django.core.urlresolvers.reverse function
    must be patched to return paths with locale prefix (see models.py).
    """
    def __init__(self):
        if not settings.USE_I18N:
            raise django.core.exceptions.MiddlewareNotUsed()

    def process_request(self, request):
        
        #  we check if another middleware has already set the language, eg. from domain name
        if not hasattr(request, "LANGUAGE_CODE") or not request.LANGUAGE_CODE: 
            
            locale, path = utils.strip_path(request.path_info)
             
            #return HttpResponse(str((request.META["SCRIPT_NAME"], request.path_info, locale)))
            
            if localeurl_settings.USE_ACCEPT_LANGUAGE and not locale:
                accept_langs = filter(lambda x: x, 
                                      [utils.supported_language(lang[0])
                                       for lang in parse_accept_lang_header(
                                       request.META.get('HTTP_ACCEPT_LANGUAGE', ''))])
                if accept_langs:
                    locale = accept_langs[0]
            locale_path = utils.locale_path(path, locale)
        
            if locale_path != request.path_info:
                
                full_path = ''.join([request.META["SCRIPT_NAME"], locale_path])
                                          
                query = request.META.get("QUERY_STRING", "")
                if query:
                    full_path = "%s?%s" % (full_path, query)
                    
                return HttpResponsePermanentRedirect(full_path)
            
            request.path_info = path
            if not locale:
                try:
                    locale = request.LANGUAGE_CODE
                except AttributeError:
                    locale = settings.LANGUAGE_CODE
            translation.activate(locale)
            request.LANGUAGE_CODE = locale

    def process_response(self, request, response):
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response
