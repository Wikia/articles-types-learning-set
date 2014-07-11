import requests


class WikiaSearch(object):
    select_url = None
    config = {'url': 'http://search-s11:8983/solr', 'core': 'main'}

    def __init__(self):
        self.select_url = self.config['url'] + '/' + self.config['core'] + '/select?q='

    def __build_url(self, query, filter_query='', start=0, rows=10, sort=''):
        final_url = list()
        final_url.append(self.select_url + query)

        if filter_query is not '':
            final_url.append('fq=%s' % filter_query)

        final_url.append('start=%d&rows=%d' % (start, rows))

        if sort is not '':
            final_url.append('sort=%s' % sort)

        final_url.append('wt=json')

        return "&".join(final_url)

    def query(self, query, filter_query='', start=0, rows=10, sort=''):

        url = self.__build_url(query, filter_query, start, rows, sort)
        try:
            resp = requests.get(url)
        except requests.RequestException:
            return None

        return resp.json()