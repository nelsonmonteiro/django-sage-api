from django import http
from .models import Sage
from .settings import SageSettings


def authorise(request):
    auth_code = request.GET.get('code', None)
    state_code = request.GET.get('state', None)

    if not auth_code:
        return http.HttpResponseBadRequest('Authorization code is required')

    if not state_code:
        return http.HttpResponseForbidden('State code is required to verify the request')

    user = request.user
    if not user.is_authenticated():
        return http.HttpResponseForbidden('User is not authenticated')

    Sage.create_for_user(user, auth_code, state_code)

    return http.HttpResponseRedirect(SageSettings().AUTH_SUCCESS_URL)


def success(request):
    pass
