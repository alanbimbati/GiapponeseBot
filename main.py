#!/home/alan/MEGAsync/GiapponeseBot/python/bin/python3
from GiappoClass import GiappoBot
from telebot import types
from telebot import TeleBot
import time

from sqlalchemy         import create_engine
from sqlalchemy.orm     import sessionmaker

from model import Utente,Word, db_connect, create_table

# BOT_TOKEN = "1359089063:AAEig5IHLo_sRmyoGEzPbEv0PdylyyIglAo" #Giappo
BOT_TOKEN = "1090156197:AAGIWGYMqK_tfjsTHoAdZ3xby1lZ6GWy8Q8" #BimbatiHouse
CANALE_LOG = "-1001469821841"
bot = TeleBot(BOT_TOKEN)


hideBoard = types.ReplyKeyboardRemove()  
admin = {}
admin['Alan'] = '62716473'
admin['Lorena'] = '391473447'

def authorize(message):
    flag = 0
    for superuser in admin:         
        if str(message.chat.id) in admin[superuser]:
            flag = 1
    if flag ==0:
        bot.reply_to(message, "Non sei autorizzato ad utilizzare questo bot")
    return flag 

def error(message, error):
    print(str(error))
    bot.send_message(CANALE_LOG, str(error)+"\n#Error")
    bot.reply_to(message, "😔 C'è stato un problema...riavviamo con /start", reply_markup=hideBoard)

@bot.message_handler(commands=['start'])
def Start(message):
    if message.chat.type == "private":
        g = GiappoBot(BOT_TOKEN, CANALE_LOG)  
        g.CreateUtente(message)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

        markup.add('🇮🇹 ItaToRomaji 🇯🇵', '🇮🇹 ItaToKatana 🇯🇵')
        markup.add('🇯🇵 RomajiToIta 🇮🇹', '🇯🇵 KatanaToIta 🇮🇹')
        markup.add('️#️⃣ Tag', '🎲 TuttoRandom')
        markup.add('👤 Scheda personale','🏆 Classifica')

        if authorize(message):
            markup.add('Backup','Restore')

        msg = bot.reply_to(message, "Cosa vuoi fare?", reply_markup=markup)
        bot.register_next_step_handler(msg, Menu)
    else:
        bot.reply_to(message, "Mi dispiace, questo bot funziona solo in privato")

@bot.callback_query_handler(func=lambda call: "Menu" in call.data)
def Menu(message): 
    try: 
        # SQLalchemy session
        engine = db_connect()
        create_table(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        g = GiappoBot(BOT_TOKEN, CANALE_LOG)  
        chatid = message.chat.id

        words = session.query(Word).all()

        if "ItaToRomaji" in message.text:     
            g.ItaToRomanji(chatid, words)
            Question(message, chatid)
        elif "ItaToKatana" in message.text:     
            g.ItaToKatana(chatid, words)
            Question(message, chatid)
        elif "RomajiToIta" in message.text:     
            g.RomanjiToIta(chatid, words)
            Question(message, chatid)
        elif "KatanaToIta" in message.text:     
            g.KatanaToIta(chatid, words)
            Question(message, chatid)
        elif "Tag" in message.text:
            tags = engine.execute("SELECT tag FROM WORD").unique()
            markup_tags = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            for tag in tags:
                tag = str(tag).replace("(","").replace(")","").replace("'","").replace(",","")
                markup_tags.add(tag)
            msg = bot.reply_to(message, "Scegli il tag", reply_markup=markup_tags)
            bot.register_next_step_handler(msg, Tag)
        elif "TuttoRandom" in message.text:
            g.TuttoRandom(chatid, words)
            Question(message, chatid)
        elif "Scheda" in message.text:
            bot.reply_to(message, g.printMe(chatid),reply_markup=hideBoard)
            time.sleep(1)
            Start(message)
        elif "classifica" in message.text.lower():
            utenti = g.classifica()
            if len(utenti)>=1:
                classifica = "🥇 "+utenti[0].nome+" Lv."+str(utenti[0].livello)+"Exp. "+str(utenti[0].exp)+"\n"
            if len(utenti)>=2:
                classifica = classifica + "🥈 "+utenti[1].nome+" Lv."+str(utenti[1].livello)+"Exp. "+str(utenti[1].exp)+"\n"
            if len(utenti)>=3:
                classifica = classifica + "🥉 "+utenti[2].nome+" Lv."+str(utenti[2].livello)+"Exp. "+str(utenti[2].exp)+"\n"
            bot.send_message(chatid, classifica)
            Start(message)

        if authorize(message):
            if "Backup" in message.text:
                doc = open('giappo.db', 'rb')
                bot.send_document(chatid, doc, caption="#database #backup", reply_markup=hideBoard)
                doc.close()
                Start(message)
            if "Restore" in message.text:
                g.populaDB()  
                Start(message)
        session.close()
    except Exception as e:
        error(message, e)


def Tag(message):
    chatid = message.chat.id
    g = GiappoBot(BOT_TOKEN, CANALE_LOG)
    g.domandaTag(chatid, message.text)
    Question(message, chatid)


def Question(message, chatid):
    engine = db_connect()
    create_table(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    indizi = ['💰 50: Metà parola', '💰 50: Skip']
    for indizio in indizi:
        markup.add(indizio)
    utente = session.query(Utente).filter_by(id_telegram = chatid).first()  
    msg = bot.reply_to(message, "Traduci \""+utente.domanda+"\" in " + utente.traduci_in, reply_markup=markup)
    bot.register_next_step_handler(msg, Answer)

    session.close()

def Answer(message):
    print("answer")

    try:
        g = GiappoBot(BOT_TOKEN,CANALE_LOG)
        chatid = message.chat.id
        utente = g.getUtente(chatid)
        risposta_esatta = cleanString(utente.risposta)
        risposta_data   = cleanString(message.text)

        level = utente.livello
        if "💰" in message.text:
            if "Metà parola" in risposta_data:
                meta = g.buyHalfWord(chatid)
                msg = bot.reply_to(message, meta) 
                bot.register_next_step_handler(msg, Answer)
            elif "Skip" in risposta_data:
                meta = g.skip(chatid)
                msg = bot.reply_to(message, meta)  
                Start(message)
        elif risposta_data==risposta_esatta:
            g.CorrectAnswer(chatid)
            current_level = utente.livello 
            if current_level != level:
                bot.send_message(chatid, "🎉 Complimenti! Sei passato/a al livello "+str(current_level), reply_markup=hideBoard)
            else:
                bot.send_message(chatid, "🎉 Complimenti hai risposto giusto!!", reply_markup=hideBoard)
            Start(message)

        else:
            g.WrongAnswer(chatid)
            bot.send_message(chatid, "Mi dispiace, la risposta era "+utente.risposta, reply_markup=hideBoard)
            Start(message)
    except Exception as e:
        error(message, e)

bot.infinity_polling()


def cleanString(string):
    return string.replace("\n","").replace(",","").replace(".","")