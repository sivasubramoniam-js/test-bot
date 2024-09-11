import subprocess
import time
import sqlite3
import base64
from PIL import Image
import io
from db import create_database, insert_into_db
# try:
#     subprocess.check_call(['pip3', 'install', '-r', 'requirements.txt'])
#     print('Dependencies installed successfully.')
# except subprocess.CalledProcessError:
#     print('Failed to install dependencies.')
from PIL import Image
import json
import re
import google.generativeai as genai

conn = sqlite3.connect('tele_bot.db', check_same_thread=False)
genai.configure(api_key='AIzaSyD4ChJeYG8pndGSikGTUTAQLrq5ZVcGkBA')
text_model = genai.GenerativeModel('gemini-1.5-flash')

#client = Client("http://47.103.63.15:50085/")

# ssl._create_default_https_context = ssl._create_unverified_context


from flask_cors import CORS
from flask import Flask, jsonify, request, render_template

app = Flask(__name__,template_folder='./',static_folder='../frontend/build/static')
CORS(app)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_post():
        # Check if the request contains file data
    if 'type' not in request.form:
        return jsonify({'error': 'No type provided'}), 400

    file_type = request.form['type']
    base64_str = request.form['data']
    theme = request.form.get('theme', '')
    print(theme)
    response_format = '''{
        captions: ["Caption 1","Caption 2","Caption 3"],
        hashtags: ["Hashtag 1","Hashtag 2","Hashtag 3"],
        recommended_songs: ["Song 1", "Song 2", "Song 3"]    
    }'''
    result = None
    try:
        # create_database()
        if base64_str.startswith('data:'):
            base64_str = base64_str.split(',')[1]

        # Decode the Base64 string
        image_data = base64.b64decode(base64_str)
        
        # Create a BytesIO object from the decoded data
        image_bytes = io.BytesIO(image_data)
        
        # Open the image with Pillow
        image = Image.open(image_bytes)
        result = None
        if len(theme):
            response = text_model.generate_content([f"Generate instagram post for this image in the format {response_format}.", image])
            result = response.text
        else:
            response = text_model.generate_content([f"Generate instagram post for this image in the format {response_format}. Theme: {theme}", image])
            result = response.text
        result_string = result

        # Remove the triple backticks and extra characters
        result_string = result_string.strip('```json\n').strip()

        # Decode escaped characters (e.g., \\" becomes ")
        result_string = result_string.replace('\\"', '"')

        # Step 2: Parse the cleaned JSON string
        json_object = json.loads(result_string)
        return jsonify({'result': json_object}), 200
    except Exception as e:
        print(str(e))
        # Handle image upload
        # insert_into_db(file_type, image_data, theme, result)
        return jsonify({'error': 'Unsupported type'}), 400

if __name__ == "__main__":
  app.run(debug=True)