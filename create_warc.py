#!/usr/bin/env python3
import sys
import re

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

def find_js_urls(html):
    '''Find urls to all JS files used in the HTML'''
    js_urls = [elem.attrs['src'] for elem in html.find('script') if 'src' in elem.attrs]
    print("Found {} urls for Javascripts".format(len(js_urls)))
    return js_urls

def find_img_urls(html):
    '''Find urls to all images being used in the HTML'''
    img_urls = [elem.attrs['src'] for elem in html.find('img') if 'src' in elem.attrs]
    print("Found {} urls for images".format(len(img_urls)))
    return img_urls

def find_css_urls(html):
    '''Find urls to all stylesheets used in the HTML'''
    css_urls = []
    # linked CSS that uses link tag. syntax: <link href="css_file.css" rel="stylesheet" type="text/css" media="all">
    for elem in html.find('link'):
        if 'stylesheet' in elem.attrs.get('rel'):
            if 'href' in elem.attrs:
                css_urls.append(elem.attrs['href'])
    # Linked CSS that uses style tag. syntax: <link href="css_file.css" rel="stylesheet" type="text/css" media="all">
    for elem in html.find('style'):
        if 'src' in elem.attrs:
            print('src inside style ', elem.html)
            css_urls.append(elem.attrs['src'])

    # Linked CSS that uses style tag and uses @import. syntax: <style type="text/css" media="all">\n@import url("//www.mygov.in/modules/system/system.base.css?q7y7yf");</style>
    for elem in html.find('style'):
        for url in re.findall(r'url\((.*?)\)', elem.html):
            if url[0] == '"' or url[0] == "'":
                # To avoid redundant quotes around url: 
                css_urls.append(url[1:-1])
            else:
                # To cover cases where link is not part of quotes:
                # url(https://www.hindustantimes.com/images/app-images/2019/4/authors/footer-sprite.svg)
                # This seems to be happening with HindustanTimes pages
                css_urls.append(url)
    print("Found {} urls for CSS files".format(len(css_urls)))
    return css_urls

def get_all_static_urls(html):
    static_urls = set.union(
        set(find_js_urls(html)),
        set(find_img_urls(html)),
        set(find_css_urls(html))
        )
    return static_urls


def filter_records(request, response, recorder):
    if response.http_headers.get_statuscode() != '200':
        print("skipping {}".format(request.http_headers.get_statuscode()))
        return None, None
    return request, response

if __name__ == "__main__":
    warc_file = '{}.warc.gz'.format(sys.argv[2])
    with capture_http(warc_file, filter_records):
        response = requests.get(sys.argv[1])
        html = HTML(html=response.text, url=response.url)
        static_resource_urls = get_all_static_urls(html)
        for static_resource in static_resource_urls:
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
