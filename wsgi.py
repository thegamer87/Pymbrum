from datetime import timedelta
from flask import Flask
import sys, logging

application = Flask(__name__)
sessionKey = "user"


logging.basicConfig(stream = sys.stderr)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.permanent_session_lifetime = timedelta(hours=1)
