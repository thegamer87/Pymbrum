import json
import datetime
from datetime import timedelta
import Cookie

from flask import Flask
from flask import request
from flask import session
from flask import render_template


from hr import Login
from hr import TimeManager
from hr import PhoneManager

import telepot

app = Flask(__name__)
sessionKey = "user"

class UserSession:
	def __init__(self, username=None, host=None, cookie=None, date=None, surname=None):
		self.username = username
		self.host = host
		self.cookie = cookie
		self.date = date
		self.surname = surname

	def from_JSON(self,j):
		obj = json.loads(j)
		self.username = obj["username"]
		self.host = obj["host"]
		self.cookie = obj["cookie"]
		return self

	def to_JSON(self):
		return json.dumps(self.__dict__)

@app.route('/rubrica', methods=['POST','GET'])
def rubrica():
	if sessionKey not in session:
		return render_template("pymbrum.html")
	userSession = UserSession().from_JSON(session[sessionKey])
	url = userSession.host
	surname = None
	if request.method == 'POST' and "surname" in request.form:
		surname = request.form["surname"]

	rubrica = PhoneManager.getRubrica(userSession.cookie, url, surname)
	if rubrica == False:
		return render_template("pymbrum.html", action="login", message="Sessione HR scaduta")

	rubricaHeaders = ["NOMINATIVO", "UFFICIO", "TELEFONO", "CELLULARE", "EMAIL", "PREFISSO", "PRESENZA"]
	rubricaTemplate = []

	for entry in rubrica:
		entryTemplate = [entry.surname, entry.code, entry.phone, entry.mobile, entry.email, entry.prefix, entry.presence]
		rubricaTemplate.append(entryTemplate)
		print entryTemplate

	return render_template("pymbrum.html", action="phonebook", headers=rubricaHeaders, rubrica=rubricaTemplate, surname=surname)


@app.route('/timbrature', methods=['POST','GET'])
def timbrature():
	todayDate = datetime.datetime.today().strftime(TimeManager.DATE_FORMAT)
	if sessionKey not in session:
		return render_template("pymbrum.html")
	userSession = UserSession().from_JSON(session[sessionKey])
	url = userSession.host
	date = None
	if request.method == 'POST' and "date" in request.form:
		date = request.form["date"]
	if not date or date == "":
		date = todayDate

	isToday = (date == todayDate)

	timbrature = TimeManager.getTimbrature(userSession.cookie, url,date)
	if (timbrature == False):
		return render_template("pymbrum.html", action="login", message="Sessione HR scaduta")

	contatori = TimeManager.getContatori(url, timbrature)

	templateHeaders = ["ORA","VERSO"]
	templateTimbrature = []
	for timbratura in timbrature:
		templTimbr = [timbratura.time, timbratura.direction]
		templateTimbrature.append(templTimbr)

	print "DATE: ",date
	return render_template("pymbrum.html", action="time", headers=templateHeaders, timbrature=templateTimbrature,
						   contatori=contatori, dataTimbrature=date, isToday=isToday)


@app.route("/")
def main():
	if sessionKey in session:
		return timbrature()
	else:
		return render_template("pymbrum.html", message=None)

@app.route('/login', methods=['POST'])
def login():
	if sessionKey in session:
		return render_template("pymbrum.html", action="time", dataTimbrature=datetime.datetime.today().strftime(TimeManager.DATE_FORMAT))
	url = request.form["url"]
	username = request.form["username"]
	password = request.form["password"]
	loginresult = Login.login(url, username, password)

	if loginresult.result:
		loginCookie = Cookie.SimpleCookie().load(loginresult.cookie)
		print "LOGIN COOKIE: ", loginCookie
		userSession = UserSession(username, url, loginresult.cookie)
		session[sessionKey] = userSession.to_JSON()
		session.permanent = True
		return timbrature()
	else:
		return render_template("pymbrum.html", action="login", message=loginresult.message)

@app.route('/logout')
def logout():
	session.pop(sessionKey, None)
	return render_template("pymbrum.html")


@app.route('/thebot/test', methods=['POST','GET'])
def the_bot_test():
	bot = telepot.Bot('120630437:AAF9Qo-mJQWQAQCmpOpLbPuNHFvVG-9Ep0U')
	return bot.getMe()


if __name__ == '__main__':
	app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.permanent_session_lifetime = timedelta(hours=1)
app.run()