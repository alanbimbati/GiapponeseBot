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

@bot.message_handler(commands=['start'])
def Start(message):
    g = GiappoBot(BOT_TOKEN, CANALE_LOG)  
    g.CreateUtente(message)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    scelte = ['🇮🇹 ItaToRomanji 🇯🇵', '🇮🇹 ItaToKatana 🇯🇵', '🇯🇵 RomanjiToIta 🇮🇹', '🇯🇵 KatanaToIta 🇮🇹', '🎲 TuttoRandom', '👤 Scheda personale']
    if str(message.chat.id) in admin:
        scelte.append("Backup")
        scelte.append("Restore")
    
    for scelta in scelte:
        types.KeyboardButton(scelta)
        markup.add(scelta)


    msg = bot.reply_to(message, "Quale operazione vuoi svolgere?", reply_markup=markup)
    bot.register_next_step_handler(msg, Menu)


def Menu(message):  
    g = GiappoBot(BOT_TOKEN, CANALE_LOG)  
    chatid = message.chat.id

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    indizi = ['💰 50: Metà parola', '💰 50: Skip']
    for indizio in indizi:
        types.KeyboardButton(indizio)
        markup.add(indizio)

    if "ItaToRomanji" in message.text:     
        g.ItaToRomanji(chatid)
        utente = g.getUtente(chatid)
        msg = bot.reply_to(message, "Traduci \""+utente.domanda+"\" in " + utente.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "ItaToKatana" in message.text:     
        g.ItaToKatana(chatid)
        utente = g.getUtente(chatid)
        msg = bot.reply_to(message, "Traduci \""+utente.domanda+"\" in " + utente.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "RomanjiToIta" in message.text:     
        g.RomanjiToIta(chatid)
        utente = g.getUtente(chatid)

        msg = bot.reply_to(message, "Traduci \""+utente.domanda+"\" in " + utente.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "KatanaToIta" in message.text:     
        g.KatanaToIta(chatid)
        utente = g.getUtente(chatid)
        msg = bot.reply_to(message, "Traduci \""+utente.domanda+"\" in " + utente.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "TuttoRandom" in message.text:
        g.TuttoRandom(chatid)
        utente = g.getUtente(chatid)
        msg = bot.reply_to(message, "Traduci \""+utente.domanda+"\" in " + utente.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "Scheda" in message.text:
        bot.reply_to(message, g.printMe(chatid),reply_markup=hideBoard)
        time.sleep(2)
        Start(message)
    elif "Backup" in message.text and chatid in admin:
        g.Backup()
        Start(message)
    elif "Restore" in message.text:
        g.populaDB()  
        Start(message)
        
def Answer(message):
    print("answer")
    g = GiappoBot(BOT_TOKEN,CANALE_LOG)
    chatid = message.chat.id
    utente = g.getUtente(chatid)
    level = utente.livello
    if "💰" in message.text:
        if "Metà parola" in message.text:
            meta = g.buyHalfWord(chatid)
            msg = bot.reply_to(message, meta) 
            bot.register_next_step_handler(msg, Answer)
        elif "Skip" in message.text:
            meta = g.skip(chatid)
            msg = bot.reply_to(message, meta)           
    elif message.text==utente.risposta:
        g.CorrectAnswer(chatid)
        current_level = utente.livello 
        if current_level != level:
            bot.send_message(chatid, "Complimenti! Sei passato/a al livello "+str(current_level), reply_markup=hideBoard)
        else:
            bot.send_message(chatid, "Complimenti! Hai ottenuto 10 exp!", reply_markup=hideBoard)
    else:
        bot.send_message(chatid, "Mi dispiace, la risposta era "+utente.risposta, reply_markup=hideBoard)

    Start(message)


bot.infinity_polling()