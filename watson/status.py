from watson.models import State, Session, SessionArticle
from watson.metric import Metrics
from watson.watson_exceptions import NoSessionException, NoArticleForSessionExistsException, OutOfRangeException, SessionDoesNotExistsException


class Status():

    def __init__(self, user):
        self.metrics = None
        self.session_article = None
        state = State.objects.filter(user=user)
        if len(state) > 0:
            self.state = state[0]
        else:
            self.state = State(user=user)

    def set(self, session, number):
        session = self._get_session(session)
        number = self._get_number(session, number)
        self.state.number = self._validate_number(session, number)
        self.state.session = session
        self.state.save()
        self._load_metrics()
        self._load_article_data()

    def get_current(self):
        return self.metrics.get_current()

    def get_current_session_name(self):
        return self.state.session.name

    def get_current_number(self):
        return self.state.number

    def get_next(self):
        if self.state.session.size > self.state.number + 1:
            return self.state.number + 1
        return 0

    def set_metric(self, metric, value):
        return self.metrics.toggle(metric, value)

    def get_url(self):
        return self._get_session_article().article.url

    def _load_metrics(self):
        self.metrics = Metrics(self._get_session_article(), self.state.user)

    def _get_number(self, session, number):
        if not number:
            if hasattr(self.state, 'session') and self.state.session == session and self.state.number is not None:
                return self.state.number

        return int(max(number, 0))

    def _get_session(self, session):
        if session is None:
            if self.state.session_id is not None:
                return self.state.session
            else:
                sessions = Session.objects.all()[:1]
                if sessions:
                    return sessions[0]
                raise NoSessionException()
        else:
            obj = self._load_session(session)
            if obj:
                return obj
        raise SessionDoesNotExistsException(session)

    def _get_session_article(self):
        try:
            if self.session_article is None:
                self.session_article = SessionArticle.objects.get(session=self.state.session, number=self.state.number)
        except SessionArticle.DoesNotExist:
            raise NoArticleForSessionExistsException(self.state.session.name)
        return self.session_article

    def _load_article_data(self):
        session_article = self._get_session_article()
        if not session_article.article.wikitext or not session_article.article.html:
            session_article.article.update()

    @staticmethod
    def _load_session(name):
        sessions = Session.objects.filter(name=name)
        return sessions[0] if len(sessions) > 0 else False

    @staticmethod
    def _validate_number(session, number):
        if 0 <= number < session.size:
            return number
        size = session.size - 1
        raise OutOfRangeException(size)