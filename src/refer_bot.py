__fname = 'refer_bot' # model: trinity_boy.py
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
cStrDivider_1 = '#----------------------------------------------------------------#'
print('', cStrDivider, f'GO _ {__filename} -> starting IMPORTs & declaring globals', cStrDivider, sep='\n')

#------------------------------------------------------------#
#   IMPORTS                                                  #
#------------------------------------------------------------#
# import random, 
from _env import env
import time, os, traceback, sys, json, pprint
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext

import req_handler

# Define the timestamp representing the bot's last online time
last_online_time = time.time()  # Initialize with current time

#------------------------------------------------------------#
#   GLOBALS                                                  #
#------------------------------------------------------------#
# constants
DEBUG_LVL = 3
LST_TG_CMDS = list(req_handler.DICT_CMD_EXE.keys())
WHITELIST_CHAT_IDS = [
    '-1002041092613', # $BearShares
    '-1002049491115', # $BearShares - testing
    # '-4139183080', # ?
    '-1001941928043', # TeddyShares - testing
    '-1002375576767', # tg group: testing_sowl_refer
    ]
BLACKLIST_TEXT = [
    'smart vault', 'smart-vault', 'smart_vault', # @JstKidn
    ]

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
        print("*** WARNING ***: non-whitelist TG group trying to use the bot; sending deny message...")
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

# # Function to handle new group members
# def member_joined(update: Update, context: CallbackContext):
#     if update.chat_member.new_chat_member:
#         # Check if the user joined via an invite link
#         if update.chat_member.invite_link:
#             invite_link = update.chat_member.invite_link.invite_link
#             # Log or process the invite link used
#             print(f"User {update.chat_member.new_chat_member.user.first_name} joined using invite link: {invite_link}")
#         else:
#             print(f"User {update.chat_member.new_chat_member.user.first_name} joined the group.")


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
    uname_at = user.username
    uname_handle = user.first_name
    if user.last_name:
        uname_handle = user.first_name + ' ' + user.last_name
    inp_split = list(update.message.text.split())

    # parse about @user (if user simply hit enter from cmd description list in TG chat)
    if '@' in inp_split[0]: inp_split[0] = inp_split[0].split('@')[0]

    # check if TG group is whitelisted to use (prints group info and deny)
    #   NOTE: at this point, inp_split[0] is indeed a valid command
    print(f'handling cmd: '+inp_split[0])
    print(f"chat_type: {chat_type}")
    tg_cmd = inp_split[0][1::] # parses out the '/'

    # fail: if not in WHITELIST_CHAT_IDS and not a DM
    valid_chat, str_deny = is_valid_chat_id(str(_chat_id), group_name, uname_at, uname_handle)
    # print(valid_cmd, valid_chat, chat_type, str_deny, sep='\n')
    if not valid_chat and not is_dm:
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
            # insert after /cmd ['</cmd>','user_id','user_at','user_handle','<tg_user_group_url>']
            inp_split.insert(1, uid) 
            inp_split.insert(2, uname_at) # left off here ....
            inp_split.insert(3, uname_handle)

            # generate random unique invite link
            chat = update.message.chat
            invite_link = await context.bot.create_chat_invite_link(chat_id=chat.id)
            inp_split.insert(4, invite_link['invite_link'])

        if tg_cmd == req_handler.kSHOW_USR_REF_HIST: # proc: GET_PROMOTOR_INFO
            # insert after /cmd ['</cmd>','<start_idx>','<count>','<is_desc>']
            inp_split.insert(1, uid) 
            # inp_split.insert(2, uname_at)
            # inp_split.insert(3, uname_handle)
            # pass # no params for 'gen_ref_link'

        if tg_cmd == req_handler.kSHOW_LEADERS: # proc: GET_LEADER_BOARD
            inp_split.insert(3, uname_handle)
            # pass # no params for 'gen_ref_link'

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

async def cmd_exe(update: Update, context: CallbackContext, aux_cmd=False):
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
        d_resp = response_dict['PAYLOAD']['result_arr'][0]
        if tg_cmd == req_handler.kREG_USER:
            # shill_id = d_resp['shill_id']
            
            # inc_ = ['post_url','shill_id','pay_usd','is_approved','tg_user_at_inp','is_paid','shill_plat','shill_type']
            # d_resp['tg_user_at_inp'] = '@'+str(d_resp['tg_user_at_inp'])
            # str_r = '\n '.join([str(k)+': '+str(d_resp[k]) for k in d_resp.keys() if str(k) in inc_])
            # await update.message.reply_text(f"Info for shill id: {shill_id} ...\n {str_r}")
            new_ref_link = d_resp['new_tg_user_group_url']
            str_r = '\n '.join([str(k)+': '+str(d_resp[k]) for k in d_resp.keys() ])
            await update.message.reply_text(f"Registration successful!\nYour referral link: {new_ref_link} ...\n {str_r}")
        else:
            str_r = '\n '.join([str(k)+': '+str(d_resp[k]) for k in d_resp.keys() ])
            await update.message.reply_text(f"'/{tg_cmd}' Executed Successfully! ...\n {str_r} ")
        
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

async def attempt_aux_cmd_exe(update: Update, context):
    funcname = 'attempt_aux_cmd_exe'
    user = update.message.from_user
    uid = user.id
    uname_at = user.username
    uname_handle = 'nil_disabled'

    # validate user has @username setup
    if uname_at == None:
        print(f'{get_time_now()} __ action : found uname_at == None; skip attempt_aux_cmd_exe')
        return
    
    if USE_ALT_ACCT: 
        # uid = '1058890141'
        # uname_at = 'laycpirates'
        uid = '6919802491'
        uname_at = 'fricardooo'

    # check if message text 'could' contain a tweet url
    inp = update.message.text
    if 'x.com' not in inp and 'twitter.com' not in inp: return

    print(f'{get_time_now()} __ action : found potential tweet url')
    print(cStrDivider_1, f'ENTER - {funcname} _ {get_time_now()}', sep='\n')

    # # traverse through string, check for valid tweet url, 
    # #   if valid tweet, check db to see if its been used yet
    # #   if not used yet, generate aux_inp_split & attempt /register & /submit
    # inp_split = list(update.message.text.split())
    # for str_ in inp_split:
    #     keyVals, valid_tweet = valid_tweet_url(str_)
    #     if valid_tweet:
    #         tweet_is_used = used_bs_tweet_url(keyVals) # db check for used reg or shill
    #         print(f'tweet_is_used: {tweet_is_used}')
    #         if not tweet_is_used:
    #             valid_shill, msg = req_handler.valid_trinity_tweet(str_, ['@BearSharesX']) # net request
    #             valid_reg, msg = req_handler.valid_trinity_tweet(str_, ['@BearSharesX', 'Trinity', 'register']) # net request
    #             print(f'valid_shill: {valid_shill}')
    #             if valid_shill:
    #                 aux_inp_split = ['/'+req_handler.kSUBMIT_SHILL, uid, uname_at, str_]
    #                 context.user_data['inp_split'] = list(aux_inp_split)
    #                 await cmd_exe(update, context, aux_cmd=True)
                
    #             print(f'valid_reg: {valid_reg}')
    #             if valid_reg:
    #                 aux_inp_split = ['/'+req_handler.kSHILLER_REG, uid, uname_at, uname_handle, '0x0', str_]
    #                 context.user_data['inp_split'] = list(aux_inp_split)
    #                 await cmd_exe(update, context, aux_cmd=True)
    #             print(f'valid_shill: {valid_shill}')
    #             print(f'valid_reg: {valid_reg}')

    print('', f'EXIT - {funcname} _ {get_time_now()}', cStrDivider_1, sep='\n')

async def log_activity(update: Update, context):
    if update.message == None:
        print(f'{get_time_now()} _ action : found .message == None; returning')
        return

    chat_type = str(update.message.chat.type)
    chat_id = update.message.chat_id
    user = update.message.from_user
    uid = str(user.id)
    usr_at_name = f'@{user.username}'
    usr_handle = user.first_name
    inp = update.message.text
    lst_user_data = [uid, usr_at_name, usr_handle]
    lst_chat_data = [chat_id, chat_type]
    print(f'{get_time_now()} _ action: {lst_user_data}, {lst_chat_data}')
    
    # if not USE_PAYOUT_ONLY and update.message.text: await attempt_aux_cmd_exe(update, context)
    if update.message.text: await attempt_aux_cmd_exe(update, context)

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
    print('added handler ALL: log_activity')

    # Start the Bot
    print('\nbot running ...\n')
    dp.run_polling(drop_pending_updates=True)


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

        inp = input('\nUse alt tg_user_id for testing (USE_ALT_ACCT)? [y/n]:\n  > ')
        USE_ALT_ACCT = True if inp.lower() == 'y' or inp.lower() == '1' else False
        print(f'  input = {inp} _ USE_ALT_ACCT = {USE_ALT_ACCT}')

        set_tg_token()  
        print(f'\nTelegram TOKEN: {TOKEN}')
        print(f'USE_PROD_TG: {USE_PROD_TG}')
        print(f'USE_ALT_ACCT: {USE_ALT_ACCT}')
        main()
    except Exception as e:
        print_except(e, debugLvl=DEBUG_LVL)
    
    ## end ##
    print(f'\n\nRUN_TIME_START: {RUN_TIME_START}\nRUN_TIME_END:   {get_time_now()}\n')

print('', cStrDivider, f'# END _ {__filename}', cStrDivider, sep='\n')

