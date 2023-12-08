import subprocess
import time
import sqlite3
import google.generativeai as palm

conn = sqlite3.connect('tele_bot.db', check_same_thread=False)
palm.configure(api_key='AIzaSyD4ChJeYG8pndGSikGTUTAQLrq5ZVcGkBA')

try:
    subprocess.check_call(['pip3', 'install', '-r', 'requirements.txt'])
    print('Dependencies installed successfully.')
except subprocess.CalledProcessError:
    print('Failed to install dependencies.')

import telebot
import ssl
import os
from dotenv import load_dotenv
#from gradio_client import Client
from wiki import search
from pytube import YouTube
from youtube_search import YoutubeSearch
from telebot import types
import requests
from io import BytesIO

#client = Client("http://47.103.63.15:50085/")

ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()
BOT_TOKEN = os.environ['BOT']

bot = telebot.TeleBot(BOT_TOKEN)

# img = req.urlretrieve("https://akm-img-a-in.tosshub.com/indiatoday/images/story/202306/leo_7-sixteen_nine.jpg", 'leo.png')
# bot.send_photo(5713740053, InputFile('leo.png'), "Naa Ready, nee ready aah ?")

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    filtered_text = message.text[7:]
    c = conn.cursor()
    c.execute("INSERT INTO tele_bot_record (command, query, user, userid, response) VALUES (?, ?, ?, ?, ?)", ('start',filtered_text,message.from_user.first_name,message.from_user.username, f'Hey, how are you doing {message.from_user.first_name} - from @codewithjss?'))
    conn.commit()
    c.close()
    print(f'Message from user : {message.from_user.first_name}')
    bot.reply_to(message, f'Hey, how are you doing {message.from_user.first_name} ? \n\n - from @codewithjss')
    bot.send_message(5713740053, f'{message.from_user.first_name} - {message.from_user.username} : {message.text}')

@bot.message_handler(commands=['chat'])
def process_req(message):
    print(f'Message from user : {message.from_user.first_name}')
    filtered_text = message.text.removeprefix('/chat ')
    response = palm.generate_text(prompt=filtered_text)
    result = response.result
    c = conn.cursor()
    c.execute("INSERT INTO tele_bot_record (command, query, user, userid, response) VALUES (?, ?, ?, ?, ?)", ('chat',filtered_text,message.from_user.first_name,message.from_user.username, result))
    conn.commit()
    c.close()
    bot.send_message(5713740053, f'{message.from_user.first_name} - {message.from_user.username} : {message.text}')
    bot.send_message(5713740053, result)
    bot.reply_to(message, result)

@bot.message_handler(commands=['summary'])
def get_summary(message):
    print(f'Message from user : {message.from_user.first_name}')
    filtered_text = message.text.removeprefix('/summary ')
    result = search('summary', filtered_text)
    c = conn.cursor()
    c.execute("INSERT INTO tele_bot_record (command, query, user, userid, response) VALUES (?, ?, ?, ?, ?)", ('summary',filtered_text,message.from_user.first_name,message.from_user.username, result))
    conn.commit()
    c.close()
    bot.send_message(5713740053, f'{message.from_user.first_name} - {message.from_user.username} : {message.text}')
    bot.send_message(5713740053, result)
    bot.reply_to(message, result)

@bot.message_handler(commands=['description'])
def get_desc(message):
    print(f'Message from user : {message.from_user.first_name}')
    filtered_text = message.text.removeprefix('/description ')
    result = search('description', filtered_text)
    c = conn.cursor()
    c.execute("INSERT INTO tele_bot_record (command, query, user, userid, response) VALUES (?, ?, ?, ?, ?)", ('description',filtered_text,message.from_user.first_name,message.from_user.username, result))
    conn.commit()
    c.close()
    bot.send_message(5713740053, f'{message.from_user.first_name} - {message.from_user.username} : {message.text}')
    bot.send_message(5713740053, result)
    bot.reply_to(message, result)

@bot.message_handler(commands=['song'])
def handle_keyword_search(message):
    keyword = message.text

    # Use youtube_search library to search for videos based on the keyword
    results = YoutubeSearch(keyword, max_results=1).to_dict()
    sorted_results = results[0]
    if not sorted_results:
        bot.send_message(message.chat.id, "No audio found for the given keyword.")
        return
    
    video_id = sorted_results['id']

    # Construct the YouTube video URL
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    yt = YouTube(video_url)
    available_formats = yt.streams.filter(only_audio=True, mime_type="audio/mp4").all()
    markup = types.InlineKeyboardMarkup()
    for i, fmt in enumerate(available_formats):
        markup.add(types.InlineKeyboardButton(f"Download {fmt.abr}",callback_data=f'Download {video_url},{fmt.abr}'))

    bot.send_message(5713740053, f'{message.from_user.first_name} - {message.from_user.username} : {message.text}')
    bot.send_message(message.chat.id, "Select a format to download:", reply_markup=markup)


@bot.callback_query_handler(func=lambda message: message.data.startswith("Download "))
def handle_download_request(message):
    extract = (message.data.replace("Download ", "")).split(',')
    selected_format = extract[1]
    video_url = extract[0]
    yt = YouTube(video_url)
    mp3_file_path = f'{yt.title}-{selected_format}.mp3'
    mp3_stream = yt.streams.filter(only_audio=True, abr=selected_format, mime_type="audio/mp4").first()
    mp3_stream.download(filename=mp3_file_path)
    # # Download the external thumbnail image
    thumbnail_response = requests.get(yt.thumbnail_url)
    thumbnail_file = BytesIO(thumbnail_response.content)
    thumbnail_file.name = f'{yt.title}-{selected_format}.png'
    bot.send_document(message.from_user.id, open(mp3_file_path, 'rb'),caption=mp3_file_path, thumbnail=thumbnail_file)
    os.remove(mp3_file_path)

@bot.message_handler(commands=['video'])
def handle_video_keyword_search(message):
    keyword = message.text

    # Use youtube_search library to search for videos based on the keyword
    results = YoutubeSearch(keyword, max_results=1).to_dict()
    sorted_results = results[0]
    if not sorted_results:
        bot.send_message(message.chat.id, "No video found for the given keyword.")
        return
    
    video_id = sorted_results['id']

    # Construct the YouTube video URL
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    yt = YouTube(video_url)
    available_formats = yt.streams.filter(mime_type="video/mp4",progressive=True).all()

    markup = types.InlineKeyboardMarkup()
    for i, fmt in enumerate(available_formats):
        markup.add(types.InlineKeyboardButton(f"Download {fmt.resolution} video",callback_data=f'{video_url},{fmt.resolution} Download'))

    bot.send_message(5713740053, f'{message.from_user.first_name} - {message.from_user.username} : {message.text}')
    bot.send_message(message.chat.id, "Select a format to download:", reply_markup=markup)

@bot.callback_query_handler(func=lambda message: message.data.endswith(" Download"))
def handle_video_download_request(message):
    extract = (message.data.replace(" Download", "")).split(',')
    selected_format = extract[1]
    video_url = extract[0]
    yt = YouTube(video_url)
    mp4_file_path = f'{yt.title}-{selected_format}.mp4'
    reqUrl = yt.streams.filter(resolution=selected_format, mime_type="video/mp4", progressive=True).first().url

    response = requests.get(reqUrl)
    if response.status_code == 200:
    # Create a BytesIO object and write the video content to it
        video_bytesio = BytesIO(response.content)
        time.sleep(1)
        bot.send_video(message.from_user.id, video_bytesio, caption=mp4_file_path)

API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
headers = {"Authorization": f"Bearer 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"}

def query_img(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

@bot.message_handler(commands=['image'])
def get_img(message):
    filtered_text = message.text.removeprefix('/image ');
    result = query_img({"inputs":filtered_text})
    c = conn.cursor()
    c.execute("INSERT INTO tele_bot_record (command, query, user, userid, response) VALUES (?, ?, ?, ?, ?)", ('description',filtered_text,message.from_user.first_name,message.from_user.username, result))
    conn.commit()
    c.close()
    bot.send_message(5713740053, f'{message.from_user.first_name} - {message.from_user.username} : {message.text}')
    bot.send_photo(5713740053, photo=result)
    bot.send_photo(message.chat.id, photo=result)

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, "Please send a message in the format \n/command yourquery")

if __name__ == '__main__':
    while True:
        bot.send_message(5713740053, 'I am awake')
        bot.infinity_polling()
        time.sleep(120)
