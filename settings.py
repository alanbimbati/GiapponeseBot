admin = {}
admin['Alan']   = '62716473'


CANALE_LOG = '-1001469821841'

TEST = 0
api_id = 22694466
api_hash = 'c6dcb5fc1fa57a29085d4ecdaddb16d9'
RASPI_TOKEN = '1722321202:AAH0ejhh_A5kLePfD9bt9CGYBXZbE9iA6AU'
GIAPPO_TOKEN = '1359089063:AAEig5IHLo_sRmyoGEzPbEv0PdylyyIglAo'
if TEST:
    BOT_TOKEN = RASPI_TOKEN #Raspi
    #GRUPPO_AROMA = -707606080 #TEST
    GRUPPO_AROMA = -1001721979634 #TEST
else:
    BOT_TOKEN = GIAPPO_TOKEN #aROMa
    GRUPPO_AROMA= -1001457029650 #aROMa


from telebot import TeleBot
from telebot import types
bot = TeleBot(BOT_TOKEN, threaded=False)
hideBoard = types.ReplyKeyboardRemove()  