import unittest
from create_warc import check_url_similarity

class TestUrlSimilarity(unittest.TestCase):
    def test_trailing_slash(self):
        url_1 = "https://www.mygov.in/covid-19/"
        url_2 = "https://www.mygov.in/covid-19"
        self.assertTrue(check_url_similarity(url_1, url_2))

    def test_missing_www_subdomain(self):
        url_1 = "https://mygov.in/covid-19"
        url_2 = "https://www.mygov.in/covid-19"
        self.assertTrue(check_url_similarity(url_1, url_2))

    def test_missing_www_subdomain_and_trailing_slash(self):
        url_1 = "https://mygov.in/covid-19/"
        url_2 = "https://www.mygov.in/covid-19"
        self.assertTrue(check_url_similarity(url_1, url_2))

        url_1 = "https://mygov.in/covid-19"
        url_2 = "https://www.mygov.in/covid-19/"
        self.assertTrue(check_url_similarity(url_1, url_2))

    def test_http_difference(self):
        url_1 = "https://mygov.in/covid-19"
        url_2 = "http://www.mygov.in/covid-19"
        self.assertTrue(check_url_similarity(url_1, url_2))

    def test_different_url(self):
        url_1 = "https://mygov.in/covid-19"
        url_2 = "https://www.india.gov.in/"
        self.assertFalse(check_url_similarity(url_1, url_2))

if __name__ == '__main__':
    unittest.main()
