import requests
from django.db import models
from django.contrib.auth import models as auth
from concurrent.futures import ThreadPoolExecutor
from wikia import api, search


class ArticleData(models.Model):
    wiki_id = models.IntegerField()
    page_id = models.IntegerField()
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    wikitext = models.TextField()
    html = models.TextField()
    article_quality = models.IntegerField(blank=True, null=True)
    hub = models.CharField(max_length=255, blank=True, null=True)

    def get_data(self):
        wtr = requests.get(self.url + '?action=raw')
        if wtr.status_code == 200:
            self.wikitext = wtr.text
        hr = requests.get(self.url + '?action=render')
        if hr.status_code == 200:
            self.html = hr.text
        self.save()

    def update(self):
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(self.get_data())

    @staticmethod
    def create_from_data(data):
        articles = ArticleData.objects.filter(page_id=data['page_id'], wiki_id=data['wiki_id'])
        if len(articles) == 0:
            article = ArticleData(wiki_id=data['wiki_id'],
                                  page_id=data['page_id'],
                                  title=data['title'],
                                  url=data['url'],
                                  article_quality=data['article_quality'],
                                  hub=data['hub'])
            article.save()
            return article
        else:
            return articles[0]

    def __unicode__(self):
        return "%d_%d" % (int(self.wiki_id), int(self.page_id))


class Session(models.Model):
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    size = models.IntegerField()
    article_quality_filter = models.IntegerField(blank=True, null=True)
    hub_filter = models.CharField(max_length=255, blank=True, null=True)
    lang_filter = models.CharField(max_length=2, blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(Session, self).save(force_insert, force_update, using, update_fields)
        self.generate_session_article_set(int(self.pk))

    @staticmethod
    def _check_session(session_collection):
        if len(session_collection) == 0:
            return False

        cnt = SessionArticle.objects.filter(session_id=session_collection[0].id).count()
        if cnt > 0:
            SessionArticle.objects.filter(session_id=session_collection[0].id).delete()

        return True

    def generate_session_article_set(self, session_id):
        session = Session.objects.filter(id=session_id)
        if self._check_session(session) is False:
            return False

        session_size = session[0].size
        api_access = api.DocumentProvider(search.WikiaSearch())

        if bool(session[0].hub_filter) is not False:
            api_access.set_hub_filter(session[0].hub_filter)
        if bool(session[0].article_quality_filter) is not False:
            api_access.set_article_quality_filter(session[0].article_quality_filter)
        if bool(session[0].lang_filter) is not False:
            api_access.set_lang_filter(session[0].lang_filter)

        host_list = []
        for host in ExcludedWikis.objects.all():
            host_list.append(host)

        documents_col = api_access.generate_new_sample(session_size, session_id, host_list)

        num = 0
        for doc in documents_col:
            article_model = ArticleData.create_from_data(doc)
            SessionArticle.save_article_to_session(session_id, num, article_model.id)
            num += 1


class State(models.Model):
    session = models.ForeignKey(Session)
    user = models.ForeignKey(auth.User)
    number = models.IntegerField()


class SessionArticle(models.Model):
    session = models.ForeignKey(Session)
    article = models.ForeignKey(ArticleData)
    number = models.IntegerField()

    @staticmethod
    def save_article_to_session(session_id, number, article_id):
        ats_model = SessionArticle(session_id=session_id,
                                   article_id=article_id,
                                   number=number)
        ats_model.save()


class Type(models.Model):
    category = models.CharField(max_length=50)
    name = models.CharField(max_length=100)

    @staticmethod
    def get_in_categories():
        categories = {}
        for type in Type.objects.all():
            if type.category not in categories.keys():
                categories[str(type.category)] = []
            categories[type.category].append(str(type.name))
        return categories

    def __unicode__(self):
        return "%s:%s" % (self.category, self.name)


class Quality(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class Kind(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class MobileQuality(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class ArticleMetrics(models.Model):
    article = models.ForeignKey(ArticleData)
    user = models.ForeignKey(auth.User)
    changed = models.DateTimeField(auto_now=True)
    type = models.ForeignKey(Type, blank=True, null=True)
    quality = models.ForeignKey(Quality, blank=True, null=True)
    kind = models.ForeignKey(Kind, blank=True, null=True)
    mobile_quality = models.ForeignKey(MobileQuality, blank=True, null=True)

    def __unicode__(self):
        return "%s: %s (%s, %s, %s, %s)" % \
               (self.user, self.article, str(self.type), str(self.quality), str(self.kind), str(self.mobile_quality))


class ExcludedWikis(models.Model):
    host = models.CharField(max_length=100)

    def __unicode__(self):
        return self.host