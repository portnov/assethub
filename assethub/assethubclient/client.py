#!/usr/bin/env python

from os.path import join
import requests
import argparse

class AssetHubClient(object):
    def __init__(self, url, application=None, component=None):
        self.url = url
        self._base_url = join(self.url, 'api', 'assets')
        self.application = application
        self.component = component
        self.tag = None

    def _get_url(self):
        if self.application is not None and self.component is not None:
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
        return r.json()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='AssetHub command-line client')
    parser.add_argument('-u', '--url', metavar='HTTP://SERVER.ORG/', help='AssetHub server URL')
    parser.add_argument('-a', '--application', metavar='APP', help='Application')
    parser.add_argument('-c', '--component', metavar='COMPONENT', help='Component')
    parser.add_argument('--author', metavar='USER', help='Asset author')
    parser.add_argument('-t', '--tag', metavar='TAG', help='Asset tag')
    args = parser.parse_args()

    if args.url:
        url = args.url
    else:
        url = 'http://assethub.iportnov.tech/'

    client = AssetHubClient(url, args.application, args.component)
    client.tag = args.tag
    client.author = args.author
    for asset in client.list():
        print(asset['title'])
