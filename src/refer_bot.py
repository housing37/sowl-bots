__fname = 'refer_bot' # model: trinity_boy.py
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
cStrDivider_1 = '#----------------------------------------------------------------#'
print('', cStrDivider, f'GO _ {__filename} -> starting IMPORTs & declaring globals', cStrDivider, sep='\n')

#------------------------------------------------------------#
#   IMPORTS                                                  #
#------------------------------------------------------------#
# import random, 
import pprint
from _env import env
import time, os, traceback, sys, json, pprint
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ChatMemberHandler, filters, CallbackQueryHandler, CallbackContext
import req_handler

# Define the timestamp representing the bot's last online time
last_online_time = time.time()  # Initialize with current time

#------------------------------------------------------------#
#   GLOBALS                                                  #
#------------------------------------------------------------#
# constants
DEBUG_LVL = 3
ALLOW_DMS = True
LST_TG_CMDS = list(req_handler.DICT_CMD_EXE.keys())
DEV_CHAT_ID = '-1002375576767' # tg group: test_sowl_test_bot
PROD_CHAT_ID_0 = '-1002275201622' # tg group: test_sowl_refer_bot
PROD_CHAT_ID_1 = '-1002003863532' # tg group: $SOWL🦉 ZONE
PROD_CHAT_ID = PROD_CHAT_ID_0
WHITELIST_CHAT_IDS = [
    '-1002375576767', # tg group: test_sowl_test_bot
    '-1002275201622', # tg group: test_sowl_refer_bot
    '-1002003863532', # tg group: $SOWL🦉 ZONE
    ]
BLACKLIST_TEXT = [
    'smart vault', 'smart-vault', 'smart_vault', # @JstKidn
    ]
REF_MSG_CNT_REQ = 1
USER_MSG_CNT = {
    # '<tg_user_id>':(-1, Update, CallbackContext)
}
# input select
USE_PROD_TG = False
TOKEN = 'nil_tg_token'
USE_ALT_ACCT = False # True = alt user 'LAO Pirates'

# # disable parsing '.from_user.first_name' (note_031824: db encoding errors)
# DISABLE_TG_HANDLES = True 

BOT_INFO = '''
Instructions:
    1) generate a personal referal link to this TG group (TG @username required, 1 link per @username)
    2) give that link to anyone you want to refer to this TG group
    3) someone uses your personal referal link to join this TG group
    4) you will earn 1 point for each person that uses your referal link
    5) you will lose 1 point if a person who joins with your link, leaves this TG group
    6) you can view promotor info (referal link, points earned, users joined, users/points lost)

CMDs ...
    /gen_ref_link
    /show_my_referrals
    /show_leaders
    <aux_referral_event>

Questions: @housing37

*IMORTANT* 
    you need a TG @username setup to use this bot

GLHF!
'''

#------------------------------------------------------------#
#   FUNCTIONS                                                #
#------------------------------------------------------------#
def set_tg_token():
    global TOKEN
    TOKEN = env.TOKEN_sowl if USE_PROD_TG else env.TOKEN_sowl_test

def is_valid_chat_id(_chat_id, _group_name, _uname, _handle):
    print("chat_id:", _chat_id)
    if _group_name: print("Group name:", _group_name)
    else: print("*NOTE* This message was not sent from a group.")
    if str(_chat_id) not in WHITELIST_CHAT_IDS: # check whitelisted groups
        print("*** WARNING ***: non-whitelist TG group trying to use the bot; generating deny message...")
        str_deny = f"@{_uname} (aka. {_handle}): ... not authorized"
        print(str_deny)
        return False, str_deny
    return True, ''

# def filter_prompt(_prompt):
#     funcname = 'filter_prompt'
#     # print(f'ENTER - {funcname}')
#     prompt_edit = _prompt.lower()
#     found_blacklist = False
#     print("Checking '_prompt' for BLACKLIST_TEXT...")
#     for i in BLACKLIST_TEXT:
#         print(' [X] '+i)
#         if i in prompt_edit:
#             print(f'  found BLACKLIST_TEXT: {i} ... (editing & continue)')
#             prompt_edit = prompt_edit.replace(i, 'bear shares')
#             found_blacklist = True

#     if found_blacklist:
#         return prompt_edit
#     return _prompt

def past_queue_limit(_msg_time, _q_sec=5*60):
    sec_diff = time.time() - _msg_time
    if sec_diff > _q_sec: print(f"Ignoring message sent more than {_q_sec} sec ago.")
    return sec_diff > _q_sec

async def cmd_handler(update: Update, context):
    # Calculate the timestamp of 5 minutes ago
    if past_queue_limit(update.message.date.timestamp()): return

    global USE_ALT_ACCT
    funcname = 'cmd_handler'
    print(cStrDivider_1, f'ENTER - {funcname} _ {get_time_now()}', sep='\n')
    
    chat_type = update.message.chat.type
    is_dm = chat_type == 'private'
    group_name = update.message.chat.title if update.message.chat.type == 'supergroup' else None
    _chat_id = update.message.chat_id

    user = update.message.from_user
    uid = user.id
    uname_at = user.username if user.username else 'nil_at'
    uname_handle = user.first_name if user.first_name else 'nil_disabled'
    if user.last_name:
        uname_handle = uname_handle + ' ' + user.last_name
    inp_split = list(update.message.text.split())

    # parse about @user (if user simply hit enter from cmd description list in TG chat)
    if '@' in inp_split[0]: inp_split[0] = inp_split[0].split('@')[0]

    # check if TG group is whitelisted to use (prints group info and deny)
    #   NOTE: at this point, inp_split[0] is indeed a valid command
    print(f'handling cmd: '+inp_split[0])
    print(f"chat_type: {chat_type}")
    print(f"_chat_id: {_chat_id}")
    tg_cmd = inp_split[0][1::] # parses out the '/'
    
    # fail: if not in WHITELIST_CHAT_IDS and not a DM
    valid_chat, str_deny = is_valid_chat_id(str(_chat_id), group_name, uname_at, uname_handle)
    # print(valid_cmd, valid_chat, chat_type, str_deny, sep='\n')

    # if DM and DMs not allow ... OR ... not a DM and not a valid chat
    #   then send deny message
    if (is_dm and not ALLOW_DMS) or (not valid_chat and not is_dm):
        await context.bot.send_message(chat_id=update.message.chat_id, text=str_deny+' '+inp_split[0])    
        print('', f'EXIT - {funcname} _ {get_time_now()}', cStrDivider_1, sep='\n')
        return

    # validate that TG @username is setup (required to participate)
    if uname_at == None:
        uname_at = str(uid)
        # str_r = f'invalid TG user. no TG @username setup for your account. Please add an @username to your TG account and try to register again.'
        # print(str_r)
        # print('', f'EXIT - {funcname} _ {get_time_now()}', cStrDivider_1, sep='\n')
        # await update.message.reply_text(str_r)
    
    # NOTE: all non-admin db procs require 'tg_user_id' & 'tg_user_at' (ie. uid & uname_at)
    if 'admin' not in tg_cmd:
        print(f'No admin found in tg_cmd: {tg_cmd}')
        if tg_cmd == req_handler.kREG_USER: # proc: ADD_TG_SOWL_PROMOTOR
            print(f'Detected cmd: {req_handler.kREG_USER}')
            # input /cmd ['</cmd>','tg_user_id','user_at','user_handle','chat_id','<tg_user_group_url>']
            inp_split.insert(1, str(uid)) 
            inp_split.insert(2, uname_at)
            # inp_split.insert(3, uname_handle)
            inp_split.insert(3, "handle_disabled_ref")
            inp_split.insert(4, str(_chat_id))

            # generate random unique invite link
            link_chat_id = _chat_id
            print(f'link_chat_id: {link_chat_id}')
            print(f'USE_PROD_TG: {USE_PROD_TG}')
            print(f'PROD_CHAT_ID: {PROD_CHAT_ID}')
            print(f'DEV_CHAT_ID: {DEV_CHAT_ID}')
            print(f'is_dm: {is_dm}')
            if is_dm: # set proper chat_id for invite link and db entry
                link_chat_id = PROD_CHAT_ID if USE_PROD_TG else DEV_CHAT_ID
                inp_split[4] = link_chat_id
            print(f'link_chat_id: {link_chat_id}')
            invite_link = await context.bot.create_chat_invite_link(chat_id=link_chat_id)
            inp_split.insert(5, invite_link['invite_link'])

        if tg_cmd == req_handler.kSHOW_USR_REF_HIST: # proc: GET_PROMOTOR_INFO
            # input /cmd = ['</cmd>','tg_user_id','<start_idx>','<count>','<is_desc>']
            inp_split.insert(1, uid)
            inp_split.insert(2, 0)
            inp_split.insert(3, 100)
            inp_split.insert(4, 1)

        if tg_cmd == req_handler.kSHOW_LEADERS: # proc: GET_LEADER_BOARD
            # input /cmd = ['</cmd>','<start_idx>','<count>','<is_desc>']
            inp_split.insert(1, 0)
            inp_split.insert(2, 100)
            inp_split.insert(3, 0)

            pass # no additional params for 'show_leaders'

    # NOTE: all admin db procs require 'tg_admin_id' & 'tg_user_at' (ie. uid & <tg_user_at>)    
    else: # if 'admin' in tg_cmd
        pass

    print(f'Sending inp_split to cmd_exe: {inp_split}')
    context.user_data['inp_split'] = list(inp_split)
    await cmd_exe(update, context)
    print('', f'EXIT - {funcname} _ {get_time_now()}', cStrDivider_1, sep='\n')

async def btn_option_selects(update: Update, context):
    print('btn_option_selects - ENTER')
    query = update.callback_query

    inp_split = context.user_data['inp_split']
    tg_cmd = inp_split[0][1::] # parses out the '/'

    context.user_data['inp_split'] = list(inp_split)
    await cmd_exe(update, context)

async def cmd_exe(update: Update, context: CallbackContext, aux_cmd=False, _tprint=False):
    if _tprint: pprint.pprint(update.to_dict())  # Convert to dict for easier reading
    funcname = 'cmd_exe'
    print(cStrDivider_1, f'ENTER - {funcname} _ {get_time_now()}', sep='\n')
    
    inp_split = list(context.user_data['inp_split'])
    print(f'cmd_exe: '+inp_split[0])
    tg_cmd = inp_split[0][1::] # parses out the '/'
    
    print(f'GO - req_handler.exe_tg_cmd ... {get_time_now()}')
    response = req_handler.exe_tg_cmd(inp_split)
    response_dict = json.loads(response.get_data(as_text=True))
    print(f'GO - req_handler.exe_tg_cmd ... {get_time_now()} _ DONE')

    print('\nprinting response_dict ...')
    pprint.pprint(response_dict)
    # print(response_dict)

    # return jsonResp # JSONResponse(...) -> Response(json.dumps(dict), mimetype="application/json" )
    if int(response_dict['ERROR']) > 0:
        err_num = response_dict['ERROR']
        err_msg = response_dict['MSG']

        if not update.message:
            # await update.callback_query.message.reply_text(f"err_{err_num}: {err_msg}")
            if not aux_cmd: await update.callback_query.message.reply_text(f"err_{err_num}: {err_msg}")
        else:
            str_resp = f"err_{err_num}: {err_msg}"
            if not aux_cmd: await update.message.reply_text(str_resp)
    else:
        d_resp_arr = response_dict['PAYLOAD']['result_arr']
        d_resp = response_dict['PAYLOAD']['result_arr'][0]
        if tg_cmd == req_handler.kREG_USER:
            # shill_id = d_resp['shill_id']
            
            # inc_ = ['post_url','shill_id','pay_usd','is_approved','tg_user_at_inp','is_paid','shill_plat','shill_type']
            # d_resp['tg_user_at_inp'] = '@'+str(d_resp['tg_user_at_inp'])
            # str_r = '\n '.join([str(k)+': '+str(d_resp[k]) for k in d_resp.keys() if str(k) in inc_])
            # await update.message.reply_text(f"Info for shill id: {shill_id} ...\n {str_r}")
            
            new_ref_link = d_resp['new_tg_user_group_url']
            pr_at = '@'+str(d_resp['tg_user_at'])
            str_r = '\n '.join([str(k)+': '+str(d_resp[k]) for k in d_resp.keys() ])
            await update.message.reply_text(f"Registration successful!\nYour referral link (for {pr_at}):\n {new_ref_link}")
        elif tg_cmd == req_handler.kSHOW_USR_REF_HIST:
            str_r = ''
            for d in d_resp_arr:
                pr_at = '@'+str(d['tg_user_at_prom'])
                rf_at = '@'+str(d['tg_user_at_ref'])
                str_live = 'live:'+ "True" if d['is_active_ref'] else "False"
                str_r += f' {pr_at} referred {rf_at} _ {str_live}\n'
            await update.message.reply_text(f"Your Referrals ...\n{str_r}")
        elif tg_cmd == req_handler.kSHOW_LEADERS:
            str_r = ''
            for d in d_resp_arr:
                pr_at = '@'+str(d['tg_user_at'])
                pr_pts = str(d['new_total_pts'])
                str_r += f' {pr_at} -> referral pts: {pr_pts}\n'
            await update.message.reply_text(f"Leader Board ...\n{str_r}")
        elif tg_cmd == req_handler.kAUX_REF_EVENT:
            pr_at = '@'+str(d_resp['tg_user_at_prom'])
            rf_at = '@'+str(d_resp['tg_user_at_ref'])
            str_live = "joined the group" if d_resp['new_is_active'] else "left the group"
            tot_pts = d_resp['new_total_pts']
            # await update.message.reply_text(f"Referral points update ...\n referral {rf_at} {str_live}\n promotor {pr_at} total pts: {tot_pts}")
            await context.bot.send_message(chat_id=update.chat_member.chat.id, text=f"Referral points update ...\n referral {rf_at} {str_live}\n promotor {pr_at} total pts: {tot_pts}")
        else:
            str_r = '\n '.join([str(k)+': '+str(d_resp[k]) for k in d_resp.keys() ])
            if update.message:
                await update.message.reply_text(f"'/{tg_cmd}' Executed Successfully! ...\n {str_r} ")
            elif update.chat_member:
                await context.bot.send_message(chat_id=update.chat_member.chat.id, text=f"'/{tg_cmd}' Executed Successfully! ...\n {str_r} ")
        print('\n request handler response successful!')
        
    print('', f'EXIT - {funcname} _ {get_time_now()}', cStrDivider_1, sep='\n')

# def valid_tweet_url(_tw_url):
#     # check for validate tweet url
#     keyVals = {'_tw_url':_tw_url}
#     keyVals, success = req_handler.parse_twitter_url(keyVals, '_tw_url')
#     return keyVals, success

# def used_bs_tweet_url(_keyVals):
#     success, jsonResp, dbProcResult = req_handler.execute_db_proc(_keyVals, 'TW_URL_IS_USED')
#     if success: return bool(dbProcResult[0]['is_used'])
#     else: True # db proc failes, return True (act like shill already used)

async def attempt_aux_cmd_exe(update: Update, context, _tprint=False):
    if _tprint: pprint.pprint(update.to_dict())  # Convert to dict for easier reading
    funcname = 'attempt_aux_cmd_exe'
    user = update.message.from_user if update.message else update.chat_member.from_user
    chat_id = update.message.chat_id if update.message else update.chat_member.chat.id
    uid = user.id
    uname_at = user.username if user.username else 'nil_at'
    # uname_handle = user.first_name if user.first_name else 'nil_disabled'
    # if user.last_name:
    #     uname_handle = uname_handle + ' ' + user.last_name
    uname_handle = 'handle_disabled_ref'

    # validate user has @username setup
    if uname_at == None:
        uname_at = str(uid)
    
    if USE_ALT_ACCT: 
        # uid = '1058890141'
        # uname_at = 'laycpirates'
        uid = '6919802491'
        uname_at = 'fricardooo'

    # handle new group members
    if update.chat_member and update.chat_member.new_chat_member:
        print('GO - update.chat_member and update.chat_member.new_chat_member')
        # Check if the user joined via an invite link
        if update.chat_member.invite_link:
            invite_link = update.chat_member.invite_link.invite_link
            # Log or process the invite link used
            print(f"User @{uname_at} joined using invite link: {invite_link}")
            aux_inp_split = ['/'+req_handler.kAUX_REF_EVENT, str(uid), uname_at, uname_handle, str(chat_id), 1, invite_link] # 1 == is_join = true
            context.user_data['inp_split'] = list(aux_inp_split)
            await cmd_exe(update, context, aux_cmd=True)
        if update.chat_member.new_chat_member.status in ['left','kicked']:
            print(f"User @{uname_at} left the group")
            aux_inp_split = ['/'+req_handler.kAUX_REF_EVENT, str(uid), uname_at, uname_handle, str(chat_id), 0, '-1'] # 0 == is_join = false; -1 = no invite link
            context.user_data['inp_split'] = list(aux_inp_split)
            await cmd_exe(update, context, aux_cmd=True)

    print('', f'EXIT - {funcname} _ {get_time_now()}', cStrDivider_1, sep='\n')

async def log_activity(update: Update, context):
    global USER_MSG_CNT, REF_MSG_CNT_REQ
    _tprint = True
    print('checking requirements for attempt_aux_cmd_exe')
    if update.message != None:
        print('ENTER - if update.message != None:')
        chat_type = str(update.message.chat.type)
        chat_id = update.message.chat_id
        user = update.message.from_user
        uid = str(user.id)
        usr_at_name = f'@{user.username}' if user.username else 'nil_at'
        usr_handle = user.first_name
        inp = update.message.text
        lst_user_data = [uid, usr_at_name, usr_handle]
        lst_chat_data = [chat_id, chat_type]

        # check if user msg count is less then req for ref points
        #  if so, incrememnt msg count and check if now meets req
        #   if so, then exe attempt_aux_cmd_exe w/ OG saved 'Update' & 'CallbackContext'
        if uid in USER_MSG_CNT.keys() and USER_MSG_CNT[uid][0] < REF_MSG_CNT_REQ:
            USER_MSG_CNT[uid] = (USER_MSG_CNT[uid][0] + 1, USER_MSG_CNT[uid][1], USER_MSG_CNT[uid][2])
            if USER_MSG_CNT[uid][0] >= REF_MSG_CNT_REQ:
                await attempt_aux_cmd_exe(USER_MSG_CNT[uid][1], USER_MSG_CNT[uid][2], True)
        elif uid in USER_MSG_CNT.keys():
            print(f'uid: {uid} msg cnt > REF_MSG_CNT_REQ ... ref pts should be logged already')
        else:
            print(f'uid: {uid} not found in USER_MSG_CNT ... doing nothing')
        print(f'{get_time_now()} _ action: {lst_user_data}, {lst_chat_data} _ msgCnt: {USER_MSG_CNT[uid][0] if uid in USER_MSG_CNT else -1}')

    elif update.chat_member != None:
        # await attempt_aux_cmd_exe(update, context, True)
        print('ENTER - elif update.chat_member != None:')
        uid = str(update.chat_member.from_user.id)
        IGNORED_BOTS = ['7065258035']
        if uid in IGNORED_BOTS:
            print(f'... ignoring uid: {uid}')
            return
        
        # if leaving, process leaving to DB
        if update.chat_member.new_chat_member.status in ['left','kicked']:
            await attempt_aux_cmd_exe(update, context, True)
        else: # else joining, process joining via msg cnt tracking
            if _tprint: pprint.pprint(update.to_dict())  # Convert to dict for easier reading        
            # check if user has msg cnt entry or not (ie. re-joining or joining)
            #  and store 'update' data for use in msg cnt tracking
            if uid not in USER_MSG_CNT.keys(): print(f'uid: {uid} joined... starting msg cnt = 0')
            else: print(f'uid: {uid} re-joined... re-starting msg cnt = 0')
            USER_MSG_CNT[uid] = (0, update, context)
    else:
        print(f'{get_time_now()} _ action : found .message & .chat_member == None; returning')

async def test(update: Update, context):
    funcname = 'test'
    print(f'\nENTER - {funcname}\n')
    await context.bot.send_message(chat_id=update.message.chat_id, text="test successful sowl")

async def help(update, context):
    funcname = 'help'
    print(f'\nENTER - {funcname}\n')
    await update.message.reply_text(BOT_INFO)

def main():
    # global TOKEN
    # create dispatcher with TG bot token
    dp = Application.builder().token(TOKEN).build()

    # Register command handlers
    dp.add_handler(CommandHandler("start", help))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("sowl", help))
    dp.add_handler(CommandHandler("test", test))
    dp.add_handler(CallbackQueryHandler(btn_option_selects))

    # register all commands -> from req_handler.DICT_CMD_EXE.keys()
    for str_cmd in LST_TG_CMDS:
        dp.add_handler(CommandHandler(str_cmd, cmd_handler))
        lst_params = req_handler.DICT_CMD_EXE[str_cmd][1]
        print(f'added cmd: {str_cmd}: {lst_params}')
        # print(f'{str_cmd} - ')

    # Add message handler for ALL messages
    #   ref: https://docs.python-telegram-bot.org/en/stable/telegram.ext.filters.html#filters-module
    dp.add_handler(MessageHandler(filters.ALL, log_activity))

    # Add handler for ChatMember updates
    dp.add_handler(ChatMemberHandler(log_activity, ChatMemberHandler.CHAT_MEMBER))
    

    print('added handler ALL: log_activity')

    # Start the Bot
    print('\nbot running ...\n')
    # dp.run_polling(drop_pending_updates=True)
    # Specify allowed updates
    dp.run_polling(drop_pending_updates=True, allowed_updates=['message', 'chat_member', 'callback_query'])


    # allowed_updates = [
    #     'message',                  # Allows your bot to receive new messages sent by users.
    #     'edited_message',           # Allows your bot to receive edited messages.
    #     'channel_post',             # Allows your bot to receive new messages sent in channels.
    #     'edited_channel_post',      # Allows your bot to receive edited messages sent in channels.
    #     'callback_query',           # Allows your bot to receive callback queries from inline keyboards or inline buttons.
    #     'inline_query',             # Allows your bot to receive inline queries from users.
    #     'chosen_inline_result',     # Allows your bot to receive chosen inline results from users.
    #     'poll',                     # Allows your bot to receive updates related to polls.
    #     'poll_answer'               # Allows your bot to receive poll answers from users.
    # ]    

#------------------------------------------------------------#
#   DEFAULT SUPPORT                                          #
#------------------------------------------------------------#
READ_ME = f'''
    *DESCRIPTION*
        SOWL referral bot.
        CMDs:
            /gen_ref_link
            /show_my_referrals
            /show_leaders
            <aux_referral_event>

    *NOTE* INPUT PARAMS...
        nil
        
    *EXAMPLE EXECUTION*
        $ python3 {__filename} -<nil> <nil>
        $ python3 {__filename}
'''

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

def wait_sleep(wait_sec : int, b_print=True, bp_one_line=True): # sleep 'wait_sec'
    print(f'waiting... {wait_sec} sec')
    for s in range(wait_sec, 0, -1):
        if b_print and bp_one_line: print(wait_sec-s+1, end=' ', flush=True)
        if b_print and not bp_one_line: print('wait ', s, sep='', end='\n')
        time.sleep(1)
    if bp_one_line and b_print: print() # line break if needed
    print(f'waiting... {wait_sec} sec _ DONE')

def get_time_now(dt=True):
    if dt: return '['+datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[0:-4]+']'
    return '['+datetime.now().strftime("%H:%M:%S.%f")[0:-4]+']'

def read_cli_args():
    print(f'\nread_cli_args...\n # of args: {len(sys.argv)}\n argv lst: {str(sys.argv)}')
    for idx, val in enumerate(sys.argv): print(f' argv[{idx}]: {val}')
    print('read_cli_args _ DONE\n')
    return sys.argv, len(sys.argv)

if __name__ == "__main__":
    ## start ##
    RUN_TIME_START = get_time_now()
    print(f'\n\nRUN_TIME_START: {RUN_TIME_START}\n'+READ_ME)
    lst_argv_OG, argv_cnt = read_cli_args()
    
    ## exe ##
    try:
        # select to use prod bot or dev bot
        inp = input('\nSelect TG bot to use:\n  0 = @sowl_refer_bot \n  1 = @sowl_test_bot \n  > ')
        USE_PROD_TG = True if inp == '0' else False
        print(f'  input = {inp} _ USE_PROD_TG = {USE_PROD_TG}')
        if USE_PROD_TG:
            inp = input('\n Select PROD_CHAT_ID to use:\n   0 = TG group: test_sowl_refer_bot \n   1 = TG group: $SOWL🦉 ZONE \n   > ')
            PROD_CHAT_ID = PROD_CHAT_ID_0 if inp == '0' or inp == '' else PROD_CHAT_ID_1
            print(f'   input = {inp} _ PROD_CHAT_ID = {PROD_CHAT_ID}')

        inp = input('\nUse alt tg_user_id for testing (USE_ALT_ACCT)? [y/n]:\n  > ')
        USE_ALT_ACCT = True if inp.lower() == 'y' or inp.lower() == '1' else False
        print(f'  input = {inp} _ USE_ALT_ACCT = {USE_ALT_ACCT}')

        inp = input('\nAllow DMs to this bot? (ALLOW_DMS)? [y/n]:\n  > ')
        ALLOW_DMS = True if inp.lower() == 'y' or inp.lower() == '1' else False
        print(f'  input = {inp} _ ALLOW_DMS = {ALLOW_DMS}')

        set_tg_token()  
        print(f'\nTelegram TOKEN: {TOKEN}')
        print(f'USE_PROD_TG: {USE_PROD_TG}')
        print(f'PROD_CHAT_ID: {PROD_CHAT_ID}')
        print(f'USE_ALT_ACCT: {USE_ALT_ACCT}')
        print(f'ALLOW_DMS: {ALLOW_DMS}')
        main()
    except Exception as e:
        print_except(e, debugLvl=DEBUG_LVL)
    
    ## end ##
    print(f'\n\nRUN_TIME_START: {RUN_TIME_START}\nRUN_TIME_END:   {get_time_now()}\n')

print('', cStrDivider, f'# END _ {__filename}', cStrDivider, sep='\n')

