import subprocess
import sqlite3

conn = sqlite3.connect('tele_bot.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS tele_bot_record (
    command TEXT,
    query TEXT,
    user TEXT,
    userid TEXT,
    response TEXT
)
''')
conn.commit()
conn.close()

try:
    print('installing Dependencies.')
    subprocess.check_call(['pip3', 'install', '-r', 'requirements.txt'])
    print('Dependencies installed successfully.')
except subprocess.CalledProcessError:
    print('Failed to install dependencies.')

import telebot
import ssl
import os
from dotenv import load_dotenv
from gradio_client import Client
from wiki import search

client = Client("http://47.103.63.15:50085/")

ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()
BOT_TOKEN = os.environ['BOT']

bot = telebot.TeleBot(BOT_TOKEN)

# img = req.urlretrieve("https://akm-img-a-in.tosshub.com/indiatoday/images/story/202306/leo_7-sixteen_nine.jpg", 'leo.png')
# bot.send_photo(5713740053, InputFile('leo.png'), "Naa Ready, nee ready aah ?")

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    filtered_text = message.text[7:]
    conn.cursor()
    cursor.execute("INSERT INTO tele_bot_record (command, query, user, userid, response) VALUES (?, ?, ?, ?, ?)", ('start',filtered_text,message.from_user.first_name,message.from_user.username, f'Hey, how are you doing {message.from_user.first_name} - from @codewithjss?'))
    conn.commit()
    print(f'Message from user : {message.from_user.first_name}')
    bot.reply_to(message, f'Hey, how are you doing {message.from_user.first_name} - from @codewithjss?')

@bot.message_handler(commands=['chat'])
def process_req(message):
    print(f'Message from user : {message.from_user.first_name}')
    filtered_text = message.text.removeprefix('/chat ')
    result = client.predict(
				filtered_text,	# str in 'Instruction' Textbox component
				1,
                2048,
				api_name="/predict"
    )
    conn.cursor()
    cursor.execute("INSERT INTO tele_bot_record (command, query, user, userid, response) VALUES (?, ?, ?, ?, ?)", ('chat',filtered_text,message.from_user.first_name,message.from_user.username, result))
    conn.commit()
    bot.reply_to(message, result)

@bot.message_handler(commands=['summary'])
def get_summary(message):
    print(f'Message from user : {message.from_user.first_name}')
    filtered_text = message.text.removeprefix('/summary ')
    result = search('summary', filtered_text)
    conn.cursor()
    cursor.execute("INSERT INTO tele_bot_record (command, query, user, userid, response) VALUES (?, ?, ?, ?, ?)", ('summary',filtered_text,message.from_user.first_name,message.from_user.username, result))
    conn.commit()
    bot.reply_to(message, result)

@bot.message_handler(commands=['description'])
def get_desc(message):
    print(f'Message from user : {message.from_user.first_name}')
    filtered_text = message.text.removeprefix('/description ')
    result = search('description', filtered_text)
    conn.cursor()
    cursor.execute("INSERT INTO tele_bot_record (command, query, user, userid, response) VALUES (?, ?, ?, ?, ?)", ('description',filtered_text,message.from_user.first_name,message.from_user.username, result))
    conn.commit()
    bot.reply_to(message, result)

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)

if __name__ == '__main__':
    print('polling start')
    bot.infinity_polling()