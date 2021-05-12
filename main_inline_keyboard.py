@bot.callback_query_handler(func=lambda call: "Menu" == call.data)
@bot.message_handler(commands=['init'])
def Init(message):
    if message.chat.type == "private":
        g = GiappoBot(BOT_TOKEN, CANALE_LOG)  
        g.CreateUtente(message)

        scelte = [
            ['🇮🇹 ItaToRomanji 🇯🇵', '🇮🇹 ItaToKatana 🇯🇵'],
            ['🇮🇹 ItaToRomanji 🇯🇵', '🇮🇹 ItaToKatana 🇯🇵'],
            ['🇯🇵 RomanjiToIta 🇮🇹', '🇯🇵 KatanaToIta 🇮🇹'],
            ['️#️⃣ Tag', '🎲 TuttoRandom'],
            ['👤 Scheda personale','🏆 Classifica']
        ]
        if authorize(message):
            scelte.append(['Backup','Restore'])

        markup = types.InlineKeyboardMarkup()
        for row in scelte:
            a = types.InlineKeyboardButton(row[0], callback_data="Menu"+row[0])
            b = types.InlineKeyboardButton(row[1], callback_data="Menu"+row[1])
            markup.add(a,b)
        print("qui")
        chatid = message.chat.id
        bot.send_message(chatid, "Cosa vuoi fare?", reply_markup=markup)
    else:
        bot.reply_to(message, "Mi dispiace, questo bot funziona solo in privato")

@bot.callback_query_handler(func=lambda call: "Menu" in call.data)
def Menu_figo(call):
    engine = db_connect()
    create_table(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    g = GiappoBot(BOT_TOKEN, CANALE_LOG)  
    words = session.query(Word).all()
    chatid = call.message.chat.id

    
    if "ItaToRomanji" in call.data: 
        g.ItaToRomanji(chatid, words)
        Question(call.message, chatid)               
    elif "ItaToKatana" in call.data:     
        g.ItaToKatana(chatid, words)
        Question(call.message, chatid)
    elif "RomanjiToIta" in call.data:     
        g.RomanjiToIta(chatid, words)
        Question(call.message, chatid)
    elif "KatanaToIta" in call.data:     
        g.KatanaToIta(chatid, words)
        Question(call.message, chatid)
    elif "Tag" in call.data:
        tags = engine.execute("SELECT tag FROM WORD").unique()
        markup_tags = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for tag in tags:
            tag = str(tag).replace("(","").replace(")","").replace("'","").replace(",","")
            markup_tags.add(tag)
        msg = bot.reply_to(call.message, "Scegli il tag", reply_markup=markup_tags)
        bot.register_next_step_handler(msg, Tag)
    elif "TuttoRandom" in call.data:
        g.TuttoRandom(chatid, words)
        Question(call.message, chatid)
    elif "Scheda" in call.data:
        bot.reply_to(call.message, g.printMe(chatid),reply_markup=hideBoard)
        time.sleep(1)
        Init(call.message)
    elif "classifica" in call.data.lower():
        utenti = g.classifica()
        if len(utenti)>=1:
            classifica = "🥇 "+utenti[0].nome+" Lv."+str(utenti[0].livello)+"Exp. "+str(utenti[0].exp)+"\n"
        if len(utenti)>=2:
            classifica = classifica + "🥈 "+utenti[1].nome+" Lv."+str(utenti[1].livello)+"Exp. "+str(utenti[1].exp)+"\n"
        if len(utenti)>=3:
            classifica = classifica + "🥉 "+utenti[2].nome+" Lv."+str(utenti[2].livello)+"Exp. "+str(utenti[2].exp)+"\n"
        bot.send_message(chatid, classifica)
        Init(call.message)

    if authorize(call.message):
        if "Backup" in call.data:
            doc = open('giappo.db', 'rb')
            bot.send_document(chatid, doc, caption="#database #backup", reply_markup=hideBoard)
            doc.close()
            Init(call.message)
        if "Restore" in call.data:
            g.populaDB()  
            Init(call.message)
    session.close()

def QuestionMeglio(message, chatid):
    engine = db_connect()
    create_table(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2)
    indizi = ['💰 50: Metà parola', '💰 50: Skip']
    for indizio in indizi:
        markup.add(indizio)
    utente = session.query(Utente).filter_by(id_telegram = chatid).first()  
    # msg = bot.reply_to(message, "Traduci \""+utente.domanda+"\" in " + utente.traduci_in, reply_markup=markup)
    bot.edit_message_text("Traduci \""+utente.domanda+"\" in " + utente.traduci_in, message.chat.id, message.message_id, reply_markup=markup)
    # bot.register_next_step_handler(msg, Answer)

    session.close()

