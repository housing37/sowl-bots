__fname = 'env'
__filename = __fname + '.py'
cStrDivider = '#================================================================#'
cStrDivider_1 = '#----------------------------------------------------------------#'
print('', cStrDivider, f'GO _ {__filename} -> starting IMPORTs & declaring globals', cStrDivider, sep='\n')
#============================================================================#
#============================================================================#
## .env support
import os
from read_env import read_env

try:
    #ref: https://github.com/sloria/read_env
    #ref: https://github.com/sloria/read_env/blob/master/read_env.py
    read_env() # recursively traverses up dir tree looking for '.env' file
except:
    print("#==========================#")
    print(" ERROR: no .env files found ")
    print("#==========================#")

# db support
dbHost = os.environ['DB_HOST']
dbName = os.environ['DB_DATABASE']
dbUser = os.environ['DB_USERNAME']
dbPw = os.environ['DB_PASSWORD']

# req_handler support
LST_KEYS_PLACEHOLDER = []

# openAI
OPENAI_KEY = os.environ['OPENAI_KEY']

# telegram
TOKEN_sowl = os.environ['TG_TOKEN_SOWL'] # @sowl_refer_bot
#============================================================================#
