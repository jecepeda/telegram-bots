# -*- coding: utf-8 -*-
import json
from urllib.request import quote

import requests
import telebot
from book import Book

file_json = open('token.json')
TOKEN = json.load(file_json)["TOKEN"]

bot = telebot.TeleBot(TOKEN)
bot.skip_pending = True
urlBase = "http://it-ebooks-api.info/v1/"

###############################################################
########## Resource URL	http://it-ebooks-api.info/v1/##########
########## Request Method	REST (GET) ########################
########## Response Format	JSON ##############################
########## Response Encoding UTF-8 ############################
###############################################################

# TODO save the information of the books in a database
# TODO use a redis database to store the querys and the query result
# TODO The value to store will be a json object with all the book results.

userStep = dict()
user_book_dict = dict()


def get_user_step(cid):
    if cid not in userStep:
        userStep[cid] = 0
    return userStep[cid]


######################
###### LISTENER ######
######################

def lstnr(msgs):
    for m in msgs:
        print("Mensaje Recibido")


######################
###### HANDLERS ######
######################

@bot.message_handler(commands=['search_book', 'buscar_libro'])
def send_document(message):
    chat_id = message.chat.id
    bot.reply_to(message, "Hola! Que libro querías buscar?")
    userStep[chat_id] = 'do_query'


@bot.message_handler(func=lambda msg: get_user_step(msg.chat.id) == 'do_query')
def search_books(message):
    chat_id = message.chat.id
    if message.content_type != 'text':
        bot.send_message(message.chat.id, "Por favor envía una busqueda")
    elif len(message.text) > 50:
        bot.send_message(message.chat.id,
                         "Por favor envia una busqueda mas pequeña")
    else:
        req = requests.get(urlBase + "search/query/" + quote(message.text))
        json_request = json.loads(req.text)
        print(json_request)
        if json_request["Total"] == 0:
            bot.send_message(chat_id, "Sorry, I haven't found any book")
        elif 'Books' in json_request:
            book_id_list = process_json(json_request)
        else:
            return bot.send_message(chat_id,
                                    "No hemos encontrado ningún resultado con esa búsqueda")
        text = ""
        for book_id in book_id_list:
            text += "/" + str(book_id) + " " + user_book_dict[
                book_id].__str__() + "\n"
        bot.send_message(chat_id, text)
        userStep[chat_id] = 'send_book'


@bot.message_handler(func=lambda msg: get_user_step(msg.chat.id) == 'send_book')
def send_selected_book(message):
    print('Me han pedido un libro concreto')
    chat_id = message.chat.id
    if message.content_type != 'text':
        bot.send_message(chat_id, "Por favor, envía texto.")
    elif int(message.text.lstrip('/').split(' ')[0].split('@')[
                 0]) in user_book_dict:
        url = urlBase + "book/" + \
              message.text.lstrip('/').split(' ')[0].split('@')[0]
        book = requests.get(url)
        rq = book.json()
        bot.send_message(chat_id,
                         "Puedes descargar el libro aquí: " + rq[u'Download'])
    else:
        bot.send_message(chat_id,
                         "Ese libro no existe, prueba con alguna opción existente")


def process_json(json_request):
    books = json_request['Books']
    book_id_list = []
    for book in books:
        user_book_dict[book[u'ID']] = Book(book[u'ID'],
                                           book[u'Title'],
                                           book[u'Description'],
                                           book[u'Image'],
                                           book[u'isbn'])
        if u'Subtitle' in book:
            user_book_dict[book[u'ID']].subtitle = book[u'Subtitle']
        book_id_list.append(book[u'ID'])

    return book_id_list


bot.set_update_listener(lstnr)
bot.polling()
