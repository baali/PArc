#!/usr/bin/env python3
import sys

from urllib.parse import urlparse
from warcio.capture_http import capture_http

# warcio Documentation STRESSES to import requests after capture_http
import requests
from requests_html import HTML

if __name__ == "__main__":
    warc_file = '{}.warc.gz'.format(sys.argv[2])
    with capture_http(warc_file):
        response = requests.get(sys.argv[1])
        html = HTML(html=response.text, url=response.url)
        js_scripts = [elem.attrs['src'] for elem in html.find('script') if 'src' in elem.attrs]
        styles = [elem.attrs['src'] for elem in html.find('style') if 'src' in elem.attrs]
        styles += [elem.attrs['href'] for elem in html.find('link') if 'href' in elem.attrs]
        images = [elem.attrs['src'] for elem in html.find('img') if 'src' in elem.attrs]
        for static_resource in js_scripts+styles+images:
            if not urlparse(static_resource).scheme:
                static_resource = 'https:'+static_resource
            print('downloading resource: {}'.format(static_resource))
            requests.get(static_resource)

    print('Done getting archive of: {}'.format(sys.argv[1]))
