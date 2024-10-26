from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
import folium
import os
import random
import string
import datetime
from flask import send_file


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Update with your SMTP server
app.config['MAIL_PORT'] = 587  # Update with your SMTP port
app.config['MAIL_USE_TLS'] = True  # Set to True if TLS is required
app.config['MAIL_USERNAME'] = 'hrishikeshsuchindra@gmail.com'  # Update with your email username
app.config['MAIL_PASSWORD'] = 'ffbu joow zbiw fjoy'  # Update with your email password

mail = Mail(app)

# Mock user credentials (replace with your authentication logic)
valid_credentials = {'username': 'emp0607', 'password': 'qwerty@1234'}

# Generate OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    msg = Message('Your OTP for Sign In', sender='your_email@example.com', recipients=[email])
    msg.body = f'Your OTP is: {otp}'
    mail.send(msg)

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
def signin_page():
    session['otp'] = generate_otp()
    email = 'example@example.com'  # Specify the recipient email address here
    send_otp_email(email, session['otp'])
    flash('OTP has been sent to your email address.')
    return render_template('signin.html')

@app.route('/signin', methods=['POST'])
def signin():
    username = request.form.get('username')
    password = request.form.get('password')
    entered_otp = request.form.get('otp')
    
    # Validate OTP
    if entered_otp != session['otp']:
        return 'Invalid OTP. Please try again.'
    
    # Validate credentials
    if username == valid_credentials['username'] and password == valid_credentials['password']:
        # Clear OTP from session
        session.pop('otp', None)
        return redirect(url_for('index'))
    else:
        return 'Invalid username or password. Please try again.'

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/results')
def results():
    infected_person_path_data = {
        'Timestamp': generate_timestamps('15min'),
        'X': np.random.uniform(0, 1, 3) * 0.05 + 12.9668,  # Adjusted for Chennai's latitude
        'Y': np.random.uniform(0, 1, 3) * 0.05 + 80.2206,  # Adjusted for Chennai's longitude
    }

    students_data = {
        'StudentID': [generate_student_id() for _ in range(500)],
        'Name': [f'Stu_{i}' for i in range(1, 501)],
        'Timestamp': [datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S') for _ in range(500)],
        'X': np.random.uniform(0, 1, 500) * 0.05 + 12.9668,  # Adjusted for Chennai's latitude
        'Y': np.random.uniform(0, 1, 500) * 0.05 + 80.2206,  # Adjusted for Chennai's longitude
    }

    THRESHOLD_DISTANCE = 0.01  # Adjust threshold distance for circular boundary

    infected_person_path = preprocess_data(pd.DataFrame(infected_person_path_data))
    students_data = preprocess_data(pd.DataFrame(students_data))

    def visualize_results_with_map(infected_person_path, students_data, infected_students):
        # Create a folium map centered at the mean of the coordinates
        map_center = [infected_person_path['X'].mean(), infected_person_path['Y'].mean()]
        my_map = folium.Map(location=map_center, zoom_start=15)

        # Add markers for students
        for idx, row in students_data.iterrows():
            color = 'orange' if row['StudentID'] in infected_students['StudentID'].values else 'blue'
            folium.CircleMarker([row['X'], row['Y']], radius=5, color=color, fill=True, fill_color=color,
                                fill_opacity=0.7, popup=f"{row['Name']}").add_to(my_map)

        # Add markers for infected person's path
        folium.PolyLine(locations=infected_person_path[['X', 'Y']].values, color='red', weight=2.5, opacity=1).add_to(my_map)

        return my_map

    infected_students = contact_tracing(infected_person_path, students_data, THRESHOLD_DISTANCE)

    students_data['InfectionStatus'] = 'Non-Infected'
    students_data.loc[students_data['StudentID'].isin(infected_students['StudentID']), 'InfectionStatus'] = 'Potentially Infected'

    # Save the students' data to a CSV file
    output_filename = 'contact_tracing_results.csv'
    students_data.to_csv(output_filename, index=False)

    # Call the visualization function
    my_map = visualize_results_with_map(infected_person_path, students_data, infected_students)

    # Save the map to an HTML file
    map_filename = 'map_visualization.html'
    my_map.save(map_filename)

    return render_template('results.html', filename=output_filename, map_filename=map_filename)

@app.route('/view_csv')
def view_csv():
    # Assuming the CSV file is loaded into a DataFrame
    df = pd.read_csv("contact_tracing_results.csv")
    # Render template with DataFrame
    return render_template('csvcontents.html', data=df.to_html())

@app.route('/map_visualization')
def map_visualization():
    # Assuming the map file is generated in the current directory
    map_file = "map_visualization.html"
    return send_file(map_file)


if __name__ == '__main__':
    app.run(debug=True)
