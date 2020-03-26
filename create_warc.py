#!/usr/bin/env python3
import sys

from urllib.parse import urlparse
from warcio.capture_http import capture_http

# warcio Documentation STRESSES to import requests after capture_http
import requests
from requests_html import HTML

def check_url_similarity(url_1, url_2):
    def check_path(path_1, path_2):
        # handles cases: cases where path are similar of have a trailing /
        if path_1 == path_2:
            return True
        if path_1 == path_2+'/' or \
               path_1+'/' == path_2:
            return True
        else:
            return False

    if len(url_2) == len(url_1):
        if url_1 == url_2:
            return True
    else:
        netloc_1 = urlparse(url_1).netloc
        netloc_2 = urlparse(url_2).netloc
        path_1 = urlparse(url_1).path
        path_2 = urlparse(url_2).path
        if netloc_1 == netloc_2:
            if check_path(path_1, path_2):
                return True
        if netloc_1 == 'www.'+netloc_2 or \
           'www.'+netloc_1 == netloc_2:
            if check_path(path_1, path_2):
                return True
        # TODO:
        # 1. add case for http and https distinction
    return False

if __name__ == "__main__":
    warc_file = '{}.warc.gz'.format(sys.argv[2])
    with capture_http(warc_file):
        response = requests.get(sys.argv[1])
        html = HTML(html=response.text, url=response.url)
        js_scripts = set([elem.attrs['src'] for elem in html.find('script') if 'src' in elem.attrs])
        styles = [elem.attrs['src'] for elem in html.find('style') if 'src' in elem.attrs]
        styles += [elem.attrs['href'] for elem in html.find('link') if 'href' in elem.attrs]
        style = set(styles)
        images = set([elem.attrs['src'] for elem in html.find('img') if 'src' in elem.attrs])
        for static_resource in set.union(js_scripts, styles, images):
            if not urlparse(static_resource).hostname:
                continue
            if check_url_similarity(static_resource, html.url):
                print('skipping: {}'.format(static_resource))
                continue
            if not urlparse(static_resource).scheme:
                static_resource = 'https:'+static_resource
            print('downloading resource: {}'.format(static_resource))
            requests.get(static_resource)

    print('Done getting archive of: {}'.format(sys.argv[1]))
