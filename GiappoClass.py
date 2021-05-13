
from telebot import TeleBot
import random
from telebot import types
from sqlalchemy         import create_engine
from sqlalchemy         import update
from sqlalchemy         import desc
from sqlalchemy.orm     import sessionmaker

from model import Utente,Word, db_connect, create_table
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GiappoBot:
    domanda  = ""
    risposta = ""
    traduci_da = ""
    traduci_in = ""

    def __init__(self, bot, canale_log):
        self.bot        = bot
        self.canale_log = canale_log
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def ItaToRomanji(self, chatid, words):
        self.TranslateFromTo(chatid, "Italiano", "Romaji", words)

    def ItaToKatana(self, chatid, words):
        self.TranslateFromTo(chatid, "Italiano", "Katana", words)

    def RomanjiToIta(self, chatid, words):
        self.TranslateFromTo(chatid, "Romaji", "Italiano", words)

    def KatanaToIta(self, chatid, words):
        self.TranslateFromTo(chatid, "Katana", "Italiano", words)
        
    def TranslateFromTo(self, chatid, translate_by, translate_to, words):
        print("Translate from ", translate_by, "to ",translate_to)
        self.clean(chatid)
        # words = session.query(Word).all()
        random.seed()
        index = random.randint(0,len(words)-1)
        print(index, len(words), words[index])
        word = words[index]
        item={}

        if translate_by == "Italiano":
            item['domanda'] = word.ita
        elif translate_by == "Romaji":
            item['domanda'] = word.romanji
        elif translate_by == "Katana":
            item['domanda'] = word.katana

        if translate_to == "Italiano":
            item['risposta'] = word.ita
        elif translate_to == "Romaji":
            item['risposta'] = word.romanji
        elif translate_to == "Katana":
            item['risposta'] = word.katana

        if item['risposta'] == "" or item['domanda']=="":
            self.clean(chatid)
            self.TranslateFromTo(chatid, translate_by, translate_to, words)

        item['traduci_da'] = translate_by
        item['traduci_in'] = translate_to
        print(item)
        self.update_user(chatid, item)

    def domandaTag(self,chatid, tag):
        session = self.Session()
        words = session.query(Word)
        words = words.filter_by(Tag=tag).all()
        random.seed()
        scelta = random.randint(1,4)
        if scelta == 1:
            self.ItaToKatana(chatid, words)
        elif scelta == 2:
            self.ItaToRomanji(chatid, words)
        elif scelta == 3:
            self.RomanjiToIta(chatid, words)
        elif scelta == 4:
            self.KatanaToIta(chatid, words)
        else:
            print("ERROR")
        session.close()

    def TuttoRandom(self, chatid, words):
        scelta = random.randint(1,4)
        if scelta == 1:
            self.ItaToKatana(chatid, words)
        elif scelta == 2:
            self.ItaToRomanji(chatid, words)
        elif scelta == 3:
            self.RomanjiToIta(chatid, words)
        elif scelta == 4:
            self.KatanaToIta(chatid, words)
        else:
            print("ERROR")

    def clean(self, chatid):
        item = {}
        item['traduci_in'] = ""
        item['traduci_da'] = ""
        item['domanda'] = ""
        item['risposta'] = ""
        self.update_user(chatid, item)

    def changeExp(self, chatid, Exp, Money):
        utente = self.getUtente(chatid)
        item = {}
        item['exp'] = utente.exp + Exp
        item['money'] = utente.money+ Money
        item['livello'] = int(item['exp']/100)
        print(item)
        self.update_user(chatid,item)

    def CorrectAnswer(self, chatid):
        money = random.randint(1, 10)
        exp = random.randint(2,5)
        self.changeExp(chatid, exp, money)

    def WrongAnswer(self, chatid):
        money = random.randint(1,5)*-1
        exp = 1
        self.changeExp(chatid, exp, money)

    def printMe(self, chatid):
        me = self.getUtente(chatid)
        if me.username is not None:
            return "👤 @"+me.username+"\n💪🏻 Exp"+str(me.exp)+"\n🎖 Lv. "+str(me.livello)+"\n💰 Money "+str(me.money)
        else:
            return "👤 "+me.nome+"\n💪🏻 Exp"+str(me.exp)+"\n🎖 Lv. "+str(me.livello)+"\n💰 Money "+str(me.money)

    def CreateUtente(self, message):
        session = self.Session()
        exist = self.getUtente(message.chat.id)
        if exist is None:
            try:
                utente = Utente()
                utente.username = message.chat.username
                utente.nome = message.chat.first_name
                utente.id_telegram = message.chat.id
                utente.cognome = message.chat.last_name
                utente.exp = 0
                utente.livello = 0
                utente.money = 0
                # logging.info("adding...")
                # logging.info(sell)
                session.add(utente)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()

    def buyHalfWord(self, chatid):
        utente = self.getUtente(chatid)
        if utente.money >=20:
            item = {}
            item['money'] = utente.money -20
            self.update_user(chatid, item)
            return utente.risposta[:int(len(utente.risposta)/2)]
        else:
            return "No money, no party"

    def buyCategory(self,chatid):
        utente = self.getUtente(chatid)
        session = self.Session()
        if utente.traduci_in == "Italiano":
            tag = session.query(Word).filter_by(ita=utente.risposta).first().Tag
        elif utente.traduci_in == "Romaji":
            tag = session.query(Word).filter_by(romanji=utente.risposta).first().Tag
        elif utente.traduci_in == "Katana":
            tag = session.query(Word).filter_by(katana=utente.risposta).first().Tag

        if utente.money >=10:
            item = {}
            item['money'] = utente.money -10
            self.update_user(chatid, item)
            return tag
        else:
            return "No money, no party"

    def getUtente(self, chatid):
        session = self.Session()
        utente = session.query(Utente).filter_by(id_telegram = chatid).first()  
        session.close()
        return utente

    def update_user(self, chatid, kwargs):
        session = self.Session()
        utente = session.query(Utente).filter_by(id_telegram = chatid).first()
        
        for key, value in kwargs.items():  # `kwargs.iteritems()` in Python 2
            setattr(utente, key, value) 

        session.commit()
        session.close()

    def populaDB(self):
        session = self.Session()
        scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("Studio Giapponese").sheet1
        nrows = sheet.get_all_records()
        for row in nrows:
            exist = session.query(Word).filter_by(ita=row['Italiano']).first()
            if exist is None:
                try:
                    word = Word()
                    word.ita        = row['Italiano']
                    word.romanji    = row['Romanji']
                    word.katana     = row['Katana']
                    word.libro      = row['Libro']
                    word.lezione    = row['Lezione']
                    word.Tag        = row['Tag']
                    word.Altro      = row['Altro...']

                    session.add(word)
                    session.commit()
                except:
                    session.rollback()
                    raise
                finally:
                    session.close()
            else:
                word = Word()
                if row['Romanji'] != word.romanji: word.romanji = row['Romanji']
                if row['Katana'] != word.katana: word.katana = row['Katana']
                if row['Libro'] != word.libro: word.libro = row['Libro']
                if row['Lezione'] != word.Lezione: word.Lezione = row['Lezione']
                if row['Tag'] != word.Tag: word.Tag = row['Tag']
                if row['Altro...'] != word.Altro: word.Altro = row['Altro...']


    def classifica(self):   
        session = self.Session()
        utenti = session.query(Utente).order_by(desc(Utente.livello)).order_by(desc(Utente.exp)).all()
        return utenti
        