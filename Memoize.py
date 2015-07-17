import datetime

class Memoize:
    def __init__(self, f):
        self.f = f
        self.cache = {}
        self.callTime = {}

    def __call__(self, *args):
        cookie, url, surname = args
        if surname:
            surname = surname.upper(surname)
        keyArgs = (url,surname)
        callTime = datetime.datetime.today()

        if not keyArgs in self.cache:
            print "NEW ARGS ... MAKE REAL CALL"
            self.cache[keyArgs] = self.f(*args)
            self.callTime[keyArgs] = callTime
        else:
            precCallTime = self.callTime[keyArgs]
            delta = (callTime-precCallTime).total_seconds()
            if delta > 1800:
                print "OLD ARGS BUT TIME LIMIT REACHED ... MAKE REAL CALL"
                self.cache[keyArgs] = self.f(*args)
                self.callTime[keyArgs] = callTime
            else:
                print "RETURN CACHED"
        return self.cache[keyArgs]

