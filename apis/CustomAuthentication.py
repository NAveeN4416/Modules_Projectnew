from __future__ import unicode_literals

import base64
import binascii

from django.contrib.auth import get_user_model
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _

from rest_framework import HTTP_HEADER_ENCODING, exceptions
from rest_framework.compat import authenticate
from rest_framework.authentication import BaseAuthentication


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.

    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, text_type):
        # Work around django test client oddness
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        # Return the failure reason instead of an HttpResponse
        return reason


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'Token'
    model = None

    send = {'status':0, 'data':{}}

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    """
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            #return None
            self.send['status'] = '2'
            self.send['status_code'] = '401'
            self.send['message'] = 'Please Login !'
            raise exceptions.AuthenticationFailed(self.send)

        if len(auth) == 1:
            self.send['status'] = '2'
            self.send['status_code'] = '401'
            self.send['message'] = 'Invalid token header. No credentials provided.' 
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(self.send)
        elif len(auth) > 2:
            self.send['status'] = '2'
            self.send['status_code'] = '401'
            self.send['message'] = 'Invalid token header. Token string should not contain spaces.' 
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(self.send)

        try:
            token = auth[1].decode()
        except UnicodeError:
            self.send['status'] = '2'
            self.send['status_code'] = '401'
            send['message'] = 'Invalid token.'
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):

        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            self.send['status'] = '2'
            self.send['status_code'] = '401'
            self.send['message'] = 'Session expired! Please login again'
            raise exceptions.AuthenticationFailed(self.send)
            #raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            self.send['status_code'] = '401'
            self.send['message'] = 'User inactive or deleted.'
            raise exceptions.AuthenticationFailed(self.send)

        return (token.user, token)

    def authenticate_header(self, request):
        return self.keyword