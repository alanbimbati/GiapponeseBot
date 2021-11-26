#!/home/alan/MEGAsync/GiapponeseBot/python/bin/python3
#!/home/pi/Documents/Giappo/GiapponeseBot/python/bin/python3
from sqlalchemy.orm.session import Session
from GiappoClass import GiappoBot
from telebot import types
from telebot import TeleBot
import time

from sqlalchemy         import create_engine
from sqlalchemy.orm     import sessionmaker

from model import Utente,Word, db_connect, create_table

BOT_TOKEN = "1359089063:AAEig5IHLo_sRmyoGEzPbEv0PdylyyIglAo" #Giappo
# BOT_TOKEN = "1722321202:AAH0ejhh_A5kLePfD9bt9CGYBXZbE9iA6AU" #RaspiAlanBot
CANALE_LOG = "-1001469821841"
bot = TeleBot(BOT_TOKEN, threaded=False)


hideBoard = types.ReplyKeyboardRemove()  
admin = {}
admin['Alan']   = '62716473'
admin['Lorena'] = '391473447'


comandi = {}
comandi['random']       = '🎲 Domanda Casuale'
comandi['last_lv']      = '🎲 Ultimo livello'
comandi['livelli']      = '🔢 Livelli'
comandi['ItaToRomaji']  = '🇮🇹 Da Ita a Romaji 🇯🇵'
comandi['RomajiToIta']  = '🇯🇵 Da Romaji a Ita 🇮🇹'
comandi['ItaToKana']    = '🇮🇹 Da Ita a Kana 🇯🇵'
comandi['KanaToIta']    = '🇯🇵 Da Kana a Ita 🇮🇹'
comandi['Categoria']    = '#️⃣ Categoria'
comandi['profilo']      = '👤 Scheda personale'
comandi['classifica']   = '🏆 Classifica'
comandi['delete']       = '❌ Cancella Profilo'
comandi['materiale']    = '📚 Materiale di studio'

def broadcast(message):
    if authorize(message):
        engine = db_connect()
        create_table(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        people = session.query(Utente).all()
        for person in people:
            try:
                bot.send_message(person.id_telegram, message.text)
            except:
                bot.reply_to(message, "L'utente "+person.nome+" ("+str(person.id_telegram)+") non ha l'accesso al bot")

def cleanString(string):
    return string.replace("\n","").replace(",","").replace(".","").lower()

def authorize(message):
    flag = 0
    for superuser in admin:         
        if str(message.chat.id) in admin[superuser]:
            flag = 1
    return flag 

def error(message, error):
    print(str(error))
    bot.send_message(CANALE_LOG, str(error)+"\n#Error")
    bot.reply_to(message, "😔 C'è stato un problema...riavviami con /start", reply_markup=hideBoard)

def scegli_livello(utente, tipo):
    markup_lvl = types.InlineKeyboardMarkup()
    for i in range(utente.livello+1):
        lv = tipo+" Livello "+str(utente.livello-i)
        markup_lvl.add(types.InlineKeyboardButton(lv, callback_data=lv))
    return markup_lvl

@bot.callback_query_handler(func=lambda call: True and ("Livello" in call.data or "Forme" in call.data))
def SendMateriale(call):
    chatid = call.message.chat.id
    words = call.data.split()[1:]
    livello = ""
    for word in words:    
        livello = livello+word+" "
    livello = livello[:-1]
    print(livello)
    if "Materiale" in call.data:
        try:
            doc = open("Materiale/"+livello+'.pdf', 'rb')
            bot.send_document(chatid, doc, caption="Materiale di studio "+livello)
            doc.close()
        except Exception as e:
            print("Errore nel documento")
    elif "Domanda" in call.data:
        try:
            g = GiappoBot(BOT_TOKEN, CANALE_LOG)
            g.domandaLevel(chatid, livello)
            Question(call.message, chatid)
        except Exception as e:
            print("Error")



@bot.callback_query_handler(func=lambda call: True and "💰" in call.data)
def Indizi(call):
    g = GiappoBot(BOT_TOKEN, CANALE_LOG)  
    chatid = call.message.chat.id
    risposta = ""
    if "metà parola" in call.data.lower():
        risposta = g.buyHalfWord(chatid)
    elif "categoria" in call.data.lower():
        risposta = g.buyCategory(chatid)
    elif "🩸" in call.data:
        if "leggera" in call.data.lower():
            risposta = g.buyPotion(chatid, 0)
        elif "moderata" in call.data.lower():
            risposta = g.buyPotion(chatid, 1)
        elif "superiore" in call.data.lower():
            risposta = g.buyPotion(chatid, 2)
    bot.send_message(chatid, risposta)

@bot.callback_query_handler(func=lambda call: True and "Tag" in call.data)
def Tag(call):
    chatid = call.message.chat.id
    tag = call.data.split(":")[1]
    try:
        g = GiappoBot(BOT_TOKEN, CANALE_LOG)
        g.domandaTag(chatid, tag)
        Question(call.message, chatid)
    except Exception as e:
        print("Errore nel tag")


def unlock(message):
    engine = db_connect()
    create_table(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    livello = session.query(Utente).filter_by(id_telegram=message.chat.id).first().livello
    
    markup = types.ReplyKeyboardMarkup( )

    if livello>=0:
        markup.add(comandi['random'], comandi['last_lv'])
    if livello>=1:
        markup.add(comandi['livelli'])
    if livello>=2:
        markup.add(comandi['ItaToRomaji'], comandi['RomajiToIta'])
    if livello>=3:
        markup.add(comandi['ItaToKana'], comandi['KanaToIta'])
    if livello>=5:
        markup.add(comandi['Categoria'])

    markup.add(comandi['profilo'], comandi['classifica'])
    markup.add(comandi['materiale'])
    markup.add(comandi['delete'])  
    if authorize(message):
        markup.add('Backup','Restore')
        markup.add("Broadcast")  
    return markup


def createUser(message):
    chatid = message.chat.id
    engine = db_connect()
    create_table(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    utente = session.query(Utente).filter_by(id_telegram=chatid).first()
    if utente is None:
        g = GiappoBot(BOT_TOKEN, CANALE_LOG)  
        g.CreateUtente(message)

@bot.message_handler(commands=['start'])
def start(message):
    createUser(message)
    markup = unlock(message)
    welcome = "Benvenuto nel bot per poter imparare il giapponese giocando! 🇮🇹🇯🇵 \n\n✅ Rispondi correttamente alle domande, otterrai punti esperienza per passare di livello  e sbloccare nuove funzionalità, e ottenere monete da spendere.\n\n ❌ Se sbaglierai risposta perderai vita, non morire!"
    bot.send_message(message.chat.id, welcome, reply_markup=markup)
    Menu(message)

@bot.message_handler(func=lambda msg: True)
def Menu(message): 
    print("Menu")
    try: 
        # SQLalchemy session
        engine = db_connect()
        create_table(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        g = GiappoBot(BOT_TOKEN, CANALE_LOG)  
        chatid = message.chat.id

        words = session.query(Word)
        words = g.LevelFilter(chatid, words)
        utente = session.query(Utente).filter_by(id_telegram=chatid).first()

        g = GiappoBot(BOT_TOKEN, CANALE_LOG)  
        g.CreateUtente(message)
        markup = unlock(message)
       
        if "/help" == message.text:
            bot.send_message(chatid, "Benvenuto nel bot per poter imparare il giapponese giocando! 🇮🇹🇯🇵 \n\n✅ Rispondi correttamente alle domande, otterrai punti esperienza per passare di livello  e sbloccare nuove funzionalità, e ottenere monete da spendere per avere indizi.\n\n ❌ Se sbaglierai risposta guadagnerai meno punti esperienza e perderai monete)")
            bot.send_message(chatid, "Per incominciare premi /start o scrivimi /help per riavere questo messaggio")
     
        elif comandi['ItaToRomaji'] == message.text:     
            g.ItaToRomanji(chatid, words)
            Question(message, chatid)
        elif comandi['ItaToKana'] == message.text:     
            g.ItaToKana(chatid, words)
            Question(message, chatid)
        elif comandi['RomajiToIta'] == message.text:   
            g.RomanjiToIta(chatid, words)
            Question(message, chatid)
        elif comandi['KanaToIta'] == message.text:     
            g.KanaToIta(chatid, words)
            Question(message, chatid)

        elif comandi["Categoria"] == message.text:
            words = words.all()
            tags = words.tag.unique()
            markup_tags = types.InlineKeyboardMarkup()
            for tag in tags:
                tag = str(tag).replace("(","").replace(")","").replace("'","").replace(",","")
                markup_tags.add(types.InlineKeyboardButton(tag, callback_data="Categoria: "+tag))
            bot.reply_to(message, "Scegli il tag", reply_markup=markup_tags)
            
        elif comandi['livelli'] == message.text:
            markup_lvl = scegli_livello(utente, "Domanda")
            msg = bot.reply_to(message, "Scegli il livello della domanda", reply_markup=markup_lvl)

        elif comandi['last_lv'] == message.text:
            g.domandaLevel(chatid, "Livello "+str(utente.livello))
            Question(message, chatid)

        elif comandi['random'] == message.text:
            g.TuttoRandom(chatid, words)
            Question(message, chatid)

        elif comandi['profilo'] == message.text:
            bot.reply_to(message, g.printMe(chatid))
            time.sleep(0.5)

        elif comandi["classifica"] == message.text:
            utenti = g.classifica()
            classifica = ""
            for i in range(len(utenti)):
                if i==0:
                    classifica = classifica + "🥇\t"
                elif i==1:
                    classifica = classifica + "🥈\t"
                elif i==2:
                    classifica = classifica + "🥉\t"
                else:
                    classifica = classifica + str(i+1) + "\t"
                classifica = classifica + utenti[i].nome+"\tLv."+str(utenti[i].livello)+"\tExp. "+str(utenti[i].exp)+"\n"
            bot.send_message(chatid, classifica, reply_markup=markup)

        elif 'cancella' in message.text.lower():
            msg = bot.reply_to(message, 'Sei sicuro di cancellare il tuo account? Scrivi SI, SONO SICURO')
            bot.register_next_step_handler(msg, Delete)
     
        elif comandi['materiale'] == message.text:
            markup_lvl = scegli_livello(utente, "Materiale")
            markup_lvl.add(types.InlineKeyboardButton("Materiale Forme di scrittura", callback_data="Materiale Forme di scrittura"))
            msg = bot.reply_to(message, "Scegli il livello", reply_markup=markup_lvl)

        
        elif authorize(message):
            if "backup" in message.text.lower():
                doc = open('giappo.db', 'rb')
                bot.send_document(chatid, doc, caption="#database #backup")
                doc.close()
     
            elif "Restore" in message.text:
                bot.send_message(chatid, "Aggiorno il database, abbi pazienza...")
                g.Restore()  
                bot.send_message(chatid, "Ho aggiornato tutte le parole!")

            elif "update" in message.text:
                utenti = session.query(Utente).all()
                for utente in utenti:
                    bot.send_message(utente.id_telegram, "Ciao, il bot è stato aggiornato. Premi /start per farlo funzionare!")
            elif "Broadcast" in message.text:
                msg = bot.reply_to(message, "Cosa vuoi scrivere?")
                bot.register_next_step_handler(msg, broadcast)
        else:
            bot.send_message(chatid, 'Questa funzionalità non esiste o la devi ancora sbloccare', reply_markup=markup)
        session.close()
    except Exception as e:
        error(message, e)


def Tag(message):
    try:
        chatid = message.chat.id
        g = GiappoBot(BOT_TOKEN, CANALE_LOG)
        g.domandaTag(chatid, message.text)
        Question(message, chatid)
    except Exception as e:
        error(message,e)


def Delete(message):
    chatid = message.chat.id
    if message.text == 'SI, SONO SICURO':
        g = GiappoBot(BOT_TOKEN, CANALE_LOG)
        g.deleteAccount(chatid)
        bot.send_message(chatid, 'Sayounara!')
    else:
        bot.send_message(chatid, 'Nessun problema')

def Question(message, chatid):
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    markup = types.InlineKeyboardMarkup()
    indizi = ['💰 10: Categoria', '💰 20: Metà parola', '💰 10: Pozione leggera 🩸', '💰 20: Pozione moderata 🩸', '💰 30: Pozione superiore 🩸']


    for indizio in indizi:
        markup.add(types.InlineKeyboardButton(indizio, callback_data=indizio))
    utente = session.query(Utente).filter_by(id_telegram = chatid).first() 

    if utente.traduci_in == "Italiano":
        word = session.query(Word).filter_by(ita=utente.risposta).first()
    elif utente.traduci_in == "Romaji":
        word = session.query(Word).filter_by(romanji=utente.risposta).first()
    elif utente.traduci_in == "Kana":
        word = session.query(Word).filter_by(katana=utente.risposta).first()

    if word is not None:
        domanda = "Traduci \""+utente.domanda+"\" in " + utente.traduci_in
        if word.Altro != "":
            domanda = domanda +" ("+ word.Altro+")"
        session.close()
        msg = bot.reply_to(message, domanda, reply_markup=markup)
        bot.register_next_step_handler(msg, Answer)


def Answer(message):
    try:
        g = GiappoBot(BOT_TOKEN,CANALE_LOG)
        chatid = message.chat.id
        utente = g.getUtente(chatid)
        risposta_esatta = cleanString(utente.risposta)
        risposta_data   = cleanString(message.text)

        level = utente.livello
        if risposta_data==risposta_esatta:
            risposta = g.CorrectAnswer(chatid)           
            bot.send_message(chatid, risposta)
        else:
            risposta = g.WrongAnswer(chatid)
            bot.send_message(chatid, risposta)
            

        utente = g.getUtente(chatid)
        current_level = utente.livello 
        markup = unlock(message)
        if current_level != level:
            doc = open("Materiale/Livello "+str(current_level)+'.pdf', 'rb')
            bot.send_document(chatid, doc, caption="Materiale di studio "+str(current_level), reply_markup=markup)
            doc.close()            
            if current_level==1:
                doc = open("Materiale/Forme di scrittura.pdf", 'rb')
                bot.send_document(chatid, doc, caption="Materiale di studio: Forme di scrittura", reply_markup=markup)
                doc.close() 
                SendMateriale(message)
    except Exception as e:
        error(message, e)

@bot.message_handler(func=lambda m: True)
def echo_all(message):
	bot.reply_to(message, "Mi dispiace ma non ho capito... premi /start per riavviarmi")

bot.infinity_polling()


