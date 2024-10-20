__fname = 'req_handler'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
cStrDivider_1 = '#----------------------------------------------------------------#'
print('', cStrDivider, f'GO _ {__filename} -> starting IMPORTs & declaring globals', cStrDivider, sep='\n')

#=====================================================#
#         imports                                     #
#=====================================================#
from _env import env
from db_controller import *
from req_helpers import *
import json#, time
# from datetime import datetime

#=====================================================#
#         global static keys                          #
#=====================================================#
kPin = 'admin_pin'
# kUserId = "user_id"
# kKeyVals = "key_vals"

VERBOSE_LOG = False

#=====================================================#
#         TG cmd / request handler static keys        #
#=====================================================#
#-----------------------------------------------------#
# SOWL _  'Edit Commands' (TG: @BotFather)
#-----------------------------------------------------#
# start - show help info
# help - show help info
# gen_ref_link - no_params
# show_my_referrals - no_params
# show_leaders - <start_idx> <count> <is_desc>
# <aux_referral_event> - no_params

#-----------------------------------------------------#
#   SWOL REFER
#-----------------------------------------------------#
# '/gen_ref_link'
kREG_USER = "gen_ref_link"
LST_CMD_REG_USER = ['<tg_user_group_url>']
STR_ERR_REG_USER = f'Please tweet "@BearSharesX #Trinity register" 👍️️️️️️\n Then use that link to register with cmd:\n /{kREG_USER} {" ".join(LST_CMD_REG_USER)}'
LST_KEYS_REG_USER_RESP = env.LST_KEYS_PLACEHOLDER
DB_PROC_ADD_NEW_USER = 'ADD_TG_SOWL_PROMOTOR'
LST_KEYS_REG_USER = ['user_id','user_at','user_handle','tg_user_group_url'] # '<tg_user_group_url>'

# '/show_my_referrals'
kSHOW_USR_REF_HIST = "show_my_referrals"
LST_CMD_SHOW_HIST = ['<start_idx>','<count>','<is_desc>']
STR_ERR_SHOW_HIST = f'''please use cmd format :\n /{kSHOW_USR_REF_HIST} {" ".join(LST_CMD_SHOW_HIST)}'''
LST_KEYS_SHOW_HIST_RESP = env.LST_KEYS_PLACEHOLDER
DB_PROC_GET_USR_REF_HIST = 'GET_PROMOTOR_INFO'
LST_KEYS_SHOW_HIST = ['user_id','start_idx','count','is_desc']

# '/show_leaders'
kSHOW_LEADERS = "show_leaders"
LST_CMD_SHOW_LEADERS = ['<start_idx>','<count>','<is_desc>']
STR_ERR_SHOW_LEADERS = f'''please use cmd format :\n /{kSHOW_LEADERS} {" ".join(LST_CMD_SHOW_LEADERS)}'''
LST_KEYS_SHOW_LEADERS_RESP = env.LST_KEYS_PLACEHOLDER
DB_PROC_GET_LEADERS = 'GET_LEADER_BOARD' # get where 'is_approved' = False
LST_KEYS_SHOW_LEADERS = []

# '/aux_referral_event'
kAUX_REF_EVENT = "aux_referral_event"
LST_CMD_REF_EVENT = ['<is_join>', '<tg_user_group_url>']
STR_ERR_REF_EVENT = f'''please use cmd format :\n /{kAUX_REF_EVENT} {" ".join(LST_CMD_REF_EVENT)}'''
LST_KEYS_REF_EVENT_RESP = env.LST_KEYS_PLACEHOLDER
DB_PROC_REF_EVENT = 'EXE_REFERRAL_EVENT'
LST_KEYS_REF_EVENT = ['user_id','user_at','user_handle','is_join','tg_user_group_url']

#-----------------------------------------------------#
DICT_CMD_EXE = {
    # SWOL REFER CMDs
    kREG_USER:[kREG_USER,LST_KEYS_REG_USER,LST_KEYS_REG_USER_RESP,DB_PROC_ADD_NEW_USER,LST_CMD_REG_USER,STR_ERR_REG_USER],
    kSHOW_USR_REF_HIST:[kSHOW_USR_REF_HIST,LST_KEYS_SHOW_HIST,LST_KEYS_SHOW_HIST_RESP,DB_PROC_GET_USR_REF_HIST,LST_CMD_SHOW_HIST,STR_ERR_SHOW_HIST],
    kSHOW_LEADERS:[kSHOW_LEADERS,LST_KEYS_SHOW_LEADERS,LST_KEYS_SHOW_LEADERS_RESP,DB_PROC_GET_LEADERS,LST_CMD_SHOW_LEADERS,STR_ERR_SHOW_LEADERS],
    kAUX_REF_EVENT:[kAUX_REF_EVENT,LST_KEYS_REF_EVENT,LST_KEYS_REF_EVENT_RESP,DB_PROC_REF_EVENT,LST_CMD_REF_EVENT,STR_ERR_REF_EVENT],
}

#=====================================================#
#         request handler accessors/mutators          #
#=====================================================#
def exe_tg_cmd(_lst_inp, _is_web_dapp=False):
    funcname = f'{__filename} exe_tg_cmd(_is_web_dapp={_is_web_dapp})'
    print(funcname+' - ENTER')

    # generate keyVals to pass as 'request' w/ 'tg_cmd!=None', to 'handle_request'
    tg_cmd = _lst_inp[0][1::] # parse out the '/'
    lst_params = _lst_inp[1::]
    keyVals = {}
    print(' tg_cmd: '+tg_cmd)
    print(' lst_params: ', *lst_params, sep='\n  ')
    print(' DICT_CMD_EXE[tg_cmd][1]: ', *DICT_CMD_EXE[tg_cmd][1], sep='\n  ')

    # validate input cmd params count
    if len(lst_params) != len(DICT_CMD_EXE[tg_cmd][1]):
        print(' ** WARNING **: input cmd param count != db required param count; forcing return fail')
        str_req_params = ''.join(DICT_CMD_EXE[tg_cmd][-1])
        bErr, jsonResp = prepJsonResponseValidParams(keyVals, False, tprint=True, errMsg=f'invalid number of params; {str_req_params}') # False = force fail
        return jsonResp

    # generate keyVals from input cmd params
    for i,v in enumerate(lst_params): 
        print(f' lst_params[{i}]={v}')
        keyVals[DICT_CMD_EXE[tg_cmd][1][i]] = str(v) # [tg_cmd][1] = LST_KEYS_...
    
    print(' generated keyVals ...')
    [print(f'  keyVals[{k}]={keyVals[k]}') for k in keyVals.keys()]
    # simuate: 'handle_request(request, kREQUEST_KEY)' w/ added 'tg_cmd'
    return handle_request(keyVals, DICT_CMD_EXE[tg_cmd][0], tg_cmd)

#=====================================================#
#         STATIC request handler support              #
#=====================================================#
def handle_request(request, req_handler_key, tg_cmd=None):
    funcname = f'{__filename} handle_request'
    print(funcname + ' - ENTER')
    
    # (1) vaidate & parse request param key/vals
    bErr, jsonResp, keyVals = parse_request(request, req_handler_key, tg_cmd)
    if bErr:
        return jsonResp # JSONResponse(...)
        
    # (2) perfom database executions
    bErr, jsonResp, dbProcResult = execute_db_calls(keyVals, req_handler_key, tg_cmd)
    if bErr:
        return jsonResp # JSONResponse(...)

    # (3) generate success response params
    arrStrReturnKeys, strRespSuccessMSG = generate_resp_params(req_handler_key, keyVals, tg_cmd)
    
    # (4) prepare return json model
    # jsonResp = prepJsonResponseDbProc(arrStrReturnKeys, dbProcResult, strRespSuccessMSG, tprint=False)
    if tg_cmd: jsonResp = prepJsonResponseDbProc_ALL(arrStrReturnKeys, dbProcResult, strRespSuccessMSG, tprint=VERBOSE_LOG)
    else: jsonResp = prepJsonResponseDbProc(arrStrReturnKeys, dbProcResult, strRespSuccessMSG, tprint=VERBOSE_LOG)
    
    # (5) return client response
    return jsonResp # JSONResponse(...) -> Response(json.dumps(dict), mimetype="application/json" )

def parse_request(request, req_handler_key, tg_cmd=None): # (1)
    funcname = f'{__filename} parse_request'
    print(funcname + ' - ENTER')
    
    if tg_cmd:
        keyVals = dict(request)
        print('HIT - tg_cmd: '+tg_cmd)
        if tg_cmd in DICT_CMD_EXE.keys():
            # if tg_cmd == kADMIN_SET_SHILL_REM:
            #     if keyVals['removed']=='yes' or keyVals['removed']=='removed' or keyVals['removed']=='1' or keyVals['removed'].lower()=='true':
            #         keyVals['removed'] = '1'
            #     else:
            #         keyVals['removed'] = '0'
            pass
        else:
            bErr, jsonResp = prepJsonResponseValidParams(keyVals, False, tprint=VERBOSE_LOG, errMsg='command not found') # False = force fail
            return bErr, jsonResp, -1 # dbProcResult
        
    else:
        # note: utilizing additional dict here (instead of just request.form/args/get_json())
        #   because we want to be secure the params passed to the database are only the keys we want
        reqParamsImmutDict = request.form
        #print(funcname, 'reqParamsImmutDict - DONE', f'{reqParamsImmutDict}', tprint=True)

        # validate required params & set local vars
        keyVals = reqParamsImmutDict.copy()["key_vals"] if reqParamsImmutDict is not None else None

        keyVals = json.loads(keyVals)
        #print(funcname, 'keyVals - DONE', tprint=True)

    # validate request params (PIN, keys, etc.)
    validParams0 = validate_params(keyVals, req_handler_key, tg_cmd)
    #print(funcname, 'validParams0 - DONE', tprint=True)

    #bErr, jsonResp = prepJsonResponseValidParams(keyVals, validParams0, valid_PIN, tprint=True)
    bErr, jsonResp = prepJsonResponseValidParams(keyVals, validParams0, tprint=True)
    #print(funcname, 'prepJsonResponseValidParams - DONE', tprint=True)
    if bErr:
        return bErr, jsonResp, None # JSONResponse(...)
        
    return bErr, jsonResp, keyVals

#=====================================================#
#         DYNAMIC request handler support             #
#=====================================================#
def execute_db_proc(keyVals, stored_proc):
    funcname = f'{__filename} execute_db_call_simple'
    print(funcname + ' - ENTER')
    dbProcResult = exe_stored_proc(-1, stored_proc, keyVals)
    bErr, jsonResp = prepJsonResponseDbProcErr(dbProcResult, tprint=VERBOSE_LOG)
    if bErr: return False, 'db error occurred', dbProcResult
    return True, jsonResp, dbProcResult

    # LEFT OFF HERE ...

# append req_handler_key, parse keyVals params, invoke database function
def execute_db_calls(keyVals, req_handler_key, tg_cmd=None): # (2)
    funcname = f'{__filename} execute_db_calls'
    print(funcname + ' - ENTER')

    # perfom database executions
    bErr=False
    jsonResp={}
    dbProcResult = None

    if tg_cmd != None:
        print('HIT - tg_cmd: '+tg_cmd)
        if tg_cmd in DICT_CMD_EXE.keys():                            
            # if 'user_id' in keyVals: del keyVals['user_id']
            stored_proc = DICT_CMD_EXE[tg_cmd][3] # [tg_cmd][3] = 'stored-proc-name'
            dbProcResult = exe_stored_proc(-1, stored_proc, keyVals)
            if dbProcResult[0]['status'] == 'failed': errMsg = dbProcResult[0]['info']
            else: errMsg = None
            bErr, jsonResp = prepJsonResponseDbProcErr(dbProcResult, tprint=VERBOSE_LOG, errMsg=errMsg) # errMsg != None: force fail from db
        else:
            dbProcResult=-1
            bErr, jsonResp = prepJsonResponseDbProcErr(dbProcResult, tprint=True)
    else:
        # NOTE: current http request integration is delgated through 'exe_tg_cmd'
        print('HIT - http request integration')
        pass 
    
    return bErr, jsonResp, dbProcResult

# append req_handler_key, set arrStrReturnKeys & strRespSuccessMSG
def generate_resp_params(req_handler_key, keyVals=None, tg_cmd=None): # (3)
    funcname = f'{__filename} generate_resp_params'
    print(funcname + ' - ENTER')
    
    # success response params
    arrStrReturnKeys = ["nil_keys"]
    strRespSuccessMSG = "nil_msg"

    if tg_cmd != None:
        if tg_cmd in DICT_CMD_EXE.keys():
            arrStrReturnKeys = DICT_CMD_EXE[tg_cmd][2] # [tg_cmd][2] = LST_KEYS_..._RESP
            strRespSuccessMSG = f"CMD {tg_cmd} successful!"
        else:
            arrStrReturnKeys = [f"nil_keys, err failed to find req_handler_key: {req_handler_key}"]
            strRespSuccessMSG = f"nil_msg, err failed to find req_handler_key: {req_handler_key}"
    else:
        pass # http request integration
        
    return arrStrReturnKeys, strRespSuccessMSG

# append req_handler_key, invoke keyVals validation function
def validate_params(keyVals, req_handler_key, tg_cmd=None):
    funcname = f'{__filename} validate_params'
    print(funcname + ' - ENTER')
    #valid_PIN = validatePIN(keyVals)
    
    if tg_cmd != None:
        if tg_cmd in DICT_CMD_EXE.keys():
            return valid_keys(keyVals, DICT_CMD_EXE[tg_cmd][1]) # [tg_cmd][1] = LST_KEYS_...
        else:
            return False
    else:
        # http request integration
        return req_handler_key == 'TRINITY_WEB_DAPP'
    return False

#=====================================================#
#         endpoint key validation support             #
#=====================================================#
def validatePIN(keyVals):
    funcname = f'({__filename}) validatePIN'
    if kPin not in keyVals:
        return False

    vPin = str(keyVals[kPin])
    print(funcname, f"procValidatePIN({vPin})...")
    dbResult = procValidatePIN(strPIN=vPin)
    print(funcname, f"procValidatePIN({vPin}) = {dbResult}")
    return dbResult > 0

## all endpoint key validations ##
def valid_keys(keyVals, lst_valid_keys):
    funcname = f'{__filename} valid_keys'
    print(funcname + ' - ENTER')
    if keyVals is None or len(keyVals) < 1:
        print(funcname, 'FAILED static/constant keyVals check lenth; returning False')
        return False
    for idx, key in enumerate(lst_valid_keys):
        if key not in keyVals:
            print(funcname, f'FAILED static/constant keyVals check key: {key}; returning False')
            return False
    return True

#====================================================#
#====================================================#

print(__filename, f"\n CLASSES & FUNCTIONS initialized:- STARTING -> additional '{__filename}' run scripts (if applicable) . . .")
print(__filename, f"\n  DONE Executing additional '{__filename}' run scripts ...")
print('#======================================================================#')


        