# SchemeAI: AI-Powered Government Scheme Recommendation System

SchemeAI is a modern, production-quality, full-stack web application designed to help Indian citizens discover, check eligibility for, compare, and apply for Central and State Government Schemes using Machine Learning.

## Features

- **AI Recommendation Engine**: A Multi-Output Random Forest Classifier trained on encoded profile details to predict eligibility match probabilities.
- **Rules Matching & Eligibility Checker**: Double-checks citizen inputs against strict scheme rules (age, income caps, location, caste, BPL/APL cards) to verify matches with 100% precision.
- **Scheme Comparison Matrix**: Compare up to three schemes side-by-side on departments, eligibility limits, benefits, and link modes.
- **Benefits Calculator Suite**: Dynamic calculators with Chart.js visualization:
  - Scholarship allowance estimator.
  - Atal Pension Projection.
  - Business subsidy estimator.
  - Mudra Loan eligibility calculator.
  - PMAY Housing Grant calculator.
- **Interactive Chatbot**: Local semantic helper answering queries about applications, required documents, and dashboard tools.
- **Multilingual Support**: Supports English, Hindi, and Marathi translations.
- **Voice Search**: Real-time voice query inputs leveraging HTML5 SpeechRecognition.
- **User Dashboard**: Save bookmarks, track check logs, examine notifications, and download PDF matching reports.
- **Administrative Portal**: Secure CRUD controls, CSV batch imports, user database directories, and dynamic registration metrics.

---

## Technical Stack

- **Frontend**: HTML5, CSS3 (Custom Design system), JavaScript (ES6), Bootstrap 5, Font Awesome, Chart.js, html2pdf.js, Google Fonts (Poppins)
- **Backend**: Python, Flask Micro-Framework
- **Database**: SQLite3 (compatible with MySQL/PostgreSQL)
- **Machine Learning**: Scikit-Learn (Random Forest), Pandas, NumPy, Joblib

---

## Local Installation Setup

Follow these steps to run SchemeAI locally on your system:

### 1. Set Up Environment & Install Dependencies
Create a virtual environment (optional but recommended) and install packages:
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Initialize Database & Seed Scheme Entries
Create the local SQLite database (`database/schemeai.db`), categories, documents, default admin, and seed the master schemes:
```bash
python db_init.py
```

### 3. Train the AI Recommendation Classifier
Run the trainer script to generate synthetic user profiles and save the Random Forest pipeline:
```bash
python models/model_trainer.py
```

### 4. Boot the Flask Web Server
Start the local server (default port `5000`):
```bash
python app.py
```
Open `http://127.0.0.1:5000/` in your browser.

---

## System Login Credentials

- **System Admin Login**:
  - Email: `admin@schemeai.com`
  - Password: `admin123`
  
- **Citizen Account**:
  - Register a new account via the UI to pre-populate custom user dashboard panels.

---

## Production Deployment to Render

This repository is pre-configured for Render deployment:
- **Build Command**: `pip install -r requirements.txt && python db_init.py && python models/model_trainer.py`
- **Start Command**: `gunicorn app:app`
- **Environment**: Set `SECRET_KEY` in Render configuration settings if desired.
