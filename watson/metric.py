import csv
import re
from watson import models


class Metrics():

    prep = re.compile(r'_([a-z])')

    def __init__(self, session_article, user):
        self.article_metrics = (models.ArticleMetrics.objects.filter(article=session_article.article, user=user).first() or
                                models.ArticleMetrics(article=session_article.article, user=user))

    def get_current(self):
        return self.article_metrics

    def toggle(self, metric, value):
        model = self._get_model(metric, value)
        if getattr(self.article_metrics, metric) == model:
            model = None
        setattr(self.article_metrics, metric, model)
        self.article_metrics.save()
        return model

    @staticmethod
    def import_from_file(file):
        output = []
        with open(file, 'r') as csv_file:
            file_reader = csv.reader(csv_file)
            for line in file_reader:
                model = getattr(models, line[0])
                if not model.objects.filter(name=line[2]):
                    new = model()
                    if line[1]:
                        setattr(new, 'category', line[1])
                    setattr(new, 'name', line[2])
                    output.append(str(new))
                    new.save()
        return output

    @staticmethod
    def _get_model(metric, value):
        camel_cased = Metrics.prep.sub(lambda x: x.group(1).upper(), metric.capitalize())
        return getattr(models, camel_cased).objects.get(name=value)