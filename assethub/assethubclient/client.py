#!/usr/bin/env python

from os.path import join, basename
import sys
from io import BytesIO
import requests
from requests.auth import HTTPBasicAuth
import argparse
import getpass

class Asset(object):
    def __init__(self, json):
        self.dict = json

    def __getattr__(self, attr):
        return self.dict[attr]

#     def __setattr__(self, attr, val):
#         self.dict[attr] = val

    def json(self):
        return self.dict
    
    def __unicode__(self):
        return unicode(self.dict)

    def __str__(self):
        return str(self.dict)

    def __repr__(self):
        return repr(self.dict)

    def get_data_content_type(self):
        r = requests.head(self.data)
        r.raise_for_status()
        return r.headers.get('content-type', None)

    def download_data(self, outpath):
        r = requests.get(self.data)
        r.raise_for_status()
        with open(outpath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)

    def get_data(self, content_type=None):
        r = requests.get(self.data)
        r.raise_for_status()
        if content_type is not None:
            if r.headers.get('content-type', None) != content_type:
                raise TypeError("Asset data is not of type " + content_type)
        f = BytesIO()
        for chunk in r.iter_content(chunk_size=1024):
            f.write(chunk)
        result = f.getvalue()
        f.close()
        return result

    def get_filename(self):
        return basename(self.data)

class AssetHubClient(object):
    def __init__(self, url, application=None, component=None, username=None, password=None):
        self.url = url
        self._base_url = join(self.url, 'api', 'assets')
        if not self._base_url.endswith('/'):
            self._base_url = self._base_url + '/'
        self.application = application
        self.component = component
        self.username = username
        self.password = password
        self.tag = None
        self.author = None
        self.id = None
        self.license = None
        self.asset_constructor = Asset

    def _get_url(self):
        if self.id is not None:
            return join(self._base_url, self.id)
        elif self.application is not None and self.component is not None:
            return join(self._base_url, self.application, self.component)
        elif self.application is not None:
            return join(self._base_url, self.application)
        else:
            return self._base_url

    def _get_params(self):
        params = {}
        if self.tag is not None:
            params['tag'] = self.tag
        if self.author is not None:
            params['author'] = author
        return params

    def list(self):
        r = requests.get(self._get_url(), params=self._get_params())
        r.raise_for_status()
        json = r.json()
        if isinstance(json, list):
            return [self.asset_constructor(a) for a in r.json()]
        else:
            return [self.asset_constructor(json)]

    def get(self, id):
        url = join(self._base_url, str(id))
        r = requests.get(url)
        r.raise_for_status()
        return self.asset_constructor(r.json())

    def post(self, asset, data_file, image_file=None):
        auth = HTTPBasicAuth(self.username, self.password)
        data = asset.json()
        files = dict(data=data_file)
        if image_file is not None:
            files['image'] = image_file
        r = requests.post(self._base_url, data=data, files=files, auth=auth)
        r.raise_for_status()
        return r.json()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='AssetHub command-line client')
    parser.add_argument('-u', '--url', metavar='HTTP://SERVER.ORG/', help='AssetHub server URL')
    parser.add_argument('-a', '--application', metavar='APP', help='Application')
    parser.add_argument('-c', '--component', metavar='COMPONENT', help='Component')
    parser.add_argument('--author', metavar='USER', help='Asset author')
    parser.add_argument('--id', metavar='ID', help='Asset ID')
    parser.add_argument('-t', '--tag', metavar='TAG', help='Asset tag')
    parser.add_argument('-L', '--license', metavar='LICENSE', help='Asset license')
    parser.add_argument('--title', metavar='TITLE', help='Asset title')
    parser.add_argument('-J', '--json', action='store_true', help='Output data as JSON')
    parser.add_argument('-D', '--download', action='store_true', help='Download asset data')
    parser.add_argument('-P', '--post', metavar='FILENAME.dat', help='Post new asset')
    parser.add_argument('-T', '--thumb', metavar='FILENAME.png', help='Thumbnail for new asset')
    parser.add_argument('--content-type', action='store_true', help='Print data content type')
    parser.add_argument('-U', '--user', metavar='USER', help='User name')
    parser.add_argument('-W', '--password', metavar='PASSWORD', help='Password')
    args = parser.parse_args()

    if args.url:
        url = args.url
    else:
        url = 'http://assethub.iportnov.tech/'

    client = AssetHubClient(url, args.application, args.component)
    client.tag = args.tag
    client.author = args.author
    client.id = args.id

    if args.post:
        if not args.title:
            print("Title is mandatory when posting an asset")
            sys.exit(1)
        if not args.application:
            print("Application is mandatory when posting an asset")
            sys.exit(1)
        if not args.component:
            print("Component is mandatory when posting an asset")
            sys.exit(1)
        if not args.license:
            print("License is not specified, defaulting to CC0")
            args.license = "CC0"
        asset = Asset(dict(title=args.title, application=args.application, component=args.component, license=args.license))
        if not args.user:
            print("User name is mandatory to post an asset")
            sys.exit(1)
        client.username = args.user
        if not args.password:
            client.password = getpass.getpass()
        else:
            client.password = args.password

        data_file = open(args.post, 'rb')
        if args.thumb:
            image_file = open(args.thumb, 'rb')
        else:
            image_file = None
        client.post(asset, data_file, image_file)

    else:

        for asset in client.list():
            if args.download:
                asset.download_data(asset.get_filename())
                print("Downloaded " + asset.get_filename())
            elif args.json:
                print(asset)
            elif args.content_type:
                print("{}\t{}\t{}".format(asset.id, asset.title, asset.get_data_content_type()))
            else:
                print("{}\t{}".format(asset.id, asset.title))

