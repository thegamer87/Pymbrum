import httplib, urllib, json
from urlparse import urlparse
import datetime
import re

DATA_PROVIDER_URL =  "/servlet/SQLDataProviderServer"

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
HUMAN_TIME_FORMAT = "%Hh %Mm %Ss"

ROWS_FIELD = "rows"
ROWS_VALUE = "10"
START_ROW_FIELD = "startrow"
START_ROW_VALUE = "0"
COUNT_FIELD = "count"
COUNT_VALUE = "true"
SQL_CMD_FIELD = "sqlcmd"
SQL_CMD_VALUE = "rows:ushp_fgettimbrus"
PDATE_FIELD = "pDATE"

TIMBR_DAY_FIELD = "DAYSTAMP"
TIMBR_TIME_FIELD = "TIMETIMBR"
TIMBR_DIRECTION_FIELD = "DIRTIMBR"
TIMBR_CAUSE_FIELD = "CAUSETIMBR"
TIMBR_TYPE_FIELD = "TYPETIMBR"
TIMBR_IP_FIELD = "IPTIMBR"

minExitTime = datetime.timedelta(minutes=30)
dayWorkTime = datetime.timedelta(hours=7, minutes=12)

class Timbratura:
    VERSO_FIELD = "verso"
    VERSO_ENTRATA = "E"
    VERSO_USCITA  = "U"

    def __init__(self,day, time, direction, cause=None, type=None, ip=None):
        self.day = day
        self.time = time
        self.direction = direction
        self.cause = cause
        self.type = type
        self.ip=ip

def switchVerso(verso):
    if verso == Timbratura.VERSO_ENTRATA:
        return Timbratura.VERSO_USCITA
    elif verso == Timbratura.VERSO_USCITA:
        return Timbratura.VERSO_ENTRATA





def getTimbrature(cookie, url, date):
    parsedUrl = urlparse(url)
    host = parsedUrl.netloc
    path = parsedUrl.path+DATA_PROVIDER_URL

    if not date:
        date = datetime.date.today().strftime(DATE_FORMAT)

    params = urllib.urlencode({ROWS_FIELD:ROWS_VALUE, START_ROW_FIELD:START_ROW_VALUE, COUNT_FIELD:COUNT_VALUE, SQL_CMD_FIELD:SQL_CMD_VALUE, PDATE_FIELD:date})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Cookie":cookie}

    connection = httplib.HTTPSConnection(host)
    connection.request("POST", path, params, headers)

    response = connection.getresponse().read()

    responseDict = json.loads(response)

    headers = responseDict["Fields"]
    data = responseDict["Data"]


    timbrature = []
    versoActual = Timbratura.VERSO_ENTRATA
    for adata in data:
        if ("t" not in adata):
            day = None
            time = None
            dir = None
            cause = None
            type = None
            ip = None
            for index, d in enumerate(adata):
                if index < len(headers):
                    h = headers[index]
                    if h == TIMBR_DAY_FIELD:
                        day = d
                    if h == TIMBR_TIME_FIELD:
                        time = d
                    if h == TIMBR_DIRECTION_FIELD:
                        dir = d
                    if h == TIMBR_CAUSE_FIELD:
                        cause = d
                    if h == TIMBR_TYPE_FIELD:
                        type = d
                    if h == TIMBR_IP_FIELD:
                        ip = d
            timbratura = Timbratura(day, time, dir, cause, type, ip)
            if (timbratura.direction != versoActual):
                timbratura.direction = versoActual
            versoActual = switchVerso(versoActual)
            timbrature.append(timbratura)
    return timbrature

def getContatori(timbrature):
    totalWorkTime = None
    totalExitTime = None

    precTime = None
    precDir = None
    time = None
    precTime = None

    if (timbrature):
        for timbratura in timbrature:
            dir = timbratura.direction
            time = datetime.datetime.strptime(timbratura.time, TIME_FORMAT)
            print "DIR: ",dir," TIMBR: ",str(timbratura.time)
            if not precTime:
                precTime = time

            if dir == Timbratura.VERSO_USCITA:
                workedTime = time - precTime
                print "U timbr readed ... workedTime is: ",workedTime
                if (not totalWorkTime):
                    totalWorkTime = workedTime
                else:
                    totalWorkTime += workedTime
                print "totalWorkTime updated to ",totalWorkTime
            if dir == Timbratura.VERSO_ENTRATA:
                exitTime = time-precTime
                print "E timbr readed ... exitTime is: ",exitTime
                if (not totalExitTime):
                    totalExitTime = exitTime
                else:
                    totalExitTime += exitTime
                print "totalExitTime updated to ",totalExitTime
            precTime = time

        nowTime = datetime.datetime.now().time()
        nowDateTime = datetime.datetime(time.year, time.month, time.day, nowTime.hour, nowTime.minute, nowTime.second)
        workedTime = nowDateTime - time
        if dir == Timbratura.VERSO_ENTRATA:
            if (not totalWorkTime):
                totalWorkTime = workedTime
            else:
                totalWorkTime += workedTime
            print "last timbr readed is E ... totalWorkTime updated to ",totalWorkTime
        if totalExitTime and totalExitTime < minExitTime:
            totalWorkTime -= (minExitTime - totalExitTime)
            print "exitTime < minExitTime ... totalWorkTime updated to ",totalWorkTime

        print "final totalWorkTime is ",totalWorkTime
        print "final totalExitTime is ",totalExitTime

        timeToExit = dayWorkTime - totalWorkTime
        timeOfExit = nowDateTime + timeToExit

        workedPercent = round(totalWorkTime.total_seconds() / dayWorkTime.total_seconds() * 100)
        if workedPercent > 100:
            workedPercent = 100

        print "final work time percent is: ",workedPercent

        timeOfExitString = timeOfExit.strftime(TIME_FORMAT)
        if timeToExit.total_seconds() < 0:
            timeOfExitString = str(timeOfExit.time())+" ... che stracacchio di uno stracacchio ci fai ancora su quella sedia !!!"

        print "final timeOfExit is ",timeOfExit

        h,m,s = re.split(":",str(totalWorkTime))
        totalWorkTimeString = h+"h "+m+"m "+s+"s"

        h,m,s = re.split(":",str(totalExitTime))
        totalExitTimeString = h+"h "+m+"m "+s+"s"

        workedPercentString = str(workedPercent)


    else:
        totalWorkTimeString = "0h 0m 0s"
        totalExitTimeString = "0h 0m 0s"
        timeOfExitString = ""
        workedPercentString = "0"

        print "no timbr readed"
    return {"workedTime":totalWorkTimeString, "exitTime":totalExitTimeString, "timeOfExit":timeOfExitString, "workedPercent":workedPercentString}





