from random import randint


class DocumentProvider(object):

    def __init__(self, wikia_solr):
        self.data = []
        self.wikia_solr = wikia_solr
        self.hub_filter = None
        self.article_quality_filter = None
        self.lang_filter = 'en'

    def set_article_quality_filter(self, quality):

        self.article_quality_filter = 'article_quality_i:%d' % quality

    def set_hub_filter(self, hub):
        if ',' in hub:
            hubs = ('hub:' + hub for hub in hub.split(','))
            self.hub_filter = "(" + " OR ".join(hubs) + ")"
        else:
            self.hub_filter = 'hub:'+hub

    def set_lang_filter(self, lang):
        self.lang_filter = lang

    def generate_new_sample(self, size=10, random=randint(1, 5000), exclude_hosts=[]):
        query = 'ns:0 AND lang:%s' % self.lang_filter
        sort = 'random_%d asc' % random
        filter_query = 'is_main_page:false'

        if len(exclude_hosts) > 0:
            for host in exclude_hosts:
                filter_query += " AND -(host:%s)" % host

        if self.article_quality_filter is not None:
            filter_query += " AND "+self.article_quality_filter

        if self.hub_filter is not None:
            filter_query += " AND "+self.hub_filter

        results = self.wikia_solr.query(query, filter_query, 0, size, sort)

        if results is not None:
            for result in results['response']['docs']:
                item = {
                    'wiki_id': result['wid'],
                    'page_id': result['pageid'],
                    'title': result['title_' + result['lang']],
                    'url': result['url'],
                    'article_quality': result['article_quality_i'] if 'article_quality_i' in result else 0,
                    'hub': result['hub']
                }
                self.data.append(item)

        return self.data