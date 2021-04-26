from GiappoClass import GiappoBot
from telebot import types
from telebot import TeleBot
import time

from sqlalchemy         import create_engine
from sqlalchemy.orm     import sessionmaker

from model import Utente,Word, db_connect, create_table

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
    scelte.append("🏆 Classifica")
    if str(message.chat.id) in admin:
        scelte.append("Backup")
        scelte.append("Restore")
    
    for scelta in scelte:
        types.KeyboardButton(scelta)
        markup.add(scelta)


    msg = bot.reply_to(message, "Quale operazione vuoi svolgere?", reply_markup=markup)
    bot.register_next_step_handler(msg, Menu)


def Menu(message):  
    engine = db_connect()
    create_table(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    g = GiappoBot(BOT_TOKEN, CANALE_LOG)  
    chatid = message.chat.id

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    indizi = ['💰 50: Metà parola', '💰 50: Skip']
    for indizio in indizi:
        types.KeyboardButton(indizio)
        markup.add(indizio)

    if "ItaToRomanji" in message.text:     
        g.ItaToRomanji(chatid)
        utente = session.query(Utente).filter_by(id_telegram = chatid).first()  
        msg = bot.reply_to(message, "Traduci \""+utente.domanda+"\" in " + utente.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "ItaToKatana" in message.text:     
        g.ItaToKatana(chatid)
        utente = session.query(Utente).filter_by(id_telegram = chatid).first()  
        msg = bot.reply_to(message, "Traduci \""+utente.domanda+"\" in " + utente.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "RomanjiToIta" in message.text:     
        g.RomanjiToIta(chatid)
        utente = session.query(Utente).filter_by(id_telegram = chatid).first()  
        msg = bot.reply_to(message, "Traduci \""+utente.domanda+"\" in " + utente.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "KatanaToIta" in message.text:     
        g.KatanaToIta(chatid)
        utente = session.query(Utente).filter_by(id_telegram = chatid).first() 
        msg = bot.reply_to(message, "Traduci \""+utente.domanda+"\" in " + utente.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "TuttoRandom" in message.text:
        g.TuttoRandom(chatid)
        utente = session.query(Utente).filter_by(id_telegram = chatid).first()  
        msg = bot.reply_to(message, "Traduci \""+utente.domanda+"\" in " + utente.traduci_in, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)
    elif "Scheda" in message.text:
        bot.reply_to(message, g.printMe(chatid),reply_markup=hideBoard)
        time.sleep(2)
        Start(message)
    elif "classifica" in message.text.lower():
        utenti = g.classifica()
        if len(utenti)>=1:
            classifica = "🥇 "+utenti[0].nome+" "+utenti[0].cognome+" Lv."+str(utenti[0].livello)+"\n"
        if len(utenti)>=2:
            classifica = classifica + "🥈 "+utenti[1].nome+" "+utenti[1].cognome+" Lv."+str(utenti[1].livello)+"\n"
        if len(utenti)>=3:
            classifica = classifica + "🥉 "+utenti[2].nome+" "+utenti[2].cognome+" Lv."+str(utenti[2].livello)+"\n"
        bot.send_message(chatid, classifica)
        Start(message)
    elif "Backup" in message.text and str(chatid) in admin:
        doc = open('giappo.db', 'rb')
        bot.send_document(chatid, doc, caption="#database #backup", reply_markup=hideBoard)
        doc.close()
        Start(message)
    elif "Restore" in message.text and str(chatid) in admin:
        g.populaDB()  
        Start(message)
    session.close()
    
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