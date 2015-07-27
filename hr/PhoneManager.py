import httplib, urllib, json
from urlparse import urlparse
import csv
import StringIO
from Memoize import Memoize

DATA_PROVIDER_URL =  "/servlet/SQLDataProviderServer"
REPORT_PROVIDER_URL = "/servlet/Report"
REPORT_PARAMS = "ReportName=AAA_ElencoPresenti&m_cWv=Rows%3D0%0A0%5Cu0023m_cMode%3Dhyperlink%0A0%5Cu0023outputFormat%3DCSV%0A0%5Cu0023pageFormat%3DA4%0A0%5Cu0023rotation%3DPORTRAIT%0A0%5Cu0023marginTop%3D7%0A0%5Cu0023marginBottom%3D7%0A0%5Cu0023marginLeft%3D7%0A0%5Cu0023hideOptionPanel%3DT%0A0%5Cu0023showAfterCreate%3DTrue%0A0%5Cu0023mode%3DDOWNLOAD%0A0%5Cu0023ANQUERYFILTER%3D1%0A0%5Cu0023pRAPPORTO%3D%0A0%5Cu0023pFILIALE%3D%0A0%5Cu0023pUFFICIO%3D%0A0%5Cu0023m_cParameterSequence%3Dm_cMode%2CoutputFormat%2CpageFormat%2Crotation%2CmarginTop%2CmarginBottom%2CmarginLeft%2Cmode%2ChideOptionPanel%2CshowAfterCreate%2CANQUERYFILTER%2CpRAPPORTO%2CpFILIALE%2CpUFFICIO%0A"

REPORT_PRESENCE_NAME_FIELD = "AAA_ElencoPresenti.c_Cognome_Nome"
REPORT_PRESENCE_FIELD = "AAA_ElencoPresenti.c_Presente"

ROWS_FIELD = "rows"
ROWS_VALUE = "5"
START_ROW_FIELD = "startrow"
START_ROW_VALUE = "0"
COUNT_FIELD = "count"
COUNT_VALUE = "true"
SQL_CMD_FIELD = "sqlcmd"
SQL_CMD_VALUE = "q_rubrica"
ORDERBY_FIELD = "orderby"
ORDERBY_VALUE = "ANSURNAM desc"
FILTER_FIELD = "queryfilter"
FILTER_VALUE_START = "ANSURNAM like "
PANSURNAM_FIELD = "pANSURNAM"


RUBR_SURNAME_FIELD = "ANSURNAM"
RUBR_CODE_FIELD = "CODE"
RUBR_PHONE_FIELD = "ANTELEF"
RUBR_MOBILE_FIELD = "ANMOBILTEL"
RUBR_EMAIL_FIELD = "ANEMAIL"
RUBR_PREFIX_FIELD = "ANPREFIX"

class EntryRubrica:
    def __init__(self, surname, code, phone, mobile, email, prefix, presence):
        self.surname = surname
        self.code = code
        self.phone = phone
        self.mobile = mobile
        self.email = email
        self.prefix = prefix
        self.presence = presence

def getRubrica(cookie, url, surname):
    parsedUrl = urlparse(url)
    host = parsedUrl.netloc
    path = parsedUrl.path+DATA_PROVIDER_URL

    paramsDict = {ROWS_FIELD:ROWS_VALUE, START_ROW_FIELD:START_ROW_VALUE, COUNT_FIELD:COUNT_VALUE, SQL_CMD_FIELD:SQL_CMD_VALUE, ORDERBY_FIELD:ORDERBY_VALUE, PANSURNAM_FIELD:""}
    if surname:
        paramsDict.update({FILTER_FIELD:FILTER_VALUE_START+"'"+surname.upper()+"'"})

    params = urllib.urlencode(paramsDict)
    params=params.replace("+","%20")

    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Cookie":cookie}

    connection = httplib.HTTPSConnection(host)
    connection.request("POST", path, params, headers)

    response = connection.getresponse()

    responseStatus = response.status

    responseData = response.read()

    responseDict = json.loads(responseData)

    rubricaHeaders = responseDict["Fields"]
    rubricaData = responseDict["Data"]

    #Hack: get presenze
    path = parsedUrl.path+REPORT_PROVIDER_URL
    print path

    params = REPORT_PARAMS
    print params

    connection.request("POST", path, params, headers)
    response = connection.getresponse().read()


    csvFile = StringIO.StringIO(response)
    csvReader = csv.reader(csvFile, delimiter=",")

    nameIndex = None
    presenceIndex = None
    presenceDict = {}
    for index,csvRow in enumerate(csvReader):
        print "INDEX: ",index
        print "CSVROW: ",csvRow
        if index == 0:
            csvHeader = csvRow[0].split(";")
            for i,field in enumerate(csvHeader):
                if field == REPORT_PRESENCE_NAME_FIELD:
                    nameIndex = i
                if field == REPORT_PRESENCE_FIELD:
                    presenceIndex = i
        else:
            csvData = csvRow[0].split(";")
            presenceDict.update({csvData[nameIndex]:csvData[presenceIndex]})

    print "PRESENCE DICT"
    print presenceDict


    rubrica = []
    for adata in rubricaData:
        if ("t" not in adata):
            surname = None
            code = None
            phone = None
            mobile = None
            email = None
            prefix = None
            presence = None

            for index,d in enumerate(adata):
                if index < len(rubricaHeaders):
                    h = rubricaHeaders[index]
                    if h == RUBR_SURNAME_FIELD:
                        surname = d
                    if h == RUBR_CODE_FIELD:
                        code = d
                    if h == RUBR_PHONE_FIELD:
                        if "." in d:
                            d = d.split(".")[1]
                        phone = d
                    if h == RUBR_MOBILE_FIELD:
                        mobile = d
                    if h == RUBR_EMAIL_FIELD:
                        email = d
                    if h == RUBR_PREFIX_FIELD:
                        prefix = d
            dictSurname = surname.replace(",","")
            if dictSurname in presenceDict:
                presence = presenceDict[dictSurname]
                print "PRESENCE FOR ",dictSurname+" IS "+presence


            entryRubrica = EntryRubrica(surname, code, phone, mobile, email, prefix, presence)
            rubrica.append(entryRubrica)
    return rubrica

getRubrica = Memoize(getRubrica)
