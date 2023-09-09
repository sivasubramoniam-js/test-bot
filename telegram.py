import telebot
import ssl
import os
from dotenv import load_dotenv

ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()
BOT_TOKEN = os.environ['BOT']

bot = telebot.TeleBot(BOT_TOKEN)

# img = req.urlretrieve("https://akm-img-a-in.tosshub.com/indiatoday/images/story/202306/leo_7-sixteen_nine.jpg", 'leo.png')
# bot.send_photo(5713740053, InputFile('leo.png'), "Naa Ready, nee ready aah ?")

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, f'Hey, how are you doing {message.from_user.first_name} ?')

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)

if __name__ == '__main__':
    print('polling start')
    bot.infinity_polling()