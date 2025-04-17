# 📍 Contact Tracing Web App

A Flask-powered contact tracing system that uses geolocation data to identify potentially infected individuals based on proximity to a known infected path. Features OTP-based sign-in via email and visualizes contact zones using an interactive map.

---

## 🚀 Features

- 📧 **Email OTP Authentication**: Sends a 6-digit OTP to the user's email for secure login.
- 🧭 **Contact Tracing Algorithm**: Uses proximity search (BallTree from `scikit-learn`) to identify possible infections.
- 🗺️ **Interactive Map**: Generates a dynamic map with infected zones and user location using Folium.
- 📄 **CSV Export**: Outputs detailed contact tracing data as a downloadable CSV file.
- 📊 **HTML Table View**: Display the result data table inside the browser.
- 💻 **Flask Web Interface**: Simple and responsive web interface for user interaction.

---

## 🛠️ Tech Stack

- Python 3.x
- Flask
- Flask-Mail
- Pandas
- NumPy
- Scikit-learn
- Folium (for map generation)
- HTML, CSS (Jinja2 templates)

---

## 📂 Project Structure

