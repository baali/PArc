import unittest
from create_warc import find_css_urls
from requests_html import HTML

class TestCSSLink(unittest.TestCase):
    def setUp(self):
        html_src = open('page.html', 'r')
        self.html = HTML(html=html_src.read())
        html_src.close()

    def test_css_links_with_links(self):
        css_links = find_css_urls(self.html)
        self.assertTrue(css_links)

    def test_css_links_with_no_css(self):
        src = '''
<!DOCTYPE html>
<html data-ng-app="site_stats_display" xml:lang="en"
      version="XHTML+RDFa 1.0" dir="ltr"
      xmlns:fb="http://ogp.me/ns/fb#"
      xmlns:og="http://ogp.me/ns#"
      xmlns:article="http://ogp.me/ns/article#"
      xmlns:book="http://ogp.me/ns/book#"
      xmlns:profile="http://ogp.me/ns/profile#"
      xmlns:video="http://ogp.me/ns/video#">

  <head>
  </head>
  <body>
  </body>
</html>
'''
        html = HTML(html=src)
        css_links = find_css_urls(html)
        self.assertFalse(css_links)

    def test_link_import_css(self):
        src = '''
<!DOCTYPE html>
<html data-ng-app="site_stats_display" xml:lang="en">
  <head>
    <style type="text/css" media="all">
      @import url("//www.mygov.in/modules/system/system.base.css?q7y7yf");
      @import url("//www.mygov.in/modules/system/system.menus.css?q7y7yf");
      @import url("//www.mygov.in/modules/system/system.messages.css?q7y7yf");
      @import url("//www.mygov.in/modules/system/system.theme.css?q7y7yf");
    </style>
  </head>
  <body>
  </body>
</html>
'''
        html = HTML(html=src)
        css_links = find_css_urls(html)
        self.assertTrue(css_links)
        self.assertEqual(len(css_links), 4)
        
    def test_link_href_css(self):
        src = '''
<!DOCTYPE html>
<html data-ng-app="site_stats_display" xml:lang="en">
  <head>
    <link href="default.css" rel="stylesheet" title="Default Style">
    <link href="fancy.css" rel="alternate stylesheet" title="Fancy">
    <link href="basic.css" rel="alternate stylesheet" title="Basic">
  </head>
  <body>
  </body>
</html>
'''
        html = HTML(html=src)
        css_links = find_css_urls(html)
        self.assertTrue(css_links)
        self.assertEqual(len(css_links), 3)
if __name__ == '__main__':
    unittest.main()
