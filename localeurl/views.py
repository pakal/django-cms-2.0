from urlparse import urlsplit
from django import http
from django.utils.translation import check_for_language
from localeurl import utils

def change_locale(request):
    """
    Redirect to a given url while changing the locale in the path
    The url and the locale code need to be specified in the
    request parameters.
    """
    
    # we assume the target url shares the same script name !
    script_name = request.META["SCRIPT_NAME"] 
    
    next = request.REQUEST.get('next', None)
    if not next:
        next = urlsplit(request.META.get('HTTP_REFERER', None))[2]
    if not next:
        next = request.META["SCRIPT_NAME"]+"/" # root of the django project
    
    if not next.startswith(script_name):
        script_name = ""
        locale, path_info = utils.strip_path(next)
    else:
        locale, path_info = utils.strip_path(next[len(script_name):])
     
     
    if request.method == 'POST':
        locale = request.POST.get('locale', None)   
        if locale and check_for_language(locale):
            path = utils.locale_path(path, locale, script_name)
            response = http.HttpResponseRedirect(path)
            return response
    
    return http.HttpResponseRedirect(next) # we failed language change    
    
