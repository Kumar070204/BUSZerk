# app.py (Integrated with Fast2SMS, Fake Call, and Bus Tracking)
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from datetime import datetime
import secrets
import requests
import threading
import time
import numpy as np
import pandas as pd
import joblib

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

cred = credentials.Certificate('buszerk-a24ab-firebase-adminsdk-fbsvc-30245924cc.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Load ML models and feature columns
xgb_model = joblib.load('xgb_model.pkl')
feature_columns = joblib.load('feature_columns.pkl')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# SOS Integration
FAST2SMS_API_KEY = "PrpbA1pvJBIQpvgXGuzURKujdyHeLf0io8HOtS4OGYW7LzpKml40AlV4xYzf"

def send_sos_sms(to_phone_number, latitude, longitude):
    """
    Sends an SOS SMS via Fast2SMS API including the user's location.
    """
    message = f"Emergency! Sona Help needed.\nLocation: https://www.google.com/maps?q={latitude},{longitude}"
    
    url = "https://www.fast2sms.com/dev/bulkV2"
    payload = {
        "route": "q",
        "message": message,
        "language": "english",
        "flash": 0,
        "numbers": to_phone_number
    }
    headers = {
        "authorization": FAST2SMS_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Fake Call Integration
call_scheduled = False

@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    buses = [
        {'id': 1, 'name': 'Gov(Pink) 505', 'from': 'Koyambedu', 'to': 'T.Nagar', 'time': '5 mins'},
        {'id': 2, 'name': 'Gov(AC) 515', 'from': 'Kelambakkam', 'to': 'Kilambakkam', 'time': '7 mins'},
        {'id': 1, 'name': 'Gov(Pink) 505', 'from': 'Koyambedu', 'to': 'T.Nagar', 'time': '9 mins'},
        {'id': 3, 'name': 'Gov(Nor) 19', 'from': 'Vadapalani', 'to': 'T.Nagar', 'time': '12 mins'},
        {'id': 4, 'name': 'Gov(Nor) 12b', 'from': 'Kovalam', 'to': 'Tambaram', 'time': '15 mins'},
    ]

    filtered_buses = buses  # Default to all buses

    if request.method == 'POST':
        from_location = request.form.get('from', '').strip()
        to_location = request.form.get('to', '').strip()

        if from_location and to_location:
            filtered_buses = [bus for bus in buses if bus['from'].lower() == from_location.lower() and bus['to'].lower() == to_location.lower()]
            if not filtered_buses:
                flash('No buses found for the given route.', 'warning')

    return render_template('home.html', buses=filtered_buses, call_scheduled=call_scheduled)

@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')

@app.route('/bus/<int:bus_id>')
@login_required
def bus_details(bus_id):
    if bus_id == 1:
        # Define stops
        stops = ['Koyambedu', 'Vadapalani', 'Ashok Pillar', 'Guindy', 'Saidapet', 'T.Nagar']
        
        # Bus capacity details
        max_capacity = 40
        current_passengers = 30  # Starting number of passengers
        available_seats = max(0, max_capacity - current_passengers)

        # Simulate real-time passenger movement
        bus_stops = []
        current_stop_idx = 0  # Assume bus is at Koyambedu (first stop)

        for i, stop in enumerate(stops):
            stop_data = {
                'name': stop,
                'is_current': i == current_stop_idx,
                'is_user_stop': stop == 'Saidapet',  # Hardcoded user stop as in original
                'is_final': i == len(stops) - 1
            }

            if stop_data['is_final']:
                continue  # Skip final stop for detailed stats

            if stop_data['is_user_stop']:
                # For user's stop, only show potential seats
                stop_data['potential_seats'] = available_seats
            else:
                # Predict waiting passengers using the XGBoost model
                stop_features = pd.get_dummies(pd.DataFrame([[stop, stop]], columns=['Boarding_Stop', 'Destination_Stop']))
                stop_features = stop_features.reindex(columns=feature_columns, fill_value=0)
                predicted_waiting = int(round(xgb_model.predict(stop_features)[0]))

                # Simulate passenger movements
                actual_getting_off = np.random.randint(8, 10)
                actual_passengers_boarding = np.random.randint(12, 16)

                # Update passenger count
                current_passengers += actual_passengers_boarding - actual_getting_off
                available_seats = max(0, max_capacity - current_passengers)
                standing = max(0, current_passengers - max_capacity)

                # Add details to stop
                stop_data['predicted_waiting'] = predicted_waiting
                stop_data['getting_off'] = actual_getting_off
                stop_data['boarding'] = actual_passengers_boarding
                stop_data['current_passengers'] = current_passengers
                stop_data['available_seats'] = available_seats
                stop_data['standing'] = standing

            bus_stops.append(stop_data)

        # Add the final stop
        bus_stops.append({
            'name': 'T.Nagar',
            'is_current': False,
            'is_user_stop': False,
            'is_final': True
        })

        bus_data = {
            'name': 'Gov(Pink) 505',
            'from': 'Koyambedu',
            'to': 'Adyar',
            'stops': bus_stops
        }
        return render_template('bus_details.html', bus=bus_data)
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.get_user_by_email(email)
            session['user_id'] = user.uid
            return redirect(url_for('home'))
        except:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            user = auth.create_user(
                email=request.form.get('email'),
                password=request.form.get('password')
            )
            user_data = {
                'username': request.form.get('username'),
                'email': request.form.get('email'),
                'phone': request.form.get('phone'),
                'age': request.form.get('age'),
                'gender': request.form.get('gender'),
                'emergency': {
                    'name': request.form.get('emergency_name'),
                    'phone': request.form.get('emergency_phone')
                },
                'created_at': datetime.now()
            }
            db.collection('users').document(user.uid).set(user_data)
            flash('Account created successfully')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error creating account')
    return render_template('signup.html')

@app.route('/profile')
@login_required
def profile():
    user_doc = db.collection('users').document(session['user_id']).get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return render_template('profile.html', user=user_data)
    flash("User data not found!")
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/sos')
@login_required
def sos():
    return render_template('sos.html')

@app.route('/send_sos', methods=['POST'])
@login_required
def send_sos():
    data = request.json
    phone_number = data.get("phone")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not phone_number or not latitude or not longitude:
        return jsonify({"error": "Missing required parameters"}), 400

    response = send_sos_sms(phone_number, latitude, longitude)
    return jsonify(response)

# Fake Call Routes
@app.route('/fake_call')
@login_required
def fake_call():
    global call_scheduled
    return render_template('fake_call.html', call_scheduled=call_scheduled)

@app.route('/trigger_call', methods=['POST'])
@login_required
def trigger_call():
    global call_scheduled
    if not call_scheduled:
        call_scheduled = True
        # Schedule the call to "ring" after 5 seconds
        threading.Timer(5.0, start_call).start()
        return render_template('fake_call.html', message="Call scheduled in 5 seconds!", call_scheduled=True)
    return render_template('fake_call.html', message="A call is already scheduled!", call_scheduled=True)

def start_call():
    global call_scheduled
    call_scheduled = False

@app.route('/check_call')
@login_required
def check_call():
    global call_scheduled
    if not call_scheduled and request.args.get('triggered') == 'true':
        caller_name = "Tamil Nadu Friend"
        return jsonify({'ringing': True, 'message': f"Incoming Call from: {caller_name}"})
    return jsonify({'ringing': False, 'message': "Waiting for scheduled call...", 'call_scheduled': call_scheduled})

# Bus Tracking Route
@app.route('/bus_tracking')
@login_required
def bus_tracking():
    # Fetch user data from Firestore
    user_doc = db.collection('users').document(session['user_id']).get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return render_template('bus_tracking.html', user=user_data)
    flash("User data not found!", "error")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)