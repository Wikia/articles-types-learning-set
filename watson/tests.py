import os
import time
from django.test import TestCase
from django.contrib.auth import models as auth
from watson import models
from watson.generator import Generator
from watson.metric import Metrics


# Create your tests here.
class TestGenerator(TestCase):
    def setUp(self):
        helper = TestsHelper()
        self.session_a_name = "UnitTest_a_%d" % time.time()
        self.session_a = helper.set_up_session_data(self.session_a_name, 0)
        self.session_b_name = "UnitTest_b_%d" % time.time()
        self.session_b = helper.set_up_session_data(self.session_b_name, 1)

        self.generator = Generator(self.session_a_name)

    def _get_data(self, article):
        return {
            "_id": str(article),
            "wikiId": article.wiki_id,
            "pageId": article.page_id,
            "title": article.title,
            "wikiText": article.wikitext,
        }

    def test_no_metric_set(self):
        article_session = models.SessionArticle.objects.filter(session=self.session_a)
        expected = [self._get_data(article_session[0].article),
                    self._get_data(article_session[1].article)]

        self.assertEqual(self.generator.run(), expected)

    def test_run_type_only(self):
        self.generator.set_metric('type')

        article_session = models.SessionArticle.objects.filter(session=self.session_a)
        expected = [self._get_data(article_session[0].article),
                    self._get_data(article_session[1].article)]
        expected[0]['type'] = 'Person'
        expected[1]['type'] = 'Location'

        self.assertEqual(self.generator.run(), expected)

    def test_limit(self):
        self.generator.set_metric('type')
        self.generator.set_limit(1)

        article_session = models.SessionArticle.objects.filter(session=self.session_a)
        expected = [self._get_data(article_session[0].article)]
        expected[0]['type'] = 'Person'

        self.assertEqual(self.generator.run(), expected)

        self.generator.set_limit(0)
        self.assertEqual(self.generator.run(), [])

    def test_run_two_metrics(self):
        self.generator.set_metric('type')
        self.generator.set_metric('quality')

        article_session = models.SessionArticle.objects.filter(session=self.session_a)
        expected = [self._get_data(article_session[0].article)]
        expected[0]['type'] = 'Person'
        expected[0]['quality'] = 'great'

        self.assertEqual(self.generator.run(), expected)

    def test_more_then_two_users(self):
        self.generator.set_metric('type')
        self.generator.set_lower_bound(3)

        self.assertEqual(self.generator.run(), [])

    def test_quality_filter(self):
        self.generator.set_session(session=self.session_b_name)
        self.generator.set_metric('type')
        article_session = models.SessionArticle.objects.filter(session=self.session_b)
        quality = article_session[0].article.article_quality
        self.generator.set_quality_filter(quality + 1)

        self.assertEqual(self.generator.run(), [])

        expected = [self._get_data(article_session[0].article)]
        expected[0]['type'] = 'Person'

        self.generator.set_quality_filter(quality)
        self.assertEqual(self.generator.run(), expected)

    def test_hub_filter(self):
        self.generator.set_session(session=self.session_b_name)
        self.generator.set_metric('type')

        article_session = models.SessionArticle.objects.filter(session=self.session_b)
        hub = article_session[0].article.hub
        expected = [self._get_data(article_session[0].article)]
        expected[0]['type'] = 'Person'

        self.generator.set_hub_filter('NonExistingHub')
        self.assertEqual(self.generator.run(), [])

        self.generator.set_hub_filter(hub)
        self.assertEqual(self.generator.run(), expected)


class TestsHelper():
    imported = False

    def set_up_session_data(self, name, set_number):
        self._import_types()
        session = models.Session(name=name, size=2)
        session.save()
        self._add_data(session, set_number)
        return session

    def _add_data(self, session, set_number):
        users = self._get_users(['test_user_a', 'test_user_b', 'test_user_c'])

        if set_number == 0:
            session_articles_a = models.SessionArticle.objects.filter(session=session)
            self._add_metric(users[0], session_articles_a[0].article, {'type': 'Person', 'quality': 'great'})
            self._add_metric(users[1], session_articles_a[0].article, {'type': 'Location', 'quality': 'aspiring'})
            self._add_metric(users[2], session_articles_a[0].article, {'type': 'Person', 'quality': 'great'})
            self._add_metric(users[0], session_articles_a[1].article, {'type': 'Location'})
            self._add_metric(users[1], session_articles_a[1].article, {'type': 'Location'})
            self._add_metric(users[2], session_articles_a[1].article, {'type': 'Fictional character'})

        if set_number == 1:
            session_articles_b = models.SessionArticle.objects.filter(session=session)
            self._add_metric(users[0], session_articles_b[0].article, {'type': 'Person', 'quality': 'great'})
            self._add_metric(users[1], session_articles_b[0].article, {'type': 'Person', 'quality': 'great'})

    def _import_types(self):
        if not self.imported:
            self.imported = Metrics.import_from_file("%s/../watson_types.csv" % os.path.dirname(__file__))

    @staticmethod
    def _add_metric(user, article, metrics):
        metric = models.ArticleMetrics(
            article=article,
            user=user
        )
        for key, value in metrics.items():
            setattr(metric, key, getattr(models, key.capitalize()).objects.get(name=value))
        metric.save()

    @staticmethod
    def _get_users(users):
        db_users = auth.User.objects.all()
        if not db_users:
            db_users = []
            for user in users:
                db_user = auth.User(username=user)
                db_user.save()
                db_users.append(db_user)
        return db_users