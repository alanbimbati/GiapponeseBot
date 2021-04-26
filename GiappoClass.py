
from telebot import TeleBot
import random
from telebot import types
from sqlalchemy         import create_engine
from sqlalchemy         import update
from sqlalchemy         import desc
from sqlalchemy.orm     import sessionmaker

from model import Utente, db_connect, create_table
from model import Word
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

    def ItaToRomanji(self, chatid):
        self.TranslateFromTo(chatid, "Italiano", "Romanji")

    def ItaToKatana(self, chatid):
        self.TranslateFromTo(chatid, "Italiano", "Katana")

    def RomanjiToIta(self, chatid):
        self.TranslateFromTo(chatid, "Romanji", "Italiano")

    def KatanaToIta(self, chatid):
        self.TranslateFromTo(chatid, "Katana", "Italiano")
        
    def TranslateFromTo(self, chatid, translate_by, translate_to):
        session = self.Session()
        self.clean(chatid)
        riga = random.randint(1,self.NumRows())
        word = session.query(Word).filter_by(id=riga).first()
        item={}

        if translate_by == "Italiano":
            item['domanda'] = word.ita
        elif translate_by == "Romanji":
            item['domanda'] = word.romanji
        elif translate_by == "Katana":
            item['domanda'] = word.katana


        if translate_to == "Italiano":
            item['risposta'] = word.ita
        elif translate_to == "Romanji":
            item['risposta'] = word.romanji
        elif translate_to == "Katana":
            item['risposta'] = word.katana

        item['traduci_in'] = translate_to
        item['traduci_da'] = translate_by
        print(item)
        self.update_user(chatid, item)
        session.close()


    def TuttoRandom(self, chatid):
        scelta = random.randint(1,4)
        if scelta == 1:
            self.ItaToKatana(chatid)
        elif scelta == 2:
            self.ItaToRomanji(chatid)
        elif scelta == 3:
            self.RomanjiToIta(chatid)
        elif scelta == 4:
            self.KatanaToIta(chatid)
        else:
            print("ERROR")

    def clean(self, chatid):
        item = {}
        item['traduci_in'] = ""
        item['traduci_da'] = ""
        item['domanda'] = ""
        item['risposta'] = ""
        self.update_user(chatid, item)

    def NumRows(self):
        session = self.Session()
        nrows= session.query(Word).count()
        session.close()
        return nrows 
        

    def CorrectAnswer(self, chatid):
        utente = self.getUtente(chatid)
        item = {}
        item['exp'] = utente.exp + 10
        item['money'] = utente.money+ random.randint(5,20)

        if utente.exp%100==0:
            item['livello'] = utente.livello+ 1
        self.update_user(chatid,item)


    def WrongAnswer(self, chatid):
        utente = self.getUtente(chatid)
        item = {}
        item['exp'] = utente.exp +1
        item['monny'] = utente.money+ random.randint(1,5)
        if utente.exp%100==0:
            item['livello'] = utente.livello+ 1
        self.update_user(chatid,item)

    def printMe(self, chatid):
        me = self.getUtente(chatid)
        if me.username is not None:
            return "👤 @"+me.username+"\n💪🏻 Exp"+str(me.exp)+"\n🎖 Lv. "+str(me.livello)+"\n💰 Money "+str(me.money)
        else:
            return "👤 "+me.nome+"\n💪🏻 Exp"+str(me.exp)+"\n🎖 Lv. "+str(me.livello)+"\n💰 Money "+str(me.money)

    def Backup(self):
        print("backupping")
        doc = open('giappo.db', 'rb')
        self.bot.send_document('62716473', doc, caption="#database #backup")
        doc.close()

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
        if utente.money >=50:
            self.update_user(chatid, money = utente.money- 50)
            return utente.risposta[:int(len(utente.risposta)/2)]
        else:
            return "No money, no party"
        
    def skip(self, chatid):
        utente = self.getUtente(chatid)
        if utente.money >=50:
            self.update_user(chatid, money = utente.money- 50)
            return "Domanda saltata"
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
        
        
        for row in range(42,len(nrows)):
            ita = sheet.cell(row,1).value
            print(ita)
            exist = session.query(Word).filter_by(ita=ita).first()
            if exist is None:
                try:
                    word = Word()
                    word.ita        = sheet.cell(row,1).value
                    word.romanji    = sheet.cell(row,2).value
                    word.katana     = sheet.cell(row,3).value
                    word.libro      = sheet.cell(row,4).value
                    word.lezione    = sheet.cell(row,5).value
                    word.Tag        = sheet.cell(row,6).value
                    word.Altro      = sheet.cell(row,7).value

                    session.add(word)
                    session.commit()
                except:
                    session.rollback()
                    raise
                finally:
                    session.close()

    def classifica(self):
        session = self.Session()
        utenti = session.query(Utente).order_by(desc(Utente.livello)).order_by(desc(Utente.exp)).all()
        return utenti

        