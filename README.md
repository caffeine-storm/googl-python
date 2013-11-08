# Sample usage

    import googl

    client = googl.Googl("API_key")

    result = client.shorten("http://code.google.com/p/python-googl-client/")
    print result
    >>> {
        u'kind': u'urlshortener#url',
        u'id': u'http://goo.gl/bUnil',
        u'longUrl': u'http://code.google.com/p/python-googl-client/'
    }

    print client.expand(result["id"])
    >>> {
        u'status': u'OK',
        u'kind': u'urlshortener#url',
        u'id': u'http://goo.gl/WubiJ',
        u'longUrl': u'http://code.google.com/p/python-googl-client/'
    }

# ClientLogin Auth

    client_login = googl.ClientLoginAuth("login", "pass")
    client = googl.Googl("API_key", auth=client_login)

# OAuth2
    oauth = googl.OAuth2Authorizer('oauth2 access token')
    client = googl.Googl("API_key", auth=oauth)

