__fname = 'db_controller'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
cStrDivider_1 = '#----------------------------------------------------------------#'
print('', cStrDivider, f'GO _ {__filename} -> starting IMPORTs & declaring globals', cStrDivider, sep='\n')

from _env import env
import pprint
# from house_tools import *

'''
# https://mariadb.com/resources/blog/how-to-connect-python-programs-to-mariadb/
# https://docs.sqlalchemy.org/en/13/dialects/mysql.html#module-sqlalchemy.dialects.mysql.pymysql
    mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]
# https://pymysql.readthedocs.io/en/latest/user/examples.html
    #NOTE: '$ pip3' == '$ python3.6 -m pip'
        $ python3 -m pip install PyMySQL
        $ python3.7 -m pip install PyMySQL
    '''
import pymysql.cursors
import subprocess # mysql dump support
import paramiko # ssh connect support

print(__filename, f" IMPORTs complete:- STARTING -> file '{__filename}' . . . ", sep=' ')

dbHost = env.dbHost #read_env()
dbName = env.dbName #read_env()
dbUser = env.dbUser #read_env()
dbPw = env.dbPw     #read_env()

# dbHost = env.dbHost #read_env()
# dbUser = env.dbUser #read_env()

db = None
cur = None
ssh_client = None

strErrCursor = "global var cur == None, returning -1"
strErrConn = "FAILED to connect to db"

#====================================================#
##              db connection support               ##
#====================================================#
def open_database_connection_remote(use_ssh=False, ssh_dict={}):
    funcname = f'{__filename} open_database_connection_remote(use_ssh={use_ssh})'
    print(funcname, '- ENTER')

    # Connect to DB #
    try:
        global db, cur, ssh_client        
        if use_ssh: # NOTE_010524: not working correctly
            # Set up the SSH tunnel
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the SSH server using the .pem key
            ssh_client.connect(ssh_dict['host'], username=ssh_dict['user'], key_filename=ssh_dict['path'])

            # Set up port forwarding for the MySQL connection through the SSH tunnel
            forward = ssh_client.get_transport().open_channel(
                'direct-tcpip',
                ('localhost', 3306),
                ('127.0.0.1', 3306)
            )
            db = pymysql.connect(host=dbHost,
                                port=forward.getpeername()[1],
                                user=dbUser,
                                password=dbPw,
                                db=dbName,
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)            
        else:
            db = pymysql.connect(host=dbHost,
                                user=dbUser,
                                password=dbPw,
                                db=dbName,
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)            
        cur = db.cursor()

        if cur == None:
            print(funcname, "REMOTE database cursor received (cur) == None; returning None", "FAILED to connect to db")
            return -1

        print(funcname, f' >> REMOTE CONNECTED >> to db {dbName} successfully!')
    except Exception as e:
        print(funcname, "exception hit", "FAILED to REMOTE connect to db")
        print_except(e, debugLvl=2)
        return -1
    finally:
        return 0

def open_database_connection():
    funcname = f'{__filename} open_database_connection'
    print(funcname, '- ENTER')

    # Connect to DB #
    try:
        global db, cur

        # legacy manual db connection #
        db = pymysql.connect(host=dbHost,
                             user=dbUser,
                             password=dbPw,
                             db=dbName,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        cur = db.cursor()

        if cur == None:
            print(funcname, "database cursor received (cur) == None; returning None", "FAILED to connect to db")
            return -1

        print(funcname, f' >> CONNECTED >> to db {dbName} successfully!')
    except Exception as e:
        print(funcname, "exception hit", "FAILED to connect to db")
        print_except(e, debugLvl=2)
        return -1
    finally:
        return 0

def close_database_connection(use_ssh=False):
    funcname = f'{__filename} close_database_connection'
    print(funcname, '- ENTER')

    global db, cur
    if db == None:
        print(funcname, "global var db == None; returning", "FAILED to close db connection")
        return

    db.commit()
    db.close()
    if use_ssh: ssh_client.close()

    db = None
    cur = None
    if use_ssh: ssh_client = None
    print(funcname, ' >> CLOSED >> db successfully!')

# Run mysqldump command to export table structure and content
def exeMySqlDump(tableNames='nil_tables', fileName='nil_file.sql', use_remote=False, use_ssh=False, ssh_dict={}):
    funcname = f'{__filename} exeMySqlDump({tableNames}, {fileName}, use_remote={use_remote})'
    print(funcname, '- ENTER')

    #============ open db connection ===============#
    global cur
    if use_remote:
        if open_database_connection_remote(use_ssh, ssh_dict) < 0:
            return -1
    else:
        if open_database_connection() < 0:
            return -1
    if cur == None:
        print(funcname, strErrCursor, strErrConn)
        return -1

    #============ perform mysqldump ===============#
    dump_error = 'nil_dump_error'
    result = None
    try:
        ## Run mysqldump command to export table structure and content ##
        # dump_command = f"mysqldump -u {dbUser} -p{dbPw} -h {dbHost} --databases {dbName} --tables {tableNames}" # .env password
        dump_command = f"mysqldump -u {dbUser} -p -h {dbHost} --databases {dbName} --tables {tableNames}" # CLI enter password
        dump_process = subprocess.Popen(dump_command, stdout=subprocess.PIPE, shell=True)
        dump_output, dump_error = dump_process.communicate()

        # Save the output to a .sql file
        with open(fileName, 'wb') as output_file:
            output_file.write(dump_output)

        print()
        print(funcname, f"dump_command: '{dump_command}'")
        print(funcname, f"dump_error: '{dump_error}'")
        print()
        print(funcname, f"DONE: Table '{tableNames}' exported to {fileName}")
        print()

    except Exception as e: # ref: https://docs.python.org/2/tutorial/errors.html
        #============ handle db exceptions ===============#
        strE_0 = f"Exception hit... \nFAILED to call '{funcname}'; \n\nw/ tables: {tableNames}; file: {fileName}; dump_error: {dump_error} \n\nreturning -1"
        strE_1 = f"\n __Exception__: \n{e}\n __Exception__"
        print(funcname, strE_0, strE_1)
        result = -1
    finally:
        #============ close db connection ===============#
        close_database_connection(use_ssh)
        return result
        
def exeStoredProcedure(argsTup, strProc, strOutParam=None, exe_select=False):
    # funcname = f'{__filename} exeStoredProcedure({argsTup}, {strProc}, {strOutParam}, exe_select={exe_select})'
    funcname = f'{__filename} exeStoredProcedure'
    print(funcname, '- ENTER')

    #============ open db connection ===============#
    global cur
    if open_database_connection() < 0:
        return -1

    if cur == None:
        print(funcname, strErrCursor, strErrConn)
        return -1

    #============ perform db query ===============#
    procArgs = 'nil'
    rowCnt = 'nil'
    rows = 'nil'

    try:
        if exe_select:
            procArgs = argsTup
            rowCnt = cur.execute(strProc)
            rows = cur.fetchall()
        else:
            procArgs = cur.callproc(f'{strProc}', argsTup)
            rowCnt = cur.execute(f"select {strOutParam};") if strOutParam != None else -1
            rows = cur.fetchall()

        # print(funcname, f" >> RESULT 'call {strProc}' procArgs: {procArgs};")
        # print(funcname, f" >> RESULT 'call {strProc}' rowCnt: {rowCnt};")
        #print(funcname, f' >> Printing... rows', *rows)
        # getPrintListStr(lst=rows, strListTitle='  >> Printing... rows', useEnumerate=True, goIdxPrint=True, goPrint=True)
        #print(funcname, f' >> Printing... rows[0]:', rows[0])
        if False:
            print(' >> Printing... rows')
            pprint.pprint(rows)
            print(' >> Printing... rows _ DONE')
        else: print(' >> Printing.. rows <disabled>')
        
        result = None
        if strOutParam == None: # stored proc invoked w/o OUT param
            result = rows
        else: # stored proc invoked w/ OUT param
            result = rows[0][strOutParam]
            if isTypeInteger(rows[0][strOutParam]):
                result = int(rows[0][strOutParam])
    except Exception as e: # ref: https://docs.python.org/2/tutorial/errors.html
        #============ handle db exceptions ===============#
        strE_0 = f"Exception hit... \n  FAILED to call '{funcname}'; \n\n  procArgs: {procArgs}; \n\n  returning -1"
        strE_1 = f"\n __Exception__: \n  {e}\n __Exception__"
        print('\n**************\n', funcname, strE_0, strE_1,'\n**************\n')
        result = -1
    finally:
        #============ close db connection ===============#
        close_database_connection()
        return result

def exe_stored_proc(iUserID=-1, strProc='', dictKeyVals={}):
    # funcname = f'{__filename} exe_stored_proc(iUserID={iUserID}, strProc={strProc}, dictKeyVals={dictKeyVals})'
    funcname = f'{__filename} exe_stored_proc'
    print(funcname, '- ENTER')

    argsTup = () # generate tuple of vals from dictKeyVals (dict order maintained in python3.7+)
    argsTup = [argsTup + (dictKeyVals[k],) for k in dictKeyVals]
    strOutParam = None
    args_print = ', '.join(list(dictKeyVals.values()))
    print(f' exe proc: {strProc}({args_print})')
    return exeStoredProcedure(argsTup, strProc, strOutParam)

def sel_2_tbl_query(d_col_val_where_1={},
                        d_col_val_where_2={},
                        lst_col_sel_1=[],
                        lst_col_sel_2=[],
                        str_tbl_1='',
                        str_tbl_2='',
                        str_tbl_as_1='',
                        str_tbl_as_2='',
                        bGetAll=False):
    funcname = f'{__filename} sel_2_tbl_query(d_col_val_where_1={d_col_val_where_1}, d_col_val_where_2={d_col_val_where_2}, lst_col_sel_1={lst_col_sel_1}, lst_col_sel_2={lst_col_sel_2}, str_tbl_as_1={str_tbl_as_1}, str_tbl_as_2={str_tbl_as_2}, bGetAll={bGetAll})'
    print(funcname, '- ENTER')

    # generate string using lst_col_sel_1|2:
    #   EX: 'SELECT <columns> FROM candidates cand INNER JOIN candidate_apps capp'
    strSel = ''
    print(funcname, f'strSel: {strSel}')
    if bGetAll:
        #print(funcname, f"bGetAll: {bGetAll}")
        strSel = f'SELECT {str_tbl_as_1}.*, {str_tbl_as_2}.*, {str_tbl_as_1}.id AS {str_tbl_as_1}_id, {str_tbl_as_2}.id AS {str_tbl_as_2}_id FROM {str_tbl_1} {str_tbl_as_1} INNER JOIN {str_tbl_2} {str_tbl_as_2} ON {str_tbl_as_2}.fk_{str_tbl_as_1}_id = {str_tbl_as_1}.id'
    else:
        # init query string w/ select clause
        strSel = f"SELECT {str_tbl_as_1}.id AS {str_tbl_as_1}_id, {str_tbl_as_2}.id AS {str_tbl_as_2}_id,"
        
        # generate & append str_tbl_as_1 select clause
        #   loop through 'lst_col_sel_1' (client side str_tbl_as_1 col names selected)
        for idx, col in enumerate(lst_col_sel_1):
            c = col.lower()
            if idx < len(lst_col_sel_1) - 1 or len(lst_col_sel_2) > 0:
                strSel = f"{strSel} {str_tbl_as_1}.`{c}`,"
            else:
                strSel = f"{strSel} {str_tbl_as_1}.`{c}`"

        # generate & append str_tbl_as_2 select clause
        #   loop through 'lst_col_sel_2' (client side str_tbl_as_2 col names selected)
        for idx, col in enumerate(lst_col_sel_2):
            c = col.lower()
            if idx < len(lst_col_sel_2) - 1:
                strSel = f"{strSel} {str_tbl_as_2}.`{c}`,"
            else:
                strSel = f"{strSel} {str_tbl_as_2}.`{c}`"
                
        # append FROM clause
        strSel = f"{strSel} FROM {str_tbl_1} {str_tbl_as_1} JOIN {str_tbl_2} {str_tbl_as_2} ON {str_tbl_as_2}.fk_{str_tbl_as_1}_id = {str_tbl_as_1}.id"

    # print current strSel
    print(funcname, f'strSel: {strSel}')
    
    # check / init WHERE clause
    print(funcname, f"d_col_val_where_1: {d_col_val_where_1}\n", f"d_col_val_where_2: {d_col_val_where_2}")
    if len(d_col_val_where_1) > 0 or len(d_col_val_where_2) > 0:
        strSel = f"{strSel} WHERE"

        # generate string using d_col_val_where_1|2:
        #   'WHERE <col=val>'
        for idx, key in enumerate(d_col_val_where_1):
            k = key.lower()
            if idx < len(d_col_val_where_1) - 1 or len(d_col_val_where_2) > 0: # check appending 'and' as needed
                if k[0:3:1] == 'dt_': # check for handling datetime inputs & cols
                    strSel = f"{strSel} DATE({str_tbl_as_1}.{k}) = DATE('{d_col_val_where_1[key]}') and"
                else:
                    strSel = f"{strSel} {str_tbl_as_1}.{k} = '{d_col_val_where_1[key]}' and"
            else:
                if k[0:3:1] == 'dt_':
                    strSel = f"{strSel} DATE({str_tbl_as_1}.{k}) = DATE('{d_col_val_where_1[key]}')"
                else:
                    strSel = f"{strSel} {str_tbl_as_1}.{k} = '{d_col_val_where_1[key]}'"
        for idx, key in enumerate(d_col_val_where_2):
            k = key.lower()
            if idx < len(d_col_val_where_2) - 1: # check appending 'and' as needed
                if k[0:3:1] == 'dt_': # check for handling datetime inputs & cols
                    strSel = f"{strSel} DATE({str_tbl_as_2}.{k}) = DATE('{d_col_val_where_2[key]}') and"
                else:
                    strSel = f"{strSel} {str_tbl_as_2}.{k} = '{d_col_val_where_2[key]}' and"
            else:
                if k[0:3:1] == 'dt_':
                    strSel = f"{strSel} DATE({str_tbl_as_2}.{k}) = DATE('{d_col_val_where_2[key]}')"
                else:
                    strSel = f"{strSel} {str_tbl_as_2}.{k} = '{d_col_val_where_2[key]}'"
                
    # print current strSel
    print(funcname, f'strSel: {strSel}')
    
    # append end query sorting
    strSel = f"{strSel} ORDER BY {str_tbl_as_2}_id DESC;"
    
    # print current strSel
    print(funcname, f'strSel: {strSel}')
    
    argsTup = (d_col_val_where_1, d_col_val_where_2, lst_col_sel_1, lst_col_sel_2, bGetAll)
    strProc = strSel
    strOutParam = None
    return exeStoredProcedure(argsTup, strProc, strOutParam, exe_select=True)

#===========================================================#
# db_controller support (migrated from gms_post)
#===========================================================#
def procValidatePIN(strPIN='-1'):
    funcname = f'{__filename} procValidatePIN(strPIN={strPIN})'
    print(funcname, '- ENTER')

    argsTup = (strPIN, 'p_Result')
    strProc = 'ValidatePIN'
    strOutParam = '@_ValidatePIN_1'
    return exeStoredProcedure(argsTup, strProc, strOutParam)

def procGetEmpData(strPIN=''):
    funcname = f'{__filename} procGetEmpData({strPIN})'
    print(funcname, '- ENTER')

    argsTup = (strPIN,)
    strProc = 'GetEmpDataFrom_PIN'
    strOutParam = None
    return exeStoredProcedure(argsTup, strProc, strOutParam)
    
    #exeStoredProcedure(argsTup, strProc, strOutParam=None, exe_select=False)
    
def isTypeInteger(varCheck=None):
    if varCheck == None:
        return False
    return isinstance(varCheck, int)

def getPrintListStr(lst=[], strListTitle='list', useEnumerate=True, goIdxPrint=False, goPrint=True):
    strGoIndexPrint = None
    if goIdxPrint:
        strGoIndexPrint = '(w/ indexes)'
    else:
        strGoIndexPrint = '(w/o indexes)'

    lst_str = None
    if useEnumerate:
        if goIdxPrint:
            lst_str = [f'{i}: {v}' for i,v in enumerate(lst)]
        else:
            lst_str = [f'{v}' for i,v in enumerate(lst)]
    else:
        if goIdxPrint:
            lst_str = [f'{lst.index(x)}: {x}' for x in lst]
        else:
            lst_str = [f'{x}' for x in lst]

    lst_len = len(lst)
    print(f'{strListTitle} _ {strGoIndexPrint} _ count {lst_len}:', *lst_str, sep = "\n ")
    return lst_str

#ref: https://stackoverflow.com/a/1278740/2298002
def print_except(e, debugLvl=0):
    #print(type(e), e.args, e)
    if debugLvl >= 0:
        print('', cStrDivider, f' Exception Caught _ e: {e}', cStrDivider, sep='\n')
    if debugLvl >= 1:
        print('', cStrDivider, f' Exception Caught _ type(e): {type(e)}', cStrDivider, sep='\n')
    if debugLvl >= 2:
        print('', cStrDivider, f' Exception Caught _ e.args: {e.args}', cStrDivider, sep='\n')
    if debugLvl >= 3:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        strTrace = traceback.format_exc()
        print('', cStrDivider, f' type: {exc_type}', f' file: {fname}', f' line_no: {exc_tb.tb_lineno}', f' traceback: {strTrace}', cStrDivider, sep='\n')
    
#====================================================#
#====================================================#

print(__filename, f"\n CLASSES & FUNCTIONS initialized:- STARTING -> additional '{__filename}' run scripts (if applicable) . . .")
print(__filename, f"\n  DONE Executing additional '{__filename}' run scripts ...")
print('#======================================================================#')
