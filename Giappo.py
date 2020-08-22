# coding=utf-8
import telebot
import datetime
from telebot import types
import random
import xlwt
import xlrd

StudioGiappoBot = "1359089063:AAEig5IHLo_sRmyoGEzPbEv0PdylyyIglAo"
ArghiabBot      = "1046887890:AAGleAYgCgY_VXCUePAAKW0slllf3kcSFVU"
bot = telebot.TeleBot(StudioGiappoBot)

log	= {"ID": "-1001469821841"}
admin = ['62716473']
autorizzati = ['391473447', '62716473']
libri = ["Speciale", "A", "B", "C", "Kanji"]

def logga(message):
    bot.send_message(log["ID"], message.text+" by @"+message.chat.username)

def logga_this(string):
    bot.send_message(log["ID"], string)

@bot.message_handler(commands=['start', 'menu'])
def handle_start(message):  
    logga(message)
    bot.send_message(message.chat.id, "こんいちわ")
    id_utente = message.chat.id
    salva_utente(id_utente)
    menu(message)

def boolean_response(message, domanda, next_handler):
    logga(message)

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Si', 'No')
    msg = bot.reply_to(message, domanda, reply_markup=markup)
    bot.register_next_step_handler(msg, next_handler)

def menu(message):
    logga(message)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Inserisci vocabolo', 'Domanda casuale', 'Domanda per Categoria', 'Ultima riga inserita')
    msg = bot.reply_to(message, 'Cosa vuoi fare?', reply_markup=markup)
    bot.register_next_step_handler(msg, menu2)	

def menu2(message):
    logga(message)

    id_utente = message.chat.id
    if message.text=="Inserisci vocabolo" and str(id_utente) in autorizzati:
        msg = bot.reply_to(message, "scrivimi il vocabolo in italiano")
        bot.register_next_step_handler(msg, aggiungi_romanji)
    elif message.text=="Domanda casuale":
        database = open("database.txt", "r").readlines()
        domanda_casuale(message, database)
    elif message.text=="Domanda per Tag":    
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

        tags = get_tags()
        for tag in tags:
            markup.add(tag) 
        msg = bot.reply_to(message, "Inserisci il tag", reply_markup=markup)
        bot.register_next_step_handler(msg, quale_tag)
    elif message.text=="Ultima riga inserita":
        database = open("database.txt", "r").readlines()
        last_row = database[-1]
        logga_this(str(last_row))
        bot.reply_to(message, str(last_row))
        menu(message)
    else:
        bot.reply_to(message, "Inserisci qualche vocabolo prima!")

def get_tags():
    tags = []
    filer = open("database.txt").readlines()
    for row in filer:
        for campo in row.split():
            elemento = campo.split(":")
            if elemento[0]=="tag"  and (elemento[1] not in tags):
                tag = elemento[1]
                tags.append(tag)
    tags.sort()
    return tags

def get_lessons():
    lessons = []
    filer = open("database.txt").readlines()
    for row in filer:
        for campo in row.split():
            elemento = campo.split(":")
            if elemento[0]=="lezione":
                lesson = elemento[1]
                lesson = lesson[:-1]
                if lesson not in lessons:
                    lessons.append(lesson)
    lessons.sort(reverse=True)
    return lessons

def domanda_casuale(message, database):
    # scelgo una domanda a caso tra tutte le righe del database
    if len(database)>0:
        r = random.randint(1,len(database))-1
        campi = database[r].split(",")
        #elimina tag, lezione e libro
        campi.pop(-1)
        campi.pop(-1)
        campi.pop(-1)

        # scelgo un elemento a caso tra (italiano, romaji, ecc...)
        r1 = random.randint(1, len(campi)-1)-1
        tipo = campi[r1].split(":")[0]
        risposta = campi[r1].split(":")[1]
        # elimino la domanda, se è italiano chiedo la stessa parola in un'altra forma
        r2 = r1
        while(campi[r2]==campi[r1]):
            logga_this(str(campi[r2])+", "+str(campi[r1]))
            r2 = random.randint(1, len(campi)-1)-1
            nuovo_tipo        = campi[r2].split(":")[0]
            nuova_risposta    = campi[r2].split(":")[1]
            logga_this("nuovo tipo: "+ nuovo_tipo+" nuova_risposta: "+ nuova_risposta)


        msg = bot.reply_to(message, risposta+" traduci in "+nuovo_tipo)
        bot.register_next_step_handler(msg, risposta_function, nuova_risposta)

def quale_tag(message):
    filer = open("database.txt").readlines()
    tag = message.text
    domande = []
    for row in filer:
        for campo in row.split():
            elemento = campo.split(":")
            if elemento[0]=="tag":
                if elemento[1]==tag:
                    domande.append(row)
    domanda_casuale(message, domande)

def risposta_function(message, risposta):
    logga(message)

    id_utente = message.chat.id
    if message.text.lower() == risposta.lower():
    	cambia_exp(id_utente,10)
    	msg = bot.reply_to(message, "🎉 Complimenti hai ottenuto 10 punti esperienza!\n(riavviami con /start)")
    else:
        cambia_exp(id_utente, -10)
        msg = bot.reply_to(message, "😞 Mi dispiace hai sbagliato, la risposta era " +risposta+"\n meno 10 exp!\n(riavviami con /start)")
    esperienza = exp_utente(id_utente)
    livello    = lv_utente(id_utente)
    bot.reply_to(message, "Ora hai "+str(esperienza)+" punti esperienza e sei al livello "+str(livello))
    menu(message)

def aggiungi_testo(vocabolo, tipo):
    database = open("database.txt", "r").readlines()
    dwrite = open("database.txt", "w")
    for row in database:
        dwrite.write(row)
    if tipo!="tag":
        dwrite.write(tipo+":"+vocabolo)
        dwrite.write(", ")
    elif tipo=="Italiano":
        dwrite.write("\n"+tipo+":"+vocabolo)
        dwrite.write(", ")
    else:
        dwrite.write("tag:"+vocabolo)
        dwrite.write("\n")
    dwrite.close()
    '''
    database = xlrd.open_workbook("database.csv", "r")
    sheet = database.sheet_by_index(0)

    new = xlwt.Workbook()
    sheetw = new.sheet_index(0)
    
    '''

def aggiungi_romanji(message):
    logga(message)
    id_utente = message.chat.id
    # salva ita
    aggiungi_testo(message.text, "Italiano")
    msg = bot.reply_to(message, "scrivimelo in romaji")
    bot.register_next_step_handler(msg, vuoi_hiragana)


def vuoi_hiragana(message):
    logga(message)
    id_utente = message.chat.id
    # salva romanji
    aggiungi_testo(message.text, "Romaji")
    boolean_response(message, "Vuoi inserire l'Hiragana?", aggiungi_hiragana)

def aggiungi_hiragana(message):
    logga(message)
    id_utente = message.chat.id

    if message.text =="Si":
        msg = bot.reply_to(message, "Inserisci l'Hiragana (premendo Shift+Spazio puoi cambiare tastiera)")
        bot.register_next_step_handler(msg, salva_hiragana)
    elif message.text =="No":
        boolean_response(message, "Vuoi inserire il Kanji?", aggiungi_kanji)
    else:
        aggiungi_hiragana(message)

def salva_hiragana(message):
    logga(message)
    id_utente = message.chat.id
    # salva hiragana
    aggiungi_testo(message.text, "Hiragana")
    #vuoi_kanji(message)
    boolean_response(message, "Vuoi inserire il Kanji?", aggiungi_kanji)

def aggiungi_kanji(message):
    logga(message)
    id_utente = message.chat.id
    if message.text =="Si":
        msg = bot.reply_to(message, "Inserisci il Kanji")
        bot.register_next_step_handler(msg, salva_kanji)
    elif message.text =="No":
        aggiungi_libro(message)
    else:
        aggiungi_kanji(message)
        
def salva_kanji(message):
    logga(message)
    id_utente = message.chat.id
    # salva kanji
    aggiungi_testo(message.text, "Kanji")
    aggiungi_libro(message)

def aggiungi_libro(message):
    logga(message)
    id_utente = message.chat.id
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for libro in libri:
        markup.add(libro)
    msg = bot.reply_to(message, 'Inserisci il libro', reply_markup=markup)
    bot.register_next_step_handler(msg, aggiungi_lezione)

def aggiungi_lezione(message):
    logga(message)
    id_utente = message.chat.id

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    lezioni = get_lessons()
    for lezione in lezioni:
        markup.add(lezione)

    aggiungi_testo(message.text, "libro")
    msg = bot.reply_to(message, "Inserisci la lezione", reply_markup=markup)
    bot.register_next_step_handler(msg, aggiungi_etichetta)  

def aggiungi_etichetta(message):
    logga(message)
    id_utente = message.chat.id
    aggiungi_testo(message.text, "lezione")

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)

    tags = get_tags()
    for tag in tags:
        markup.add(tag)

    msg = bot.reply_to(message, "Inserisci un'etichetta(riavviami con /start)", reply_markup=markup)
    bot.register_next_step_handler(msg, salva_etichetta)

def salva_etichetta(message):
    logga(message)
    id_utente = message.chat.id
    aggiungi_testo(message.text, "tag")
    menu(message)
    
 
'''
def vuoi(message, cosa, next_handler):
    id_utente = message.chat.id
    aggiungi_testo(message.text)
    boolean_response(message, "Vuoi inserire"+cosa+"?", next_handler)
'''

def trova_utente(id):
    book = xlrd.open_workbook("utenti.xlsx","r")
    sheet = book.sheet_by_index(0)
    for row in range(sheet.nrows):
        id_utente = sheet.cell_value(row,0)
        id = float(id)
        if id == id_utente:
            return row
    return None

def salva_utente(id):
    if trova_utente(id)==None:
        read = xlrd.open_workbook("utenti.xlsx","r")
        sheet_r= read.sheet_by_index(0)

        book = xlwt.Workbook()
        sheet = book.add_sheet("utenti.xlsx")
        trovato = 0
        riga = sheet_r.nrows
        for row in range(sheet_r.nrows):
            id_utente = sheet_r.cell_value(row,0)
            esperienza= sheet_r.cell_value(row,1)
            livello   = sheet_r.cell_value(row,2)
            if id==id_utente:
                trovato = 1
            else:
                sheet.write(row,0,str(id_utente))
                sheet.write(row,1,esperienza)
                sheet.write(row,2,livello)
        if trovato == 0:
            sheet.write(riga,0, id)
            sheet.write(riga,1, 0)
            sheet.write(riga,2, 1)

        book.save("utenti.xlsx")


def cambia_exp(id,exp):
    filer = xlrd.open_workbook("utenti.xlsx","r")
    sheet = filer.sheet_by_index(0)

    filew = xlwt.Workbook()
    sheetw= filew.add_sheet("utenti.xlsx")
    for row in range(sheet.nrows):
        id_utente   = sheet.cell_value(row,0)
        exp_attuali = sheet.cell_value(row,1)
        livello     = sheet.cell_value(row,2)

        sheetw.write(row,0,id_utente)
        if id==id_utente:
            exp_attuali = exp_attuali+exp
            livello = int(exp_attuali / 100)

        sheetw.write(row,1,exp_attuali)
        sheetw.write(row,2,livello)

    filew.save("utenti.xlsx")	    

def exp_utente(id):
    riga = trova_utente(id)
    if riga!=None:
        filer = xlrd.open_workbook("utenti.xlsx","r")
        sheet = filer.sheet_by_index(0)
        return int(sheet.cell_value(riga,1))

def lv_utente(id):
    riga = trova_utente(id)
    if riga!=None:
        filer = xlrd.open_workbook("utenti.xlsx","r")
        sheet = filer.sheet_by_index(0)
        return int(sheet.cell_value(riga,2))

bot.polling(none_stop=True, interval=0, timeout=20)