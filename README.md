django-sage
=============

This is a module for your Django project to connect with Sage API.
NOTE: At the moment, this have been only tested for Sage 200 and Sage 200 Extra.


Installation
============

Add 'sage_api' to INSTALLED_APPS
```
INSTALLED_APPS = (
      ...
      'sage_api',
      ...
)
```

Add 'sage-api' to urls.py
```
urlpatterns = (
      ...
      url(r'^sage-api/', include('sage_api.urls')),
      ...
)
```



Settings
========

```
SAGE_SETTINGS = {
    'AUTH_URL': 'https://signon.sso.services.sage.com/SSO/OAuthService/WebStartAuthorisationAttempt',
    'ACCESS_TOKEN_URL': 'https://signon.sso.services.sage.com/SSO/OAuthService/WebGetAccessToken',
    'AUTH_REDIRECT_URL': 'https://{{YOUR_DOMAIN}}/sage-api/authorise',
    'AUTH_SUCCESS_URL': '{{YOUR_SUCCESS_URL}}',
    'CLIENT_ID': '{{CLIENT_ID}}',
    'SECRET_KEY': '{{SECRET_KEY}}',
    'SCOPE': '{{CLIENT_SCOPE}}',

    'API_URL': 'https://api.columbus.sage.com/uk/sage200',
    'SIGNING_KEY': '{{SIGNING_KEY}}',
    'SUBSCRIPTION_KEY': '{{SIGNING_KEY}}',
}
```

*AUTH_URL*: URL to start OAuth authentication.

*ACCESS_TOKEN_URL*: URL to get and renew the *access_token*.

*AUTH_REDIRECT_URL*: URL OAuth should return to retrieve the auth_code. *Default: 'http://127.0.0.1:8000/sage-api/authorise'*.

*AUTH_SUCCESS_URL*: Internal URL to redirect the user after the authentication is complete. You can use url name if you wish. *Default: 'sage-api-success'*.

*CLIENT_ID*: Client ID of the application which authorization will be requested.

*SECRET_KEY*: Secret key of the application which authorization will be requested.

*SCOPE*: SCOPE of the authorization.

*API_URL*: API URL Base to make calls. *Default: 'https://api.columbus.sage.com/uk/sage200'*.

*SIGNING_KEY*: Your key to sign the requests.

*SUBSCRIPTION_KEY*: Your unique developer subscription key.



How to use
==========


Views
-----
```
from sage_api.models import Sage

def view_with_authorization_link(request):
    user = request.user

    # check if user is authenticated
    if not user.is_authenticated():
        # Authenticate the user

    authorization_url = Sage.get_authorization_url(user)
    context = RequestContext(request {
        ...
        'authorization_url': authorization_url
        ...
    })

    ...
```

HTML Template
-------------
```
...
<a href="{{authorization_url}}">Connect with Sage</a>
...
```
