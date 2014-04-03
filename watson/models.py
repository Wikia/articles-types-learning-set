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
                                  url=data['url'])
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

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(Session, self).save(force_insert, force_update, using, update_fields)
        self.generate_session_article_set(int(self.pk))

    @staticmethod
    def __check_session(session_collection):
        if len(session_collection) == 0:
            return False

        cnt = SessionArticle.objects.filter(session_id=session_collection[0].id).count()
        if cnt > 0:
            print SessionArticle.objects.filter(session_id=session_collection[0].id).delete()

        return True

    def generate_session_article_set(self, session_id):
        session = Session.objects.filter(id=session_id)
        if self.__check_session(session) is False:
            return False

        session_size = session[0].size
        api_access = api.DocumentProvider(search.WikiaSearch())
        documents_col = api_access.generate_new_sample(session_size, session_id)

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


class ArticleType(models.Model):
    article = models.ForeignKey(ArticleData)
    user = models.ForeignKey(auth.User)
    changed = models.DateTimeField(auto_now=True)
    type = models.ForeignKey(Type, blank=True, null=True)

    def get_value(self):
        return self.type

    def set_value(self, value):
        if self.type == value:
            self.type = None
        else:
            self.type = value
        self.save()
        return self.type

class Quality(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class ArticleQuality(models.Model):
    article = models.ForeignKey(ArticleData)
    user = models.ForeignKey(auth.User)
    changed = models.DateTimeField(auto_now=True)
    quality = models.ForeignKey(Quality, blank=True, null=True)

    def get_value(self):
        return self.quality

    def set_value(self, value):
        if self.quality == value:
            self.quality = None
        else:
            self.quality = value
        self.save()
        return self.quality

class Kind(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name


class ArticleKind(models.Model):
    article = models.ForeignKey(ArticleData)
    user = models.ForeignKey(auth.User)
    changed = models.DateTimeField(auto_now=True)
    kind = models.ForeignKey(Kind, blank=True, null=True)

    def get_value(self):
        return self.kind

    def set_value(self, value):
        if self.kind == value:
            self.kind = None
        else:
            self.kind = value
        self.save()
        return self.kind
