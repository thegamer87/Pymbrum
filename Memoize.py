import datetime

class Memoize:
    def __init__(self, f):
        self.f = f
        self.memo = {}
        self.callTime = {}

    def __call__(self, *args):
        callTime = datetime.datetime.today()
        print "CALL TIME IS: ",callTime
        if not args in self.memo:
            print "NEW ARGS ... MAKE REAL CALL"
            self.memo[args] = self.f(*args)
            self.callTime[args] = callTime
        else:
            precCallTime = self.callTime[args]
            delta = callTime-precCallTime
            delta = delta.total_seconds()
            if delta > 60:
                print "OLD ARGS BUT TIME LIMIT REACHED ... MAKE REAL CALL"
                self.memo[args] = self.f(*args)
                self.callTime[args] = callTime
            else:
                print "RETURN CACHED"
        return self.memo[args]

