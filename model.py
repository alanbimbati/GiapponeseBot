from sqlalchemy                 import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm             import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import (Integer, String, Date, DateTime, Float, Boolean, Text)

Base = declarative_base()


def db_connect():
    return create_engine('sqlite:///giappo.db')
    

def create_table(engine):
    Base.metadata.create_all(engine)

class Utente(Base):
    __tablename__ = "utente"
    id = Column(Integer, primary_key=True)
    id_telegram = Column('id_Telegram', Integer, unique=True)
    nome  = Column('nome', String(32))
    cognome = Column('cognome', String(32))
    username = Column('username', String(32), unique=True)
    exp = Column('exp', Integer)
    money = Column('money', Integer)
    livello = Column('livello', Integer)
    domanda = Column('domanda', String(64))
    risposta = Column('risposta', String(64))
    traduci_da = Column('traduci_da', String(64))
    traduci_in = Column('traduci_in', String(64))

class Word(Base):
    __tablename__ = "word"
    id = Column(Integer, primary_key=True)
    ita = Column('ita', String(256), unique=True)
    romanji = Column('romanji', String(256), unique=True)
    katana = Column('katana', String(256))
    libro = Column('libro', String(32))
    Lezione = Column('lezione', String(16))
    Tag = Column('tag', String(32))
    Altro = Column('altro', String(128))
