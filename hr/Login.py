import httplib, urllib
from urlparse import urlparse



USERNAME_FIELD = "m_cUserName"
PASSWORD_FIELD = "m_cPassword"
ACTION_FIELD = "m_cAction"
ACTION_VALUE = "login"

LOGIN_URL = "/servlet/cp_login"
SUCCESS_REDIRECT_URL = "/jsp/home.jsp"

class LoginResult:
    def __init__(self, result, message, cookie=None):
        self.result = result
        self.message = message
        self.cookie = cookie

def login (url, username, password):
    parsedUrl = urlparse(url)
    host = parsedUrl.netloc
    path = parsedUrl.path+LOGIN_URL

    params = urllib.urlencode({USERNAME_FIELD:username, PASSWORD_FIELD:password, ACTION_FIELD:ACTION_VALUE})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    connection = httplib.HTTPSConnection(host)
    connection.request("POST", path, params, headers)

    response = connection.getresponse()

    if response.status == 302:
        redirectLocation = response.getheader("Location")
        setCookie = response.getheader("Set-Cookie")
        if redirectLocation and redirectLocation.endswith(SUCCESS_REDIRECT_URL):
            loginResult = LoginResult(True,"Login avvenuto con successo", setCookie)
    else:
            message = response.getheader("JSURL-Message")
            if message:
                loginResult = LoginResult(False,"Login fallito: "+message)
    return loginResult





