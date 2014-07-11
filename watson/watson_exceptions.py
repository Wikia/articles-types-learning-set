class WatsonException(Exception):
    def __init__(self):
        Exception.__init__(self)

    def __unicode__(self):
        return "General Watson exception"


class NoSessionException(WatsonException):
    def __unicode__(self):
        return "No session exists"


class SessionDoesNotExistsException(WatsonException):
    def __init__(self, session):
        self.session = session
        WatsonException.__init__(self)

    def __unicode__(self):
        return "Session with %s name does not exists" % self.session


class NoArticleForSessionExistsException(WatsonException):
    def __init__(self, session):
        self.session = session
        WatsonException.__init__(self)

    def __unicode__(self):
        return "Given article was not found for %s session" % self.session


class OutOfRangeException(WatsonException):
    def __init__(self, size):
        self.size = size
        WatsonException.__init__(self)

    def __unicode__(self):
        return "Number out of range (current range: 0 to %d)" % self.size
