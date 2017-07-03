from django.core.urlresolvers import reverse, NoReverseMatch


class SageSettings(object):
    """
    Class to help the access to SAGE settings.
    """

    DEFAULT_SETTINGS = {
        'AUTH_URL': 'https://signon.sso.services.sage.com/SSO/OAuthService/WebStartAuthorisationAttempt',
        'AUTH_REDIRECT_URL': 'http://127.0.0.1:8000/sage-api/authorise/',
        'AUTH_SUCCESS_URL': 'sage-api-success',
        'ACCESS_TOKEN_URL': 'https://signon.sso.services.sage.com/SSO/OAuthService/WebGetAccessToken',
        'API_URL': 'https://api.columbus.sage.com/uk/sage200',
    }

    def __init__(self):
        from django.conf import settings
        self.__settings = getattr(settings, 'SAGE_SETTINGS', None)
        if not self.__settings:
            self._throw_error('SAGE_SETTINGS not defined in settings.py')

    def _get_setting(self, name):
        """
        Return the settings value from settings.py if exist, otherwise return the default value.
        For the settings that is required to define in the settings file, throws and error if they are not found.
        """
        setting = self.__settings.get(name, self.DEFAULT_SETTINGS.get(name, None))
        if not setting:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured('%s must be defined in SAGE_SETTINGS' % name)
        return setting

    @property
    def AUTH_URL(self):
        return self._get_setting('AUTH_URL')

    @property
    def AUTH_REDIRECT_URL(self):
        return self._get_setting('AUTH_REDIRECT_URL')

    @property
    def AUTH_SUCCESS_URL(self):
        return self._get_setting('AUTH_SUCCESS_URL')
        if url[:4] == 'http':
            return url
        return reverse(url)

    @property
    def ACCESS_TOKEN_URL(self):
        return self._get_setting('ACCESS_TOKEN_URL')

    @property
    def API_URL(self):
        return self._get_setting('API_URL')

    @property
    def CLIENT_ID(self):
        return self._get_setting('CLIENT_ID')

    @property
    def SECRET_KEY(self):
        return self._get_setting('SECRET_KEY')

    @property
    def SCOPE(self):
        return self._get_setting('SCOPE')

    @property
    def SIGNING_KEY(self):
        return self._get_setting('SIGNING_KEY')

    @property
    def SUBSCRIPTION_KEY(self):
        return self._get_setting('SUBSCRIPTION_KEY')

    @property
    def SITE_ID(self):
        return self._get_setting('SITE_ID')

    @property
    def COMPANY_ID(self):
        return self._get_setting('COMPANY_ID')

