import telebot
from telebot import types
import time
import requests
import json
import urllib
import os

""" Values """
music_search = "Музыка";
joytime = "Joytime";
lives = "Lives";
go_back_general = "Вернуться назад";

music_searching = "Ищем музыку...";

"""
mode
----------------------------------------
0 - Main

1 - Search Music
2 - Searching Music


"""
mode = 0;

""" Bot Initializing """
bot = telebot.TeleBot("1243381315:AAE2_7kHDny_glvv3XAmRahpw08PY42Jqxg", parse_mode=None);

""" DEBUG """
def debugUser(message):
    print("User ID: " + str(message.chat.id))
    print("Username: " + str(message.chat.username))
    print("First name: " + str(message.chat.first_name))
    print("Last name: " + str(message.chat.last_name))
    print("-----------------------------------------------");

""" SEARCH AUDIO QUERY INITIALIZE"""
def searchMusicQuery(message):
		bot.send_message(message.chat.id, "Введите название трека", reply_markup=rkm_back())
		pass

def rkm_back():
		markup2 = types.ReplyKeyboardMarkup(True);
		itembtn = types.KeyboardButton(go_back_general);
		markup2.add(itembtn);
		return markup2

""" SEARCH AUDIO INITIALIZE"""
def searchMusic(message):
		bot.send_message(message.chat.id, music_searching, None, None, types.ReplyKeyboardRemove(), None, None, None)
		
		response = requests.get("https://raw.githubusercontent.com/JTA15TM/MarshmelloMusicApi/main/api/all_audio.json")

		if response.status_code == 200: 
			MusicSearchResult(message, response)
		else :
			bot.send_message(message.chat.id, "Произошла ошибка, попробуйте снова!", None)

""" Search Music - Result """
def MusicSearchResult(message, response):
	global mode
	parsed_string = json.loads(response.content)

	domain = parsed_string['domain']
	end = parsed_string['end']
	audioList = parsed_string['audio']['items']

	have = False;

	list = []
	count = 0

	for item in audioList:
		if message.text.lower().strip() in item['title'].lower().strip():
			if have == False : 
				have = True
				bot.send_chat_action(message.chat.id, 'upload_audio')
			if mode != 2 : mode = 2

			a = Audio(getArtist(item), item['title'], domain + item['music_url'] + end, "" + str(count))
			list.append(a)

			audioFile = domain + item['music_url'] + end
			urllib.request.urlretrieve(audioFile, "audio_send_" + str(count) + ".mp3")

			count += 1

	if have == True :
		for i in range(len(list)):
			audio = open("audio_send_" + list[i].getId() + ".mp3", "rb")
			if i >= len(list) - 1 : bot.send_audio(message.chat.id, audio, None, None, list[i].getArtist(), list[i].getTitle(), reply_markup=rkm_back())
			else : bot.send_audio(message.chat.id, audio, None, None, list[i].getArtist(), list[i].getTitle(), reply_markup=types.ReplyKeyboardRemove())
			audio.close()

			os.remove("audio_send_" + list[i].getId() + ".mp3")

	if have == False : bot.send_message(message.chat.id, "Ничего не найдено!", reply_markup=rkm_back())
	mode = 1
		

""" Bot Start Commands """
def generateDefaultButtons(message) :
			markup = types.ReplyKeyboardMarkup(True)
			itembtn1 = types.KeyboardButton(music_search)
			itembtn2 = types.KeyboardButton(joytime)
			itembtn3 = types.KeyboardButton(lives)
			markup.add(itembtn1, itembtn2, itembtn3)
			bot.send_message(message.chat.id, "Выберите одно из ниже перечисленных", reply_markup=markup)
			pass

@bot.message_handler(commands=['start'])
def send_welcome(message):
			generateDefaultButtons(message)
			global mode 
			if mode != 0 : mode = 0

""" Bot Messaging Initialize """
@bot.message_handler(func=lambda message: True)
def echo_all(message):
	debugUser(message);
	global mode

	"""If Search Music """ 
	if mode == 1 and message.text != go_back_general:
		searchMusic(message);

	"""Selection Mode"""
	if message.text == music_search and mode == 0:
		    mode = 1
		    searchMusicQuery(message);
	elif message.text == go_back_general and mode != 0:
			mode = 0
			generateDefaultButtons(message);


""" Audio - Artist Data """
def getArtist(item):
	artist = ""
	for i in range(len(item['artist'])):
		if i == 0:
			artist += item['artist'][i]['name']
		elif i == 1:
			artist += " feat. " + item['artist'][i]['name']
		else:
			artist += " & " + item['artist'][i]['name']
	return artist


""" Audio Class """
class Audio(object):
	def getArtist(self) : return self.artist
	def getTitle(self) : return self.title
	def getUrl(self) : return self.url
	def getId(self) : return self.id

	def __init__(self, artist, title, url, id):
		self.artist = artist
		self.title = title
		self.url = url
		self.id = id

""" Bot Enabled """
bot.polling();