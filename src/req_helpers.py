__fname = 'req_helpers'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
cStrDivider_1 = '#----------------------------------------------------------------#'
print('', cStrDivider, f'GO _ {__filename} -> starting IMPORTs & declaring globals', cStrDivider, sep='\n')

#=====================================================#
#         imports                                     #
#=====================================================#
from constants import *
from flask import Response
import json
from re import match


#=====================================================#
#         request handler json response parsers       #
#=====================================================#
def JSONResponse(dict):
    return Response(json.dumps(dict), mimetype="application/json" )

def prepJsonResponseValidParams(keyVals, validParams0=True, validParams1=True, validParams2=True, validParams3=True, tprint=False, errMsg=None):
    funcname = f'{__filename} prepJsonResponseValidParams'
    print(funcname + ' - ENTER')

    keyVals = 'nil_keyVals' if keyVals == None or len(keyVals) < 1 else keyVals
    bErr = False
    if not validParams0 or not validParams1 or not validParams2 or not validParams3:
        if not errMsg: errMsg = kErrArgs
        err_resp_args = {'ERROR':vErrArgs, 'MSG':errMsg, 'PAYLOAD':{'error':errMsg,'keyVals':keyVals}}
        if tprint:
            print(funcname, f'return error: {errMsg}', f'payloaddict: {err_resp_args}\n')
        else:
            print(funcname, f'return error: {errMsg}', 'payloaddict: <print disabled>\n')
        bErr = True
        return bErr, JSONResponse(err_resp_args)

    return bErr, JSONResponse({'ERROR':vErrNone})

def prepJsonResponseDbProcErr(dbProcResult, tprint=False, errMsg=None):
    funcname = f'{__filename} prepJsonResponseDbProcErr'
    print(funcname + ' - ENTER')

    bErr = False
    #logalert(funcname, f'dbProcResult: {dbProcResult}\n\n', simpleprint=True)
    if dbProcResult == -1 or (dbProcResult != -1 and errMsg): # validate db errors #
        if not errMsg: errMsg = kErrDb
        dbProcResult = get_datetime_parse_list(dbProcResult)
        err_resp_db = {'ERROR':vErrDb, 'MSG':errMsg, 'PAYLOAD':{'error':errMsg, 'dbProcResult':dbProcResult}}
        if tprint:
            print(funcname, f'return error: {errMsg}', f'payloaddict: {err_resp_db}\n')
        else:
            print(funcname, f'return error: {errMsg}', 'payloaddict: <print disabled>\n')
        bErr = True
        return bErr, JSONResponse (err_resp_db)

    return bErr, JSONResponse({'ERROR':vErrNone})

def prepJsonResponseDbProc(arrStrReturnKeys, dbProcResult, strRespSuccessMSG, tprint=False):
    funcname = f'{__filename} prepJsonResponseDbProc'
    print(funcname + ' - ENTER')
    #l = []
    #l.append({arrStrReturnKeys:dbProcResult}) # append this json return list entry #
    l = []
    for row in dbProcResult:
        jsonRow = getJsonDictFromDBQueryRowWithKeys(row, arrStrReturnKeys)
        l.append (jsonRow) # append this json return list entry #

    payloaddict = {'error':vErrNone,'result_arr':l,'auth_token':"TODO ; )"}

    if tprint:
        print(funcname, f'return error: {vErrNone}', '\npayloaddict: %s\n' % payloaddict)
    else:
        print(funcname, f'return error: {vErrNone}', 'payloaddict: <print disabled>\n')

    return JSONResponse ({'ERROR':vErrNone,'MSG':strRespSuccessMSG,'PAYLOAD':payloaddict})

def get_datetime_parse_list(_dbProcResult):
    l = []
    for row in _dbProcResult:
        jsonRow = getJsonDictFromDBQueryRowWithKeys(row, list(row.keys()), True) # True = _ALL
        l.append (jsonRow) # append this json return list entry #
        # NOTE: getJsonDictFromDBQueryRowWithKeys required for datetime parsing
    return l
            
def prepJsonResponseDbProc_ALL(arrStrReturnKeys, dbProcResult, strRespSuccessMSG, tprint=False):
    funcname = f'{__filename} prepJsonResponseDbProc_ALL'
    print(funcname + ' - ENTER')
    #l = []
    #l.append({arrStrReturnKeys:dbProcResult}) # append this json return list entry #
    l = []
    l = get_datetime_parse_list(dbProcResult)

    payloaddict = {'error':vErrNone,'result_arr':l,'auth_token':"TODO ; )"}

    if tprint:
        print(funcname, f'return error: {vErrNone}', '\npayloaddict: %s\n' % payloaddict)
    else:
        print(funcname, f'return error: {vErrNone}', 'payloaddict: <print disabled>\n')

    return JSONResponse ({'ERROR':vErrNone,'MSG':strRespSuccessMSG,'PAYLOAD':payloaddict})

## parse database query row into json dict ##
# @descr: parses a database query row, into a json
# @expects: db query row dictionary and keys to parse
# @requires: row, keys
# @returns: dictionary with db query string return as a json
def getJsonDictFromDBQueryRowWithKeys(row, keys, _ALL=False):
    funcname = f'<{__filename}> getJsonDictFromDBQueryRowWithKeys'
    #logenter(funcname, simpleprint=False, tprint=False)

    jsonDict = {}
    for key in keys:
        #loginfo(funcname, '\n\n key: %s\n\n' % key, '')
        if key not in row and not _ALL:
            #loginfo(funcname, '\n\n key: %s NOT IN row: %s\n\n' % (key, row), '')
            continue

        if match('dt_*', key) is not None:
            try:
                #convert dt to seconds since 1970
                # note: needed because JSONResponse() parsing issues
                jsonDict[key] = jsonTimestampFromDBQueryTimestamp(row[key])

            except Exception as e:
                print(funcname, "\n\n!EXCEPTION HIT!\n\n e: '%s';\n\n in 'jsonDict[key] = jsonTimestampFromDBQueryTimestamp(row[key])'\n\n" % e, " falling back to 'jsonDict[key] = row[key]' instead")
                jsonDict[key] = row[key]
        else:
            jsonDict[key] = row[key]

    #loginfo(funcname, '\njsonDict: %s\n' % jsonDict, '')
    return jsonDict

## gets json compatible timestamp from db query timestamp ##
def jsonTimestampFromDBQueryTimestamp(timestamp):
    if timestamp == None:
        return None
    
    # NOTE_070522:
    #   new solution, return UTC epoch time as is
    #    and convert to local on client side
    #   use: "var localDate = epochDate.toLocaleString("en-US", {timeZone: "America/New_York"})"
    return int(timestamp.strftime("%s"))
    
    # NOTE: code %s means seconds,
    #   ref: http://strftime.org/
    #return int(timestamp.strftime("%s"))
    #return int(timestamp.strftime("%s")) + 14400 #EDT
    #return int(timestamp.strftime("%s")) + 18000 #EST
       #NOTE: convert from UTC to EDT
       #  using +4hrs, instead of -4hrs, since datetime lib thinks we are converting UTC to sec;
       #  but we are actually converting local unix to sec
       #NOTE_2: 4hr diff is also EDT, not EST (this may cause issue when daylight savings time ends)
    
print(__filename, f"\n CLASSES & FUNCTIONS initialized:- STARTING -> additional '{__filename}' run scripts (if applicable) . . .")
print(__filename, f"\n  DONE Executing additional '{__filename}' run scripts ...")
print('#======================================================================#')
