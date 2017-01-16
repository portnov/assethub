#!/usr/bin/env python

from os.path import join, basename
import requests
import argparse

class Asset(object):
    def __init__(self, json):
        self.dict = json

    def __getattr__(self, attr):
        return self.dict[attr]

    def json(self):
        return self.dict
    
    def __unicode__(self):
        return unicode(self.dict)

    def __str__(self):
        return str(self.dict)

    def __repr__(self):
        return repr(self.dict)

    def download_data(self, outpath):
        r = requests.get(self.data)
        r.raise_for_status()
        with open(outpath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)

    def get_filename(self):
        return basename(self.data)

class AssetHubClient(object):
    def __init__(self, url, application=None, component=None):
        self.url = url
        self._base_url = join(self.url, 'api', 'assets')
        self.application = application
        self.component = component
        self.tag = None
        self.author = None
        self.id = None

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
        return [Asset(a) for a in r.json()]

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='AssetHub command-line client')
    parser.add_argument('-u', '--url', metavar='HTTP://SERVER.ORG/', help='AssetHub server URL')
    parser.add_argument('-a', '--application', metavar='APP', help='Application')
    parser.add_argument('-c', '--component', metavar='COMPONENT', help='Component')
    parser.add_argument('--author', metavar='USER', help='Asset author')
    parser.add_argument('--id', metavar='ID', help='Asset ID')
    parser.add_argument('-t', '--tag', metavar='TAG', help='Asset tag')
    parser.add_argument('-J', '--json', action='store_true', help='Output data as JSON')
    parser.add_argument('-D', '--download', action='store_true', help='Download asset data')
    args = parser.parse_args()

    if args.url:
        url = args.url
    else:
        url = 'http://assethub.iportnov.tech/'

    client = AssetHubClient(url, args.application, args.component)
    client.tag = args.tag
    client.author = args.author
    client.id = args.id
    for asset in client.list():
        if args.download:
            asset.download_data(asset.get_filename())
            print("Downloaded " + asset.get_filename())
        elif args.json:
            print(asset)
        else:
            print("{}\t{}".format(asset.id, asset.title))

