#!/usr/bin/env python3
import sys

from urllib.parse import urlparse
from warcio.capture_http import capture_http

# warcio Documentation STRESSES to import requests after capture_http
import requests
from requests_html import HTML

def check_url_similarity(url_1, url_2):
    '''Method of compare two URLs to identify if they are same or not.
    Returns bool: True/False based on comparison'''
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
        url_1_struct = urlparse(url_1)
        url_2_struct = urlparse(url_2)
        if url_1_struct.netloc == url_2_struct.netloc:
            if check_path(url_1_struct.path, url_2_struct.path):
                return True
        if url_1_struct.netloc == 'www.'+url_2_struct.netloc or \
           'www.'+url_1_struct.netloc == url_2_struct.netloc:
            if check_path(url_1_struct.path, url_2_struct.path):
                return True
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
