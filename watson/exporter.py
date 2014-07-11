import csv
from watson.models import ArticleMetrics, SessionArticle, Session


class Exporter():

    file_name = 'metrics_export.csv'

    def __init__(self, session=None):
        self.session_name = session

    def run(self):
        session_articles = SessionArticle.objects.all() \
            if self.session_name is None else SessionArticle.objects.filter(session=self._get_session())

        with open(self.file_name, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(["url", "session", "AQ", "user", "quality", "mobile quality", "type", "kind"])
            for session_article in session_articles:
                metrics = ArticleMetrics.objects.filter(article=session_article.article)
                for metric in metrics:
                    writer.writerow([session_article.article.url,
                                    session_article.session.name,
                                    session_article.article.article_quality,
                                    metric.user,
                                    metric.quality,
                                    metric.mobile_quality,
                                    metric.type,
                                    metric.kind])

    def _get_session(self):
        return Session.objects.filter(name=self.session_name)[0]