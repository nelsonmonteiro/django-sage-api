from __future__ import unicode_literals
try:
    from urllib import urlencode, quote
except ImportError:
    from urllib.parse import urlencode, quote
import json
import pytz
import datetime
import base64
import requests
import hashlib
import hmac
import urlparse
from collections import OrderedDict
from uuid import uuid4
from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import PermissionDenied
from .settings import SageSettings


sage_settings = SageSettings()


@python_2_unicode_compatible
class Sage(models.Model):
    """
    Model to connect and save tokens from SAGE API related with a specific user.
    """
    class Meta:
        verbose_name = 'Sage account'
        verbose_name_plural = 'Sage accounts'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='sage')
    access_token_key = models.CharField(max_length=2048, blank=True, null=True)
    access_token_type = models.CharField(max_length=20)
    access_token_expires_on = models.DateTimeField(null=True, blank=True)
    refresh_token = models.CharField(max_length=200, blank=True, null=True)
    refresh_token_expires_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '%s' % self.user

    @classmethod
    def get_authorization_url(cls, user):
        """
        Return the link to use for oAuth authentication.
        """
        state_code, created = AuthStateCode.objects.get_or_create(user=user, defaults={'code': uuid4()})

        params = {
            'client_id': sage_settings.CLIENT_ID,
            'response_type': 'code',
            'state': state_code.code,
            'redirect_uri': sage_settings.AUTH_REDIRECT_URL,
            'scope': sage_settings.SCOPE,
        }
        return '%s?%s' % (sage_settings.AUTH_URL, urlencode(params))

    @classmethod
    def create_for_user(cls, user, auth_code, state_code):
        """
        Create a Sage model for an user and generates the first access token.
        Verify if the state code is valid to protect from attacks.
        """
        try:
            state_code = AuthStateCode.objects.get(user=user, code=state_code)
            state_code.delete()
            sage_auth, created = cls.objects.get_or_create(user=user)
            sage_auth.__get_access_token(auth_code)
        except AuthStateCode.DoesNotExist:
            raise PermissionDenied('State code is invalid for this user')

    def __set_access_token(self, response):
        """
        Saves access_token json response fields on database to use it later.
        """
        if not ('error' in response):
            now = datetime.datetime.now(tz=pytz.utc)
            self.access_token_key = response['access_token']
            self.access_token_type = response['token_type']
            self.access_token_expires_on = now + datetime.timedelta(seconds=response['expires_in'])
            self.refresh_token = response['refresh_token']
            self.refresh_token_expires_on = now + datetime.timedelta(seconds=response['refresh_token_expires_in'])
            self.save()

    def __get_access_token(self, code):
        """
        Make an API call to get the access_token from the authorization_code.
        """
        params = urlencode({
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': sage_settings.AUTH_REDIRECT_URL,
        })

        authorization = base64.b64encode('%s:%s' % (sage_settings.CLIENT_ID, sage_settings.SECRET_KEY))
        request = requests.post(sage_settings.ACCESS_TOKEN_URL, params, headers={
            'Authorization': 'Basic %s' % authorization,
            'ContentType': 'application/x-www-form-urlencoded;charset=UTF-8',
        })
        self.__set_access_token(request.json())

    def __refresh_access_token(self):
        """
        Make an API call to renew the access_token. 
        """
        params = urlencode({
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
        })

        authorization = base64.b64encode('%s:%s' % (sage_settings.CLIENT_ID, sage_settings.SECRET_KEY))
        request = requests.post(sage_settings.ACCESS_TOKEN_URL, params, headers={
                'Authorization': 'Basic %s' % authorization,
                'ContentType': 'application/x-www-form-urlencoded;charset=UTF-8',
        })
        self.__set_access_token(request.json())

    @property
    def access_token(self):
        """
        Return a valid access_token. 
        """
        now = datetime.datetime.now(tz=pytz.utc)

        if self.access_token_expires_on < now:
            if self.refresh_token_expires_on > now:
                self.__refresh_access_token()
            else:
                return None
        return self.access_token_key

    def __get_signature(self, url, params, data, method, nonce):
        """
        Return the signature to put in the API request's headers.
        """
        if method in ['POST', 'PUT']:
            params['body'] = base64.b64encode(json.dumps(data))

        ordered_params = OrderedDict(sorted(params.items()))
        encoded_params = quote(urlencode(ordered_params), safe='')

        raw_string = '%s&%s&%s&%s' % (method, quote(url.lower(), safe=''), encoded_params, nonce)
        signing_key = '%s&%s' % (quote(sage_settings.SIGNING_KEY, safe=''), quote(self.access_token, safe=''))

        signature = hmac.new(signing_key, raw_string, hashlib.sha1).digest().encode('base64').rstrip('\n')
        return signature

    def __get_headers(self, url, params, data, method, site_id=None, company_id=None):
        """
        Return the API request's headers already with signature.
        """
        nonce = str(uuid4().hex)
        return {
            'Authorization': '%s %s' % (self.access_token_type.capitalize(), self.access_token),
            'ocp-apim-subscription-key': sage_settings.SUBSCRIPTION_KEY,
            'X-Site': site_id or '',
            'X-Company': company_id or '',
            'X-Signature': self.__get_signature(url, params, data, method, nonce),
            'X-Nonce': nonce,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

    @staticmethod
    def __get_absolute_url(relative_url):
        """
        Return the absolute url for a API call.
        """
        return urlparse.urljoin(sage_settings.API_URL, relative_url)

    @staticmethod
    def __clean_response(response):
        if response.status_code != 200:
            error_msg = """
            STATUS_CODE: 
            %(status_code)s
            
            URL: 
            %(url)s
            
            REQUEST HEADERS:
            %(request_headers)s
            
            REQUEST BODY: 
            %(request_body)s
            
            RESPONSE HEADERS:
            %(response_headers)s
            
            RESPONSE BODY:
            %(response_body)s
            
            """ % {
                'status_code': response.status_code,
                'url':  response.request.url,
                'request_headers': response.request.headers,
                'request_body': response.request.body,
                'response_headers': response.headers,
                'response_body': response.content,
            }
            raise Exception(error_msg)
        return response.json()

    def api_get(self, relative_url, params=None, site_id=None, company_id=None):
        """
        Make an API GET request.
        """
        url = self.__get_absolute_url(relative_url)
        params = params or {}
        headers = self.__get_headers(url, params or {}, {}, 'GET', site_id, company_id)
        if params:
            url = '%s?%s' % (url, urlencode(params))
        response = requests.get(url, headers=headers)
        return self.__clean_response(response)

    def api_post(self, relative_url, params=None, data=None, site_id=None, company_id=None):
        """
        Make an API POST request.
        """
        url = self.__get_absolute_url(relative_url)
        params = params or {}
        data = data or {}
        headers = self.__get_headers(url, params, data, 'POST', site_id, company_id)
        if params:
            url = '%s?%s' % (url, urlencode(params))
        response = requests.post(url, json.dumps(data), headers=headers)
        return self.__clean_response(response)

    def api_put(self, relative_url, params=None, data=None, site_id=None, company_id=None):
        """
        Make an API PUT request.
        """
        url = self.__get_absolute_url(relative_url)
        params = params or {}
        data = data or {}
        headers = self.__get_headers(url, params or {}, data, 'PUT', site_id, company_id)
        if params:
            url = '%s?%s' % (url, urlencode(params))
        response = requests.put(url, json.dumps(data), headers=headers)
        return self.__clean_response(response)

    def api_delete(self, relative_url, params=None, site_id=None, company_id=None):
        """
        Make an API DELETE request.
        """
        url = self.__get_absolute_url(relative_url)
        params = params or {}
        headers = self.__get_headers(url, params, {}, 'DELETE', site_id, company_id)
        if params:
            url = '%s?%s' % (url, urlencode(params))
        response = requests.delete(url, headers=headers)
        return self.__clean_response(response)

    def get_sites(self):
        return self.api_get('accounts/v1/sites')


@python_2_unicode_compatible
class AuthStateCode(models.Model):
    """
    Model to save a random code for an user to prevent external attacks.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='sage_state_code')
    code = models.CharField(max_length=50)

    def __str__(self):
        return '%s' % self.user
