from django.conf import settings
from django.core import urlresolvers
from django.utils import translation
from localeurl import utils

django_reverse = None # original django reverse()

def reverse(*args, **kwargs):
    reverse_kwargs = kwargs.get('kwargs', {}) or {}
    locale = utils.supported_language(reverse_kwargs.pop('locale',
            translation.get_language()))
    url = django_reverse(*args, **kwargs)
    script_name, path_info = utils.strip_script_prefix(url)
    return utils.locale_url(path_info, locale, script_name)


def patch_reverse():
    """
    Monkey-patches the urlresolvers.reverse function. Will not patch twice.
    """
    global django_reverse
    if urlresolvers.reverse is not reverse:
        django_reverse = urlresolvers.reverse
        urlresolvers.reverse = reverse

if settings.USE_I18N:
    patch_reverse()
