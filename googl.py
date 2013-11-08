﻿#!/usr/bin/env python
"""
Python client library for the Goo.gl API.

Ivan Grishaev <ivan@grishaev.me>

See http://code.google.com/intl/en/apis/urlshortener/overview.html

Usage:

import googl

client = googl.Googl("API_key")

result = client.shorten("http://code.google.com/p/python-googl-client/")
print result
>>> {u'kind': u'urlshortener#url', u'id': u'http://goo.gl/bUnil',
        u'longUrl': u'http://code.google.com/p/python-googl-client/'}

print client.expand(result["id"])
>>> {u'status': u'OK', u'kind': u'urlshortener#url',
        u'id': u'http://goo.gl/WubiJ',
        u'longUrl': u'http://code.google.com/p/python-googl-client/'}

oauth_client = googl.Googl("API_key", auth=googl.OAuth2Authorizer('oauth2_access_token')
"""
__version__ = "0.1.1"
__author__ = "Ivan Grishaev"

import urllib
import urllib2

# Searching for JSON library.
try:
    import json # Python >= 2.6
except ImportError:
    try:
        import simplejson as json # Python <= 2.5
    except ImportError:
        try:
            from django.utils import simplejson as json # GAE
        except ImportError:
            raise ImportError("JSON library not found.")

API_URL = "https://www.googleapis.com/urlshortener/%s/url"

PROJ_FULL = "FULL"
PROJ_CLICKS = "ANALYTICS_CLICKS"
PROJ_TOP = "ANALYTICS_TOP_STRINGS"


class GooglError(Exception):
    """Goo.gl API error class."""
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return "Goo.gl error, code: %d, reason: %s" % (self.code, self.message)

class OAuth2Authorizer(object):
    def __init__(self, access_token):
        self.access_token = access_token

    def authorize(self, request):
        request.add_header('Authorization', 'Bearer ' + self.access_token)

class ClientLoginAuth(object):
    def __init__(self, email, password):
        self.token_string = ClientLoginAuth._get_client_login(email, password)

    @staticmethod
    def _get_client_login(email, password):
        """Get client login by user creditants."""
        import gdata.service
        service = gdata.service.GDataService()
        service.ClientLogin(email, password, service="urlshortener")
        return service.current_token.get_token_string()

    def authorize(self, request):
        request.add_header("Authorization", "GoogleLogin auth=%s" % self.token_string)

class Googl(object):
    """Goo.gl API class.

    key: your API key, get it here: http://code.google.com/apis/console/ client_login: token for ClientLogin authenticating mechanism
    api: current API version
    referer: optional Referer header (for Referer API limits)
    userip: optional IP (for IP API limits)
    """
    def __init__(self, key, auth=None, api="v1", userip=None, referer=None):
        self.auth = auth
        self.key = key
        self.api = api
        self.userip = userip
        self.referer = referer

    def shorten(self, longUrl):
        """Creates a new short URL."""
        data = json.dumps(dict(longUrl=longUrl))
        headers = {"Content-Type": "application/json"}
        return self.__call(data=data, headers=headers)

    def expand(self, shortUrl, projection=None):
        """Gets expansion information for a specified short URL.

        shortUrl: short URL, i.e. http://goo.gl/HdM99
        projection: additional information to return, one of the PROJ_ constants
        """
        params = dict(shortUrl=shortUrl)
        if projection is not None:
            params.update(projection=projection)
        return self.__call(params=params)

    def history(self, projection=None, nexttoken=None):
        """Retrieves a list of URLs shortened by the authenticated user.

        Authentication is required.

        projection: additional information to return, one of the PROJ_ constants.
            Possible values are PROJ_FULL or PROJ_CLICKS constants.
        nexttoken: index into the paginated list, "nextPageToken" key in result.
        """
        url = API_URL + "/history"
        params = {}
        if projection is not None:
            params["projection"] = projection
        if nexttoken is not None:
            params["start-token"] = nexttoken
        return self.__call(url=url, params=params)

    def __call(self, url=API_URL, params={}, data=None, headers={}):
        """Common method for API call.

        url: API URL
        params: query string parameters
        data: POST data
        headers: additional request headers

        Return: parsed JSON structure or raise GooglError.
        """
        params.update(key=self.key)
        if self.userip is not None:
            params.update(userip=self.userip)

        full_url = "%s?%s" % (url % self.api, urllib.urlencode(params))

        request = urllib2.Request(full_url, data=data, headers=headers)

        if self.referer is not None:
            request.add_header("Referer", self.referer)
        if self.auth is not None:
            self.auth.authorize(request)

        try:
            response = urllib2.urlopen(request)
            return json.loads(response.read())
        except urllib2.HTTPError, e:
            error = json.loads(e.fp.read())
            raise GooglError(error["error"]["code"], error["error"]["message"])

