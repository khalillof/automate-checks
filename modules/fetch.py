#!/usr/bin/env python3
import json
import socket
from http.client import HTTPConnection, HTTPResponse, HTTPSConnection
from os import path
from shutil import make_archive
from urllib.error import URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import (HTTPBasicAuthHandler,
                            HTTPPasswordMgrWithDefaultRealm,
                            ProxyBasicAuthHandler, ProxyHandler, Request,
                            build_opener, install_opener, urlcleanup, urlopen,
                            urlretrieve)

from generator import get_random_string
from utils import getDir_OrMakeOne
from templates import EmailHtmlParser, HTMLEMAILParser
from html_template import html_template
"""
Sockets and Layers¶
The Python support for fetching resources from the web is layered. urllib uses the http.client library, which in turn uses the socket library.
As of Python 2.3 you can specify how long a socket should wait for a response before timing out. This can be useful in applications which have to fetch web pages. By default the socket module has no timeout and can hang. Currently, the socket timeout is not exposed at the http.client or urllib.request levels. 
However, you can set the default timeout globally for all sockets using import socket
"""
timeout = 10  # timeout in seconds
socket.setdefaulttimeout(timeout)


class Fetch:
    def __init__(self, url: str = None, port=None, httpConnection=True, ssl=True, proxy=False, auth=False, auth_username: str = None, auth_password: str = None) -> None:
        self.urlBase = ''
        self.urlPath = ''
        self.urlFull = ''
        if url:
            self.__update_url(url)
        self._proxy = proxy
        self._authUsername = auth_username
        self._authPassword = auth_password

        self._port = port if port else 443 if ssl else 80
        self._ssl = ssl

        self.is_httpConnection = httpConnection

        if auth:
            self.__authenticate()

        if self.is_httpConnection:
            self._connection = HTTPConnection(
                url, port, timeout=10) if not self._ssl else HTTPSConnection(url, port, timeout=10)

    def __update_url(self, url: str):
        _url = urlsplit(url)

        if _url.netloc:
            self.urlBase = _url.netloc

        path_url = url.replace(_url.scheme, '').replace(_url.netloc, '')
        if path_url and path_url != '':
            self.urlPath = path_url

        self.urlFull = "%s%s%s" % (_url.scheme, self.urlBase, self.urlPath)

    def encode(self, data):
        encoded_data = urlencode(data)
        encoded_data = encoded_data.encode('ascii')  # data should be bytes
        return encoded_data

    def request(self, **kwards):  # method='GET', url: str, body=None, headers: str

        self.__update_url(kwards.get('url'))

        if self.is_httpConnection:
            if 'body' in kwards:
                kwards['body'] = self.encode(kwards['body'])
                if 'Headers' not in kwards:
                    kwards.update({'Headers': self.header_formData()})

            self._connection.request(**kwards)
            return self.getresponse()
        else:
            if 'data' in kwards:
                kwards['data'] = self.encode(kwards['data'])
                if 'Headers' not in kwards:
                    kwards.update({'Headers': self.header_formData()})
            return self.getresponse(Request(**kwards))

    def getresponse(self, req_url: any = None):
        try:
            response: HTTPResponse
            if req_url:
                # for urlFetch request
                response = urlopen(req_url)
                self._connection = response

            elif self.is_httpConnection:
                # for httpFetch request
                response = self._connection.getresponse()
            else:
                print(
                    'some thing not right, coud not determing which class where the request is comming from ')

        except URLError as e:
            #  The except HTTPError must come first, otherwise except URLError will also catch an HTTPError.
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
        else:
            # everything is fine
            return fetchResponse(response, self.urlFull, self)

    def urlretrieve(self, url: str, filename: any):
        return urlretrieve(url=url, filename=filename)

    def static(self, url: str):
        return self.get(url=url, Headers=self.header_static())

    def get(self, url='/', **kwards):
        return self.request(method='GET', url=url, **kwards)

    def put(self, url='/', **kwards):
        return self.request(method='PUT', url=url, **kwards)

    def post(self, url='/', **kwards):
        return self.request(method='POST', url=url, **kwards)

    def json(self, **kwards):
        kwards['headers'] = self.header_json()
        if 'body' in kwards:
            kwards['body'] = json.dumps(kwards['body'])

        return self.request(**kwards)

    def header_json(self):
        return {'Content-type': 'application/json'}

    def header_static(self):
        return {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}

    def header_formData(self):
        return {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    def close(self):
        if self.is_httpConnection:
            self._connection.close()
        else:
            if hasattr(self._connection,'close'):
                self._connection.close()

    def __authenticate(self):

        passman = HTTPPasswordMgrWithDefaultRealm()
        # this creates a password manager
        passman.add_password(
            None, self.url, self._authUsername, self._authPassword)
        """ 
        because we have put None at the start it will always use this username/password combination for urls for which `self.url` is a super-url        
        """
        if self._proxy:
            # if you have proxy
            proxy_support = ProxyHandler({})
            proxy_auth_handler = ProxyBasicAuthHandler()
            proxy_auth_handler.add_password(passman)

            opener = build_opener(proxy_support, proxy_auth_handler)
            # This time, rather than install the OpenerDirector, we use it directly:
            return opener.open(self.urlBase)
            # request.install_opener(opener)
        else:
            authhandler = HTTPBasicAuthHandler(passman)
            # create the AuthHandler
            opener = build_opener(authhandler)
            # Install the opener.
            install_opener(opener)
            """ 
            All calls to urllib.urlopen will now use our handler Make sure not to include the protocol in with the URL, or
            HTTPPasswordMgrWithDefaultRealm will be very confused. You must (of course) use it when fetching the page though.
            """
            return opener.open(self.urlBase)
            # authentication is now handled automatically for us
    
    @staticmethod
    def Url(url:str="https://khaliltuban.co.uk"):
        return fetchResponse(urlopen(url),url)

    @staticmethod
    def http(baseUrl:str, path='/', method='GET', ssl=True):
        _connection = Fetch(url=baseUrl,ssl=ssl)
        return _connection.request(url=path, method=method)

# ============================================================================================================


class fetchResponse:
    def __init__(self, response: HTTPResponse, fullUrl: str = None, instance=None) -> None:
        self.response = response
        self.status_reason = "Status: {}, reason: {}".format(
            response.status, response.reason)
        self.url = fullUrl
        self.obj_instance = instance
    def data(self):
        with self.response as s:
            return s.read() if s.readable() else print('data is not readable')

    def mimeType(self):
        return self.response.getheader('Content-Type').split('/')

    def save_static_data(self):
        data = self.data()
        if data:
            mimeTypes = self.mimeType()
            fname = "%s%s%s%s%s" % (getDir_OrMakeOne(
                mimeTypes[0]), '/', get_random_string(8), '.', mimeTypes[1])
            with open(fname, 'wb') as f:
                f.write(data)
            return fname

    def close(self):
        if hasattr(self.obj_instance, 'close'):
            self.obj_instance.close()

        if hasattr(self.response, 'close'):
            self.response.close()
# =============================================================================================================


def archive(archive_name='myssh_archive', dir='.ssh'):
    archive_name = path.expanduser(path.join('~', archive_name))
    aps_dir = path.expanduser(path.join('~', dir))
    # format-specific extension; 'format' is the archive format: one of "zip", "tar", "gztar","bztar", or "xztar"
    return make_archive(archive_name, 'gztar', aps_dir)
    # return file path --'/ Users/tarek/myarchive.tar.gz'

    # unzip - tar -tzvf /Users/tarek/myarchive.tar.gz


if __name__ == "__main__":
    """
    # 'www.khaliltuban.co.uk/static/agency/images/310_170/driver.png'

    obj = Fetch(url='profdrivers.co.uk', port=443, ssl=True)
    res = obj.get(url='/images/logo100Tran.png')

    # obj=Fetch(httpConnection=False)
    #res= obj.get(url='https://profdrivers.co.uk/images/logo100Tran.png')

    print(res.save_data())
    # print(res.response.info())
    obj.close()
"""
#test_fire2()
#p=MyFancyHTMLParser()
#p.feed('<img src="python-logo.png" alt="The Python logo">')


#ft=Fetch.http(baseUrl='www.khaliltuban.co.uk', path='/static/agency/images/310_170/driver.png')
#ft=Fetch.Url(url='https://khaliltuban.co.uk/')
pers = HTMLEMAILParser()
#pers.feed(ft.data().decode())
pers.feed(html_template('helllllllo','hellow world'))
#ft.save_static_data()
#print(len(pers.mimeObj_list))
#ft.close()
pers.close()


