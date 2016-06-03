# -*- coding: utf-8 -*-


#######################
###### LIBRARIES ######
#######################

import telebot # BOT API
from telebot import types # BOT TYPES
import time # FOR NON-STOPING BOT
import urllib # REQUESTS HANDLING
import json # JSON LIBRARY
import random # MATH RANDOM LIBRARY
import os # OS LIBRARY
import sys

#########################
###### DEFINITIONS ######
#########################

TOKEN = 'TOKEN' #This is the token of the BOT
bot = telebot.TeleBot(TOKEN) #Initialice the bot

######################
###### LISTENER ######
######################

def listener(messages): #Here the bot handles the different messages
    for m in messages: #We go through the messages that the bot receives
        cid = m.chat.id #We save the chat ID
        print "[" + str(cid) + "]:\t " + m.text #I print the text into terminal
        write_to_log("[" + str(cid) + "]:\t " + m.text) #I print it in the log file

######################
###### HANDLERS ######
######################

@bot.message_handler(commands=['roto2']) # roto2 handler
def command_roto2(msg): #roto2 function. Solves the command
    cid = msg.chat.id #Save the Chat ID
    try:
        bot.send_photo( cid, open( 'roto2.png', 'rb'))
        write_to_log("[" + str(cid) + "]:\t " + "roto2 enviado\n")
    except Exception as e:
        except_handler(cid, e.args[1], 'Error al enviar el roto2')

@bot.message_handler(commands=['miramacho']) # miramacho handler
def command_miramacho(msg): # miramacho function
    cid = msg.chat.id # Saves the chat id
    try:
        bot.send_message( cid, 'Vete a la mierda')
        write_to_log("[" + str(cid) + "]:\t " + "Vete a la mierda enviado\n")
    except Exception as e:
        except_handler(cid, e, "Error al procesar el comando")

@bot.message_handler(commands=['yt']) # Youtube Command handler
def command_youtube(msg): #YouTube Function
    cid = msg.chat.id
    query = msg.text[4:]
    if query == '':
        m = bot.reply_to(msg, "Que quieres buscar?")
        bot.register_next_step_handler(m, yt_video_handler)
    else:
        youtube_send(cid,query)

@bot.message_handler(commands=['img']) # img command handler
def command_img(msg):
    cid = msg.chat.id
    token = msg.text[5:]
    if token == '':
        m = bot.reply_to(msg, "Que quieres buscar?")
        bot.register_next_step_handler(m, img_handler)
    else:
        img_send(cid, token)


################################
###### REPLY_TO FUNCTIONS ######
################################

def yt_video_handler(msg):
    cid = msg.chat.id
    query = msg.text
    youtube_send(cid,query)

def img_handler(msg):
    cid = msg.chat.id
    token = msg.text
    img_send(cid, token)

################################
###### SPECIFIC FUNCTIONS ######
################################

def youtube_send(cid, query):
    try:
        link = urllib.urlopen("https://www.googleapis.com/youtube/v3/search?part=snippet&q=%s&key={API KEY}" % query)
        data = json.loads(link.read())
        rnd_no = random.randrange(0,3)
        id = data["items"][rnd_no]["id"]["videoId"] 
        video = "http://www.youtube.com/watch?v=" + id
        bot.send_message(cid, video)
        write_to_log("[" + str(cid) + "]:\t " + "Busqueda: " + query)
        write_to_log("[" + str(cid) + "]:\t " + video)
    except Exception as e:
        except_handler(cid, e, "Error while sending the video")

def img_send(cid, token):
    try:
        imgURL = "https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=" + token
        link = urllib.urlopen(imgURL)
        data = json.loads(link.read())
        rnd_no = random.randrange(0,3)
        image = urllib.URLopener()
        image.retrieve(data['responseData']['results'][0]['unescapedUrl'], "tmp.jpg")
        bot.send_photo(cid, open( 'tmp.jpg', 'rb'))
        write_to_log("[" + str(cid) + "]:\t " + imgURL + " enviado\n")
    except Exception as e:
        except_handler(cid, e, "Error while downloading the image")

def except_handler( cid, e, msg):
    bot.send_message(cid, msg)
    write_to_log(msg + "\t" + str(e))

###############################
###### WRITING FUNCTIONS ######
###############################

def write_to_log(msg): #the function to write in the file
    log = open('log.txt','a') #Open the file
    log.write("[" + time.strftime("%c") + "]\t " + str(msg) + '\n') #Write in the file
    log.close() #close the file

##################
###### MAIN ######
##################

bot.set_update_listener(listener)
bot.polling(none_stop=True)
