
from telebot import TeleBot
import random
from telebot import types
from sqlalchemy         import create_engine
from sqlalchemy         import update
from sqlalchemy.orm     import sessionmaker
from model import Utente, db_connect, create_table

class GiappoBot:
    domanda  = ""
    risposta = ""
    traduci_da = ""
    traduci_in = ""
    def __init__(self, bot, canale_log, sheet):
        self.bot        = bot
        self.canale_log = canale_log
        self.sheet      = sheet
        
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    def ItaToRomanji(self):
        riga = random.randint(1,self.NumRows())
        self.domanda  = self.sheet.cell(riga, 1).value
        self.risposta = self.sheet.cell(riga, 2).value
        self.traduci_da = "Italiano"
        self.traducu_in = "Romanji"

    def ItaToKatana(self):
        riga = random.randint(1,self.NumRows())
        while self.sheet.cell(riga, 3).value == "":
            riga = random.randint(1,self.NumRows())
            self.domanda  = self.sheet.cell(riga, 1).value
            self.risposta = self.sheet.cell(riga, 3).value
        self.traduci_da = "Italiano"
        self.traducu_in = "Katana"

    def RomanjiToIta(self):
        riga = random.randint(1,self.NumRows())
        self.domanda  = self.sheet.cell(riga, 2).value
        self.risposta = self.sheet.cell(riga, 1).value
        self.traduci_da = "Romanji"
        self.traducu_in = "Italiano"

    def KatanaToIta(self):
        riga = random.randint(1,self.NumRows())
        while self.sheet.cell(riga, 3).value == "":
            riga = random.randint(1,self.NumRows())
            self.domanda  = self.sheet.cell(riga, 3).value
            self.risposta = self.sheet.cell(riga, 1).value
        self.traduci_da = "Katana"
        self.traducu_in = "Italiano"

    def TuttoRandom(self):
        scelta = random.randint(1,4)
        if scelta == 1:
            self.ItaToKatana()
        elif scelta == 2:
            self.ItaToRomanji()
        elif scelta == 3:
            self.RomanjiToIta()
        elif scelta == 4:
            self.KatanaToIta()
        else:
            print("ERROR")

    def clean(self):
        self.traduci_in = ""
        self.traduci_da = ""
        self.risposta   = ""
        self.domanda    = ""

    def NumRows(self):
        return len(self.sheet.get_all_records())

    def CorrectAnswer(self, chatid):
        session = self.Session()
        utente = self.getUtente(chatid)
        utente.exp += 10
        utente.money += random.randint(5,20)
        if utente.exp%100==0:
            utente.livello += 1
        session.commit()

    def WrongAnswer(self, chatid):
        sesssion = self.Session()
        utente = self.getUtente(chatid)
        utente.exp += 1
        utente.money += random.randint(1,5)
        if utente.exp%100==0:
            utente.livello += 1
        session.commit() 

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
        session = self.Session()
        utente = self.getUtente(chatid)
        if utente.money >=50:
            utente.money -= 50
            session.commit()
            return g.risposta[:int(len(g.risposta)/2)]
        else:
            return "No money, no party"
        

    def getUtente(self, chatid):
        session = self.Session()
        return session.query(Utente).filter_by(id_telegram = chatid).first()
