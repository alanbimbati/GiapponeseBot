import gspread
from oauth2client.service_account import ServiceAccountCredentials
from GiappoClass import GiappoBot
from telebot import types
from telebot import TeleBot
import time


BOT_TOKEN = "1359089063:AAEig5IHLo_sRmyoGEzPbEv0PdylyyIglAo"
CANALE_LOG = "-1001469821841"
bot = TeleBot(BOT_TOKEN)


hideBoard = types.ReplyKeyboardRemove()  
admin = ['62716473']
autorizzati = ['391473447', '62716473']
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Studio Giapponese").sheet1
g = GiappoBot(BOT_TOKEN, CANALE_LOG, sheet)  

@bot.message_handler(commands=['start'])
def Start(message):
    g.CreateUtente(message)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    scelte = ['🇮🇹 ItaToRomanji 🇯🇵', '🇮🇹 ItaToKatana 🇯🇵', '🇯🇵 RomanjiToIta 🇮🇹', '🇯🇵 KatanaToIta 🇮🇹', 'TuttoRandom', '👤 Scheda personale']
    if str(message.chat.id) in admin:
        scelte.append("Backup")
        scelte.append("Restore")
    
    for scelta in scelte:
        types.KeyboardButton(scelta)
        markup.add(scelta)


    msg = bot.reply_to(message, "Quale operazione vuoi svolgere?", reply_markup=markup)
    bot.register_next_step_handler(msg, Menu)


def Menu(message):  
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    indizi = ['💰 50: Metà parola', '💰 50: Skip']
    for indizio in indizi:
        types.KeyboardButton(indizio)
        markup.add(indizio)

    if "ItaToRomanji" in message.text:     
        g.ItaToRomanji()
        msg = bot.reply_to(message, "Traduci \""+g.domanda+"\" in" + g.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "ItaToKatana" in message.text:     
        g.ItaToKatana()
        msg = bot.reply_to(message, "Traduci \""+g.domanda+"\" in" + g.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "RomanjiToIta" in message.text:     
        g.RomanjiToIta()
        msg = bot.reply_to(message, "Traduci \""+g.domanda+"\" in" + g.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "KatanaToIta" in message.text:     
        g.KatanaToIta()
        msg = bot.reply_to(message, "Traduci \""+g.domanda+"\" in" + g.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "TuttoRandom" in message.text:
        g.TuttoRandom()
        msg = bot.reply_to(message, "Traduci \""+g.domanda+"\" in" + g.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "Scheda" in message.text:
        bot.reply_to(message, g.printMe(message.chat.id),reply_markup=hideBoard)
        time.sleep(2)
        Start(message)
    elif "Backup" in message.text and message.chat.id in admin:
        g.Backup()
        Start(message)
    elif "Restore" in message.text:
        sheet = client.open("Studio Giapponese").sheet1
        g = GiappoBot(BOT_TOKEN, CANALE_LOG, sheet)  
        Start(message)
    elif message.text == "ultimo":
        sheet = client.open("Studio Giapponese").sheet1

        print(sheet.cell(len(sheet.row_values(),1)).values())
    else:
        g.clean()

    print(g.risposta)


def Answer(message):
    print("answer")
    chatid = message.chat.id
    level = g.getUtente(chatid).livello
    if "💰" in message.text:
        if "Metà parola" in message.text:
            meta = g.buyHalfWord(message.chat.id)
            msg = bot.reply_to(message, meta) 
            bot.register_next_step_handler(msg, Answer)
        elif "Skip" in message.text:
            Start(message)
        
    elif message.text==g.risposta:
        g.CorrectAnswer(chatid)
        current_level = g.me(chatid).livello 
        if current_level != level:
            bot.send_message(chatid, "Complimenti! Sei passato/a al livello "+current_level, reply_markup=hideBoard)
        else:
            bot.send_message(chatid, "Complimenti! Hai ottenuto 10 exp!"+current_level, reply_markup=hideBoard)



    else:
        bot.send_message(chatid, "Mi dispiace, la risposta era "+g.risposta, reply_markup=hideBoard)

    Start(message)


bot.infinity_polling()