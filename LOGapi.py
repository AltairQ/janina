import datetime 

JS_LOGFILE = open("js.log", "a")


def js_log(text):
	now = datetime.datetime.now()
	timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
	JS_LOGFILE.write("[js " + timestamp + " ] "+text+"\n")
