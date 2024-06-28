import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials, storage
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Set the path to your service account key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Initialize Firestore DB
db = firestore.Client()

# Initialize Firebase Admin
cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv("STORAGE_BUCKET")
})

bucket = storage.bucket()
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        role = request.form['role']
        
        # Check if user already exists in the appropriate collection
        if(role=='customer'):
            user_ref = db.collection(role + 's').where('email', '==', email).stream()
            user = None
            for u in user_ref:
                user = u.to_dict()
                break
        
            if user:
                flash('Email already exists', 'danger')
                return redirect(url_for('signup'))
        
        # Add new user to the appropriate collection in Firestore
            db.collection(role + 's').add({
                'name': name,
                'email': email,
                'phone': phone,
                'password': password,

            })
        
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))
        elif(role=='instructor'):
            pass
        else:
            pass
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        # Authenticate user
        if(role=='customer'):
            user_ref = db.collection('users').where('email', '==', email).where('role', '==', role).stream()
            user = None
            for u in user_ref:
                user = u.to_dict()
                break
        
            if user and user['password'] == password:
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid email, password, or role', 'danger')
                return redirect(url_for('login'))
            
        elif(role=='instructor'):
            pass
        else:
            pass
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session=0
    flash('You have been logged out.', 'success')
    return redirect(url_for('/'))

if __name__ == '__main__':
    app.run(debug=True)
