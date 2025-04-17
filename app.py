from flask import Flask, render_template, request, redirect, flash
from flask_mail import Mail, Message
import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
import folium
import random
import string
import datetime
from flask import send_file
from smtplib import SMTPAuthenticationError  # Import the exception

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hrishikeshsuchindra@gmail.com'
app.config['MAIL_PASSWORD'] = 'hrishikesh06072004'  # Replace with app-specific password

mail = Mail(app)

# Generate OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    try:
        msg = Message('Your OTP for Sign In', sender='hrishikeshsuchindra@gmail.com', recipients=[email])
        msg.body = f'Your OTP is: {otp}'
        mail.send(msg)
    except SMTPAuthenticationError:
        flash("Failed to send OTP email due to email authentication error. Please contact support.")
        print("Authentication error: Check email settings and ensure app-specific password is correct.")
    except Exception as e:
        flash("An error occurred while sending OTP. Please try again later.")
        print(f"Error: {e}")

def calculate_distances(infected_coordinates, students_data):
    tree = BallTree(infected_coordinates)
    student_coordinates = students_data[['X', 'Y']].values
    distances, _ = tree.query(student_coordinates)
    return distances

def contact_tracing(infected_person_path, students_data, threshold_distance):
    infected_person_path['Timestamp'] = pd.to_datetime(infected_person_path['Timestamp'], format='%d/%m/%Y %H:%M:%S')
    students_data['Timestamp'] = pd.to_datetime(students_data['Timestamp'], format='%d/%m/%Y %H:%M:%S')
    infected_coordinates = infected_person_path[['X', 'Y']].values
    distances = calculate_distances(infected_coordinates, students_data)
    infected_students = students_data[distances < threshold_distance]
    return infected_students

def preprocess_data(data):
    data['Timestamp'] = pd.to_datetime(data['Timestamp'], format='%d/%m/%Y %H:%M:%S')
    return data

def generate_student_id():
    prefix = '22'
    department = random.choice(['BCE', 'BRS', 'BAI'])
    numbers = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{department}{numbers}"

def generate_timestamps(freq):
    return pd.date_range(start=datetime.datetime.now(), periods=3, freq=freq)

@app.route('/')
def home():
    email = 'hrishikeshsuchindra@gmail.com'  # Specify the recipient email address here
    otp = generate_otp()
    send_otp_email(email, otp)
    flash('OTP has been sent to your email address.')
    return render_template('index.html')

@app.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        user_lat = request.form.get('lat')
        user_lng = request.form.get('lng')

        # Mock infected person path data
        infected_person_path_data = {
            'Timestamp': generate_timestamps('15min'),
            'X': [float(user_lat)],  # Use user-provided latitude
            'Y': [float(user_lng)],  # Use user-provided longitude
        }

        students_data = {
            'StudentID': [generate_student_id() for _ in range(500)],
            'Name': [f'Stu_{i}' for i in range(1, 501)],
            'Timestamp': [datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S') for _ in range(500)],
            'X': np.random.uniform(0, 1, 500) * 0.05 + 12.9668,
            'Y': np.random.uniform(0, 1, 500) * 0.05 + 80.2206,
        }

        THRESHOLD_DISTANCE = 0.01  # Adjust threshold distance for circular boundary

        infected_person_path = preprocess_data(pd.DataFrame(infected_person_path_data))
        students_data = preprocess_data(pd.DataFrame(students_data))

        infected_students = contact_tracing(infected_person_path, students_data, THRESHOLD_DISTANCE)

        students_data['InfectionStatus'] = 'Non-Infected'
        students_data.loc[students_data['StudentID'].isin(infected_students['StudentID']), 'InfectionStatus'] = 'Potentially Infected'

        # Save the students' data to a CSV file
        output_filename = 'contact_tracing_results.csv'
        students_data.to_csv(output_filename, index=False)

        # Create a map visualization
        my_map = folium.Map(location=[float(user_lat), float(user_lng)], zoom_start=15)
        folium.Marker(location=[float(user_lat), float(user_lng)], tooltip='Your Location', icon=folium.Icon(color='blue')).add_to(my_map)

        # Add markers for infected person's path
        folium.PolyLine(locations=infected_person_path[['X', 'Y']].values, color='red', weight=2.5, opacity=1).add_to(my_map)

        # Save the map to an HTML file
        map_filename = 'map_visualization.html'
        my_map.save(map_filename)

        return render_template('results.html', filename=output_filename, map_filename=map_filename)

    return render_template('results.html')

@app.route('/view_csv')
def view_csv():
    df = pd.read_csv("contact_tracing_results.csv")
    return render_template('csvcontents.html', data=df.to_html())

@app.route('/map_visualization')
def map_visualization():
    map_file = "map_visualization.html"
    return send_file(map_file)

if __name__ == '__main__':
    app.run(debug=True)
