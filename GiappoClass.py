
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

    def LevelFilter(self, chatid,words):
        session = self.Session()
        utente = session.query(Utente).filter_by(id_telegram = chatid).first()  
        words = words.filter(Word.livello <= utente.livello)
        return words

    def ItaToRomanji(self, chatid, words):
        self.TranslateFromTo(chatid, "Italiano", "Romaji", words)

    def ItaToKana(self, chatid, words):
        words = words.filter(Word.katana != None)
        self.TranslateFromTo(chatid, "Italiano", "Kana", words)

    def RomanjiToIta(self, chatid, words):
        self.TranslateFromTo(chatid, "Romaji", "Italiano", words)

    def KanaToIta(self, chatid, words):
        words = words.filter(Word.katana != None)
        self.TranslateFromTo(chatid, "Kana", "Italiano", words)
        
    def TranslateFromTo(self, chatid, translate_by, translate_to, words):
        livelli = words.distinct(Word.livello).group_by(Word.livello).all()
        words = words.all()
        self.clean(chatid)
        # words = session.query(Word).all()
        random.seed()
        index = random.randint(0,len(words)-1)
        word = words[index]
        print("PAROLA ", word.ita, word.romanji, word.katana)
        item={}

        if translate_by == "Italiano":
            item['domanda'] = word.ita
        elif translate_by == "Romaji":
            item['domanda'] = word.romanji
        elif translate_by == "Kana":
            item['domanda'] = word.katana

        if translate_to == "Italiano":
            item['risposta'] = word.ita
        elif translate_to == "Romaji":
            item['risposta'] = word.romanji
        elif translate_to == "Kana":
            item['risposta'] = word.katana

        item['traduci_da'] = translate_by
        item['traduci_in'] = translate_to


        # scegli livello 0
        if len(livelli)==1 and livelli[0].livello==0:
            if item['traduci_da'] == "Italiano" and item['traduci_in'] == "Kana":
                print("ita kana -> ita romaji")
                item['traduci_in'] = "Romaji"
                item['risposta'] = word.romanji

            elif item['traduci_da'] == "Kana" and item['traduci_in'] == "Italiano":
                print("kana ita -> romaji ita")
                item['traduci_da'] == "Romaji"
                item['domanda'] = word.romanji

            elif item['traduci_da'] == "Kana" and item['traduci_in'] == "Romaji":
                print("kana romaji -> ita romaji")
                item['traduci_da'] == "Italiano"
                item['domanda'] = word.ita

            elif item['traduci_da'] == "Romaji" and item['traduci_in'] == "Kana":
                print("romaji kana -> romaji ita")
                item['traduci_in'] = "Italiano"
                item['risposta'] = word.ita


        if item['risposta'] != "" and item['domanda'] != "":
            self.update_user(chatid, item)

    def domandaTag(self,chatid, tag):
        session = self.Session()
        words = session.query(Word)
        words = words.filter_by(Tag=tag).all()
        self.TuttoRandom(chatid,words)
        session.close()

    
    def domandaLevel(self,chatid, livello):
        lvl = int(livello.split()[1])
        session = self.Session()
        words = session.query(Word)
        words = words.filter_by(livello=lvl)
        self.TuttoRandom(chatid,words)
        session.close()

    def TuttoRandom(self, chatid, words):
        scelta = random.randint(1,4)        
        if   scelta == 1:
            self.RomanjiToIta(chatid, words)
        elif scelta == 2:
            self.ItaToRomanji(chatid, words)
        elif scelta == 3:
            self.ItaToKana(chatid, words)
        elif scelta == 4:
            self.KanaToIta(chatid, words)
        else:
            print("ERROR")

    def clean(self, chatid):
        item = {}
        item['traduci_in'] = ""
        item['traduci_da'] = ""
        item['domanda'] = ""
        item['risposta'] = ""
        self.update_user(chatid, item)

    def CorrectAnswer(self, chatid):
        utente = self.getUtente(chatid)
        item = {}
        item['money'] = utente.money + random.randint(1, 10)
        item['exp']   = utente.exp + random.randint(2,5)
        item['livello'] = int(item['exp'] / 100)
        risposta = "🎉 Complimenti hai risposto giusto!!"
        if item['livello']!=utente.livello:
            item['vita'] = self.maxLife(utente)+10
            risposta = risposta + "\n🎉 Complimenti! Sei passato/a al livello "+str(item['livello'])

        self.update_user(chatid, item)
        return risposta

    def WrongAnswer(self, chatid):
        item = {}
        utente = self.getUtente(chatid)
        item['vita'] = utente.vita - random.randint(1,5)
        current_life = item['vita']
        if current_life<0:
            item['vita']        = self.maxLife(utente)
            item['livello']     = max(utente.livello-1,0)
            item['exp']         = max(utente.exp-100,0)
            risposta = "☠️ Sei morto! Hai perso 1 livello, la prossima volta compra qualche pozione!"
        else:
            risposta = "Mi dispiace la risposta giusta era "+str(utente.risposta)
        self.update_user(chatid, item)
        return risposta

    def printMe(self, chatid):
        session = self.Session()
        me = session.query(Utente).filter_by(id_telegram = chatid).first()  
        if me.username is not None:
            stringa = "👤 @"+me.username
        else:
            stringa = "👤 "+me.nome
        stringa = stringa +"\n💪🏻 Exp "+str(me.exp)+"\n🎖 Lv. "+str(me.livello)+"\n💰 Money "+str(me.money)+"\n🩸 Vita "+str(me.vita)+"/"+str(self.maxLife(me))
        session.close()
        return stringa

    def CreateUtente(self, message):
        session = self.Session()
        chatid = message.chat.id
        exist = session.query(Utente).filter_by(id_telegram = chatid).first()  
        if exist is None:
            try:
                utente = Utente()
                utente.username     = message.chat.username
                utente.nome         = message.chat.first_name
                utente.id_telegram  = message.chat.id
                utente.cognome      = message.chat.last_name
                utente.vita         = 50
                utente.exp          = 0
                utente.livello      = 0
                utente.money        = 0
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
        utente = session.query(Utente).filter_by(id_telegram = chatid).first()  
        if utente.money >=20:
            item = {}
            item['money'] = utente.money -20
            session.close()
            self.update_user(chatid, item)
            return utente.risposta[:int(len(utente.risposta)/2)]
        else:
            session.close()
            return "No money, no party"

    def buyCategory(self,chatid):
        session = self.Session()
        utente = session.query(Utente).filter_by(id_telegram = chatid).first()  
        if utente.traduci_in == "Italiano":
            tag = session.query(Word).filter_by(    ita=utente.risposta     ).first().Tag
        elif utente.traduci_in == "Romaji":
            tag = session.query(Word).filter_by(    romanji=utente.risposta ).first().Tag
        elif utente.traduci_in == "Katana":
            tag = session.query(Word).filter_by(    katana=utente.risposta  ).first().Tag

        if utente.money >=10:
            item = {}
            item['money'] = utente.money -10
            self.update_user(chatid, item)
            return tag
        else:
            return "No money, no party"
        session.close()

    def buyPotion(self, chatid, tipologia):
        session = self.Session()
        utente = session.query(Utente).filter_by(id_telegram = chatid).first()  
        max_life = self.maxLife(utente)
        item = {}
        if tipologia==0:   
            vita = 10
        elif tipologia==1:
            vita = 25
        elif tipologia==2:
            vita = 50
        else:
            vita = 0
        item['vita'] = min(utente.vita +vita, max_life)
        if vita!=0:
            messaggio = "Ho ripristinato "+ str(vita)+ " Punti Vita 🩸"
        else:
            messaggio = "Senza soldi non puoi comprare alcuna pozione"
        self.update_user(chatid, item)
        return messaggio

    def update_user(self, chatid, kwargs):
        session = self.Session()
        utente =  session.query(Utente).filter_by(id_telegram=chatid).first()
        for key, value in kwargs.items():  # `kwargs.iteritems()` in Python
            print("updating ",key, "in ",value)
            setattr(utente, key, value) 
        session.commit()
        session.close()

    def update_word(self, word_id, kwargs):
        session = self.Session()
        word = session.query(Word).filter_by(id = word_id).first()
        
        for key, value in kwargs.items():  # `kwargs.iteritems()` in Python 2
            setattr(word, key, value) 

        session.commit()
        session.close()


    def Restore(self):
        scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open("Studio Giapponese").sheet1
        nrows = sheet.get_all_records()
        for row in nrows:
            session = self.Session()
            exist = session.query(Word).filter_by(id=row['Id']).first()
            word = Word()
            word.id         = row['Id']
            word.ita        = row['Italiano']
            word.romanji    = row['Romaji']
            word.katana     = row['Kana']
            word.libro      = row['Libro']
            word.lezione    = row['Lezione']
            word.Tag        = row['Tag']
            word.Altro      = row['Altro...']
            word.livello    = row['Livello']
            session.close()
            if exist is None:
                session = self.Session()
                try:
                    session.add(word)
                    session.commit()
                except:
                    session.rollback()
                    raise
                finally:
                    session.close()
            else:
                word = {}
                word['id']          = row['Id']
                word['romanji']     = row['Romaji']
                word['katana']      = row['Kana']
                word['libro']       = row['Libro']
                word['ita']         = row['Italiano']
                word['tag']         = row['Tag']
                word['altro']       = row['Altro...']
                word['lezione']     = row['Lezione']
                word['livello']     = row['Livello']
                session.close()
                self.update_word(word['id'], word)
                

    def classifica(self):   
        session = self.Session()
        utenti = session.query(Utente).order_by(desc(Utente.livello)).order_by(desc(Utente.exp)).all()
        session.close()
        return utenti
        
    def deleteAccount(self,chatid):
        session = self.Session()
        utente = session.query(Utente).filter_by(id_telegram = chatid).first()  
        session.delete(utente)
        session.commit()

    def getUtente(self, chatid):
        session = self.Session()    
        utente = session.query(Utente).filter_by(id_telegram=chatid).first()
        session.close()
        return utente

    def maxLife(self, utente):
        return 50 + utente.livello*10