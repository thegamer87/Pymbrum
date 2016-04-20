import telepot
from wsgi import app

@app.route('/thebot/test', methods=['POST','GET'])
def the_bot_test():
	bot = telepot.Bot('120630437:AAF9Qo-mJQWQAQCmpOpLbPuNHFvVG-9Ep0U')
	return bot.getMe()
