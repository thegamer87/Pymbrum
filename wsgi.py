from datetime import timedelta
import sys, logging

from Pymbrum import app as application

logging.basicConfig(stream = sys.stderr)
application.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
application.permanent_session_lifetime = timedelta(hours=1)
