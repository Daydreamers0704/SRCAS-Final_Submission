from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import os
import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
from database.db_connection import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = '\tO&\xd7\xb3\r\x88}0+f\x10\xd4\xcf:L\x03\x832;\xac\xf7\xd6\x0e'

# Paths and settings
UPLOAD_FOLDER = "D:/Hackathon/Crop disease/AI/static/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MODEL_PATH = 'D:/Hackathon/Crop disease/AI/models/Trained model.h5'
CSV_FILE_PATH = "D:/Hackathon/Crop disease/AI/static/data/ajith.csv"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load your trained model
model = load_model(MODEL_PATH)

# Class labels
class_labels = ['Brown_Rust', 'Healthy', 'Loose_Smut', 'Septoria', 'Yellow_Rust']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_image(image_path):
    # Open the image using PIL
    image = Image.open(image_path)
    
    # Convert the image to RGB (3 channels)
    image = image.convert('RGB')
    
    # Resize the image to the target size expected by the model (128x128 pixels)
    image = image.resize((128, 128))
    
    # Convert the image to a numpy array
    image = img_to_array(image)
    
    # Expand dimensions to match the model's input shape (batch_size, height, width, channels)
    image = np.expand_dims(image, axis=0)
    
    # Normalize the image data
    image = image / 255.0
    
    # Predict the class probabilities
    prediction = model.predict(image)
    
    # Get the index of the class with the highest probability
    predicted_class = np.argmax(prediction, axis=1)[0]
    
    # Map the index to the class label
    predicted_label = class_labels[predicted_class]
    
    return predicted_label

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/log')
def log():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user[2], password):  # Assuming password is stored hashed
        flash('Login Successful!', 'success')
        return redirect(url_for('home2'))
    else:
        flash('Login Failed. Check your credentials.', 'danger')
        return redirect(url_for('home2'))

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = generate_password_hash(request.form['password'])
    phone_number = request.form['phonenumber']

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO users (name, email, password, phone_number) VALUES (%s, %s, %s, %s)', 
                   (name, email, password, phone_number))
    connection.commit()
    cursor.close()
    connection.close()

    flash('Account Created Successfully! Please login.', 'success')
    return redirect(url_for('log'))

@app.route('/dashboard')
def home2():
    return render_template('dashboard2.html')

@app.route('/Estore')
def Estore():
    return render_template('e.index.html')




@app.route('/model', methods=['GET'])
def index():
    return render_template('model.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Predict the image using the trained model
            prediction = predict_image(file_path)

            return render_template('result.html', prediction=prediction, image_file=filename)

    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
