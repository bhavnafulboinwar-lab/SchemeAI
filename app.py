import os
import sqlite3
import json
import pandas as pd
import joblib
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from config import Config
from models.chatbot_responder import respond_to_query

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Helper
def get_db_connection():
    conn = sqlite3.connect(app.config['DB_PATH'])
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Security Middleware: Custom CSRF Protection
import secrets
@app.before_request
def csrf_protection():
    # Generate CSRF token for session if not present
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(24)
        
    # Check POST requests for CSRF token
    if request.method == 'POST':
        # Exclude API endpoints from CSRF if called asynchronously from scripts
        # (Though we can still validate csrf via headers, standard APIs are fine without form tokens in mock project)
        if request.path.startswith('/api/'):
            return
            
        token = request.form.get('csrf_token')
        if not token or token != session.get('csrf_token'):
            abort(400, "CSRF verification failed. Token mismatch or missing.")

@app.context_processor
def inject_csrf_token():
    def csrf_token():
        return session.get('csrf_token', '')
    return dict(csrf_token=csrf_token)

# Context Injection for Navigation active page
@app.context_processor
def inject_active_page():
    return dict(active_page=request.endpoint)

# Helper to fetch all categories
def fetch_categories():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()
    return categories

# Helper to execute strict eligibility logic
def check_strict_eligibility(profile, scheme):
    scorecard = []
    eligible = True
    partially_eligible = False
    
    # 1. Age Rule
    age = int(profile['age'])
    min_age = int(scheme['min_age'])
    max_age = int(scheme['max_age'])
    age_ok = min_age <= age <= max_age
    scorecard.append({
        "name": "Age Target",
        "user": f"{age} Years",
        "required": f"{min_age} to {max_age} Years",
        "status": "Match" if age_ok else "Fail"
    })
    if not age_ok:
        eligible = False

    # 2. Gender Rule
    gender = profile['gender']
    gender_target = scheme['gender_target']
    gender_ok = gender_target == 'All' or gender == gender_target
    scorecard.append({
        "name": "Gender Target",
        "user": gender,
        "required": gender_target,
        "status": "Match" if gender_ok else "Fail"
    })
    if not gender_ok:
        eligible = False

    # 3. Income Rule
    income = float(profile['income'])
    max_income = float(scheme['max_income'])
    income_ok = income <= max_income
    scorecard.append({
        "name": "Annual Income Limit",
        "user": f"₹{int(income)}",
        "required": "No Limit" if max_income >= 10000000 else f"<= ₹{int(max_income)}",
        "status": "Match" if income_ok else "Fail"
    })
    if not income_ok:
        eligible = False

    # 4. State Rule
    state = profile['state']
    scheme_state = scheme['state']
    state_ok = scheme_state == 'All' or state == scheme_state
    scorecard.append({
        "name": "State Restriction",
        "user": state,
        "required": scheme_state,
        "status": "Match" if state_ok else "Fail"
    })
    if not state_ok:
        eligible = False

    # 5. Disability Rule
    disability = profile['disability_status']
    disability_required = scheme['disability_required']
    disability_ok = disability_required == 'No' or disability == 'Yes'
    scorecard.append({
        "name": "Disability Match",
        "user": disability,
        "required": f"Disability Req: {disability_required}",
        "status": "Match" if disability_ok else "Fail"
    })
    if not disability_ok:
        eligible = False

    # 6. BPL Rule
    bpl = profile['bpl_status']
    bpl_required = scheme['bpl_required']
    bpl_ok = bpl_required == 'No' or bpl == 'Yes'
    scorecard.append({
        "name": "BPL Card Match",
        "user": bpl,
        "required": f"BPL Card Req: {bpl_required}",
        "status": "Match" if bpl_ok else "Fail"
    })
    if not bpl_ok:
        eligible = False

    # Determine status
    match_count = sum(1 for item in scorecard if item['status'] == 'Match')
    if match_count == len(scorecard):
        status = "Eligible"
    elif match_count >= 4:
        status = "Partially Eligible"
    else:
        status = "Not Eligible"
        
    return {
        "status": status,
        "scorecard": scorecard
    }

# ==========================================================================
# Core Web Page Routes
# ==========================================================================

@app.route('/')
def home():
    conn = get_db_connection()
    popular_schemes = conn.execute("SELECT * FROM schemes LIMIT 3").fetchall()
    categories = conn.execute("SELECT * FROM categories LIMIT 7").fetchall()
    
    # Bookmarks list
    bookmarked_ids = []
    if 'user_id' in session:
        bookmarks = conn.execute("SELECT scheme_id FROM bookmarks WHERE user_id = ?", (session['user_id'],)).fetchall()
        bookmarked_ids = [b['scheme_id'] for b in bookmarks]
        
    conn.close()
    return render_template('home.html', popular_schemes=popular_schemes, categories=categories, bookmarked_ids=bookmarked_ids)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/schemes')
def schemes():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories").fetchall()
    
    # Read filter query params
    search_query = request.args.get('search', '').strip()
    selected_type = request.args.get('type', '')
    selected_category = request.args.get('category', '')
    selected_occupation = request.args.get('occupation', '')
    selected_state = request.args.get('state', '')
    selected_gender = request.args.get('gender', '')
    selected_income = request.args.get('income', '')
    sort_by = request.args.get('sort', 'name_asc')

    # Construct sql query
    query = "SELECT * FROM schemes WHERE 1=1"
    params = []

    if search_query:
        query += " AND (name LIKE ? OR description LIKE ? OR department LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])
        
    if selected_type:
        query += " AND type = ?"
        params.append(selected_type)
        
    if selected_category:
        query += " AND category = ?"
        params.append(selected_category)
        
    if selected_state:
        query += " AND (state = 'All' OR state = ?)"
        params.append(selected_state)
        
    if selected_occupation:
        query += " AND (occupation_target = 'All' OR occupation_target = ?)"
        params.append(selected_occupation)
        
    if selected_gender:
        query += " AND (gender_target = 'All' OR gender_target = ?)"
        params.append(selected_gender)
        
    if selected_income:
        query += " AND max_income <= ?"
        params.append(float(selected_income))

    # Apply sorting
    if sort_by == 'name_desc':
        query += " ORDER BY name DESC"
    elif sort_by == 'category':
        query += " ORDER BY category ASC"
    else:
        query += " ORDER BY name ASC"

    schemes_list = conn.execute(query, params).fetchall()
    
    # Bookmarks checking
    bookmarked_ids = []
    if 'user_id' in session:
        bookmarks = conn.execute("SELECT scheme_id FROM bookmarks WHERE user_id = ?", (session['user_id'],)).fetchall()
        bookmarked_ids = [b['scheme_id'] for b in bookmarks]

    conn.close()
    return render_template('schemes.html', 
                           schemes=schemes_list, 
                           categories=categories,
                           search_query=search_query,
                           selected_type=selected_type,
                           selected_category=selected_category,
                           selected_occupation=selected_occupation,
                           selected_state=selected_state,
                           selected_gender=selected_gender,
                           selected_income=selected_income,
                           sort_by=sort_by,
                           bookmarked_ids=bookmarked_ids)

@app.route('/scheme/<int:scheme_id>')
def scheme_details(scheme_id):
    conn = get_db_connection()
    scheme = conn.execute("SELECT * FROM schemes WHERE id = ?", (scheme_id,)).fetchone()
    
    if not scheme:
        conn.close()
        abort(404, "Scheme not found")
        
    bookmarked_ids = []
    if 'user_id' in session:
        bookmarks = conn.execute("SELECT scheme_id FROM bookmarks WHERE user_id = ?", (session['user_id'],)).fetchall()
        bookmarked_ids = [b['scheme_id'] for b in bookmarks]
        
    conn.close()
    return render_template('scheme_details.html', scheme=scheme, bookmarked_ids=bookmarked_ids)

@app.route('/recommend')
def recommend():
    # If user logged in, load profile to prefill wizard
    user_profile = None
    if 'user_id' in session:
        conn = get_db_connection()
        user_profile = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        conn.close()
        
    return render_template('recommend.html', user=user_profile)

@app.route('/eligibility', methods=['GET', 'POST'])
def eligibility():
    conn = get_db_connection()
    schemes_list = conn.execute("SELECT id, name FROM schemes ORDER BY name ASC").fetchall()
    
    selected_scheme = None
    eligibility_result = None
    profile = None
    
    # If preset via GET
    scheme_id_preset = request.args.get('scheme_id')
    if scheme_id_preset:
        selected_scheme = conn.execute("SELECT * FROM schemes WHERE id = ?", (int(scheme_id_preset),)).fetchone()
        
    # Check if user logged in, prefill fields
    if 'user_id' in session:
        profile = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()

    if request.method == 'POST':
        scheme_id = int(request.form.get('scheme_id'))
        selected_scheme = conn.execute("SELECT * FROM schemes WHERE id = ?", (scheme_id,)).fetchone()
        
        profile = {
            "age": int(request.form.get('age')),
            "gender": request.form.get('gender'),
            "state": request.form.get('state'),
            "occupation": request.form.get('occupation'),
            "income": float(request.form.get('income')),
            "bpl_status": request.form.get('bpl_status'),
            "disability_status": request.form.get('disability_status'),
            "education": request.form.get('education')
        }
        
        # Perform eligibility rules check
        eligibility_result = check_strict_eligibility(profile, selected_scheme)
        
        # Save history if logged in
        if 'user_id' in session:
            conn.execute("""
                INSERT INTO eligibility_history (user_id, scheme_id, status, missing_criteria)
                VALUES (?, ?, ?, ?)
            """, (
                session['user_id'],
                scheme_id,
                eligibility_result['status'],
                json.dumps([score for score in eligibility_result['scorecard'] if score['status'] == 'Fail'])
            ))
            conn.commit()

    conn.close()
    return render_template('eligibility.html', 
                           schemes_list=schemes_list, 
                           selected_scheme=selected_scheme, 
                           eligibility_result=eligibility_result,
                           profile=profile)

@app.route('/compare')
def compare():
    conn = get_db_connection()
    schemes_list = conn.execute("SELECT id, name FROM schemes ORDER BY name ASC").fetchall()
    
    s1_id = request.args.get('s1')
    s2_id = request.args.get('s2')
    s3_id = request.args.get('s3')
    
    s1 = conn.execute("SELECT * FROM schemes WHERE id = ?", (s1_id,)).fetchone() if s1_id else None
    s2 = conn.execute("SELECT * FROM schemes WHERE id = ?", (s2_id,)).fetchone() if s2_id else None
    s3 = conn.execute("SELECT * FROM schemes WHERE id = ?", (s3_id,)).fetchone() if s3_id else None
    
    conn.close()
    return render_template('compare.html', schemes_list=schemes_list, s1=s1, s2=s2, s3=s3)

@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

@app.route('/documents')
def documents():
    conn = get_db_connection()
    docs = conn.execute("SELECT * FROM documents").fetchall()
    conn.close()
    return render_template('documents.html', documents_list=docs)

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        rating = int(request.form.get('rating'))
        message = request.form.get('message')
        
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO feedback (name, email, rating, message)
            VALUES (?, ?, ?, ?)
        """, (name, email, rating, message))
        conn.commit()
        conn.close()
        
        flash("Thank you for your feedback! Your submission was recorded successfully.", "success")
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

# ==========================================================================
# User Auth Routes
# ==========================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session or 'admin_id' in session:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password')
        role = request.form.get('role') # user or admin
        
        conn = get_db_connection()
        
        if role == 'admin':
            admin = conn.execute("SELECT * FROM admins WHERE email = ?", (email,)).fetchone()
            if admin and check_password_hash(admin['password_hash'], password):
                session['admin_id'] = admin['id']
                session['admin_name'] = admin['name']
                session['admin_email'] = admin['email']
                flash("Admin logged in successfully.", "success")
                conn.close()
                return redirect(url_for('admin'))
        else:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                flash(f"Welcome back, {user['name']}!", "success")
                conn.close()
                return redirect(url_for('dashboard'))
                
        conn.close()
        flash("Invalid email or password. Please try again.", "error")
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session or 'admin_id' in session:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        name = request.form.get('name').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Profile details
        age = request.form.get('age')
        gender = request.form.get('gender')
        state = request.form.get('state')
        occupation = request.form.get('occupation')
        income = request.form.get('income')
        education = request.form.get('education')
        category = request.form.get('category')
        bpl_status = request.form.get('bpl_status', 'No')
        disability_status = request.form.get('disability_status', 'No')
        
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('register'))
            
        conn = get_db_connection()
        # Check email uniqueness
        existing_user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing_user:
            conn.close()
            flash("An account with that email already exists.", "error")
            return redirect(url_for('register'))
            
        pass_hash = generate_password_hash(password)
        
        conn.execute("""
            INSERT INTO users (
                name, email, password_hash, age, gender, state, occupation, income,
                education, category, bpl_status, disability_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, email, pass_hash, 
            int(age) if age else None,
            gender if gender else None,
            state if state else None,
            occupation if occupation else None,
            float(income) if income else None,
            education if education else None,
            category if category else None,
            bpl_status, disability_status
        ))
        conn.commit()
        
        # Add welcome notification
        new_user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute("""
            INSERT INTO notifications (user_id, title, message)
            VALUES (?, 'Welcome to SchemeAI!', 'Fill out your dashboard parameters or complete the AI Recommendation form to discover eligible schemes.')
        """, (new_user_id,))
        conn.commit()
        conn.close()
        
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email').strip()
        # Mock recovery
        flash(f"If an account with email {email} exists, password reset guidelines have been sent.", "success")
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have logged out successfully.", "success")
    return redirect(url_for('home'))

# ==========================================================================
# Dashboards and Profile Management
# ==========================================================================

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please login to view dashboard.", "warning")
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    # Bookmarks
    bookmarks = conn.execute("""
        SELECT s.* FROM schemes s
        JOIN bookmarks b ON s.id = b.scheme_id
        WHERE b.user_id = ?
    """, (session['user_id'],)).fetchall()
    
    # Recommendations
    recs_raw = conn.execute("""
        SELECT * FROM recommendations WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (session['user_id'],)).fetchall()
    
    recommendations = []
    for r in recs_raw:
        scheme_ids = r['recommended_scheme_ids'].split(',')
        recommendations.append({
            "timestamp": r['timestamp'],
            "inputs": json.loads(r['inputs']),
            "scheme_count": len(scheme_ids)
        })
        
    # Eligibility History
    history_raw = conn.execute("""
        SELECT h.*, s.name as scheme_name FROM eligibility_history h
        JOIN schemes s ON h.scheme_id = s.id
        WHERE h.user_id = ?
        ORDER BY h.checked_at DESC
    """, (session['user_id'],)).fetchall()
    
    # Notifications
    notifications = conn.execute("""
        SELECT * FROM notifications 
        WHERE user_id IS NULL OR user_id = ? 
        ORDER BY created_at DESC
    """, (session['user_id'],)).fetchall()
    
    conn.close()
    return render_template('dashboard.html', 
                           user=user, 
                           bookmarks=bookmarks,
                           recommendations=recommendations,
                           history=history_raw,
                           notifications=notifications)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    name = request.form.get('name').strip()
    age = request.form.get('age')
    gender = request.form.get('gender')
    state = request.form.get('state')
    occupation = request.form.get('occupation')
    income = request.form.get('income')
    education = request.form.get('education')
    category = request.form.get('category')
    bpl_status = request.form.get('bpl_status')
    disability_status = request.form.get('disability_status')
    
    conn = get_db_connection()
    conn.execute("""
        UPDATE users SET
            name = ?, age = ?, gender = ?, state = ?, occupation = ?,
            income = ?, education = ?, category = ?, bpl_status = ?, disability_status = ?
        WHERE id = ?
    """, (
        name,
        int(age) if age else None,
        gender if gender else None,
        state if state else None,
        occupation if occupation else None,
        float(income) if income else None,
        education if education else None,
        category if category else None,
        bpl_status, disability_status,
        session['user_id']
    ))
    conn.commit()
    conn.close()
    
    flash("Profile settings updated successfully.", "success")
    return redirect(url_for('dashboard'))

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (session['user_id'],))
    conn.commit()
    conn.close()
    
    session.clear()
    flash("Your account and all associated data have been permanently deleted.", "success")
    return redirect(url_for('home'))

# ==========================================================================
# Admin Portal & CRUD Routes
# ==========================================================================

@app.route('/admin')
def admin():
    if 'admin_id' not in session:
        flash("Unauthorized access. Admin privileges required.", "error")
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    
    # 1. Base counts
    user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    scheme_count = conn.execute("SELECT COUNT(*) FROM schemes").fetchone()[0]
    feedback_count = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
    
    # 2. Lists for CRUD & search
    schemes_list = conn.execute("SELECT * FROM schemes ORDER BY id DESC").fetchall()
    users_list = conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    feedbacks_list = conn.execute("SELECT * FROM feedback ORDER BY submitted_at DESC").fetchall()
    categories = conn.execute("SELECT * FROM categories").fetchall()
    
    # 3. Analytics charts parameters
    cat_counts = conn.execute("SELECT category, COUNT(*) FROM schemes GROUP BY category").fetchall()
    cat_labels = [row[0] for row in cat_counts]
    cat_values = [row[1] for row in cat_counts]
    
    type_counts = conn.execute("SELECT type, COUNT(*) FROM schemes GROUP BY type").fetchall()
    type_labels = [row[0] for row in type_counts]
    type_values = [row[1] for row in type_counts]
    
    conn.close()
    
    stats = {
        "users": user_count,
        "schemes": scheme_count,
        "feedback": feedback_count,
        "cat_labels": cat_labels,
        "cat_values": cat_values,
        "type_labels": type_labels,
        "type_values": type_values
    }
    
    return render_template('admin.html', 
                           stats=stats, 
                           schemes_list=schemes_list, 
                           users_list=users_list, 
                           feedbacks_list=feedbacks_list,
                           categories=categories)

@app.route('/admin/add-scheme', methods=['POST'])
def admin_add_scheme():
    if 'admin_id' not in session:
        abort(403)
        
    name = request.form.get('name')
    department = request.form.get('department')
    category = request.form.get('category')
    type_scheme = request.form.get('type')
    state = request.form.get('state')
    min_age = int(request.form.get('min_age', 0))
    max_age = int(request.form.get('max_age', 120))
    gender_target = request.form.get('gender_target', 'All')
    max_income = float(request.form.get('max_income', 10000000))
    occupation_target = request.form.get('occupation_target', 'All')
    disability_required = request.form.get('disability_required', 'No')
    bpl_required = request.form.get('bpl_required', 'No')
    benefits = request.form.get('benefits')
    required_documents = request.form.get('required_documents')
    official_link = request.form.get('official_link')
    image_url = request.form.get('image_url')
    description = request.form.get('description')
    
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO schemes (
            name, department, category, type, state, min_age, max_age,
            gender_target, max_income, occupation_target, disability_required, bpl_required,
            benefits, required_documents, official_link, image_url, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, department, category, type_scheme, state, min_age, max_age,
        gender_target, max_income, occupation_target, disability_required, bpl_required,
        benefits, required_documents, official_link, image_url, description
    ))
    conn.commit()
    conn.close()
    
    flash("New scheme added successfully.", "success")
    return redirect(url_for('admin'))

@app.route('/admin/delete-scheme/<int:scheme_id>')
def admin_delete_scheme(scheme_id):
    if 'admin_id' not in session:
        abort(403)
        
    conn = get_db_connection()
    conn.execute("DELETE FROM schemes WHERE id = ?", (scheme_id,))
    conn.commit()
    conn.close()
    
    flash("Scheme deleted successfully.", "success")
    return redirect(url_for('admin'))

@app.route('/admin/upload-csv', methods=['POST'])
def admin_upload_csv():
    if 'admin_id' not in session:
        abort(403)
        
    file = request.files.get('csv_file')
    if not file or file.filename == '':
        flash("Please upload a valid CSV file.", "error")
        return redirect(url_for('admin'))
        
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            df = pd.read_csv(filepath)
            
            # Basic schema columns check
            required_cols = ['name', 'department', 'category', 'type', 'state', 'benefits', 'required_documents', 'official_link', 'description']
            for col in required_cols:
                if col not in df.columns:
                    flash(f"CSV import failed. Missing mandatory column: {col}", "error")
                    return redirect(url_for('admin'))
            
            conn = get_db_connection()
            
            # Insert each row
            for _, row in df.iterrows():
                # Check duplicates by name
                existing = conn.execute("SELECT id FROM schemes WHERE name = ?", (row['name'],)).fetchone()
                if not existing:
                    # Provide defaults for numerical bounds
                    min_age = int(row.get('min_age', 0))
                    max_age = int(row.get('max_age', 120))
                    max_income = float(row.get('max_income', 10000000))
                    gender_target = row.get('gender_target', 'All')
                    occupation_target = row.get('occupation_target', 'All')
                    disability = row.get('disability_required', 'No')
                    bpl = row.get('bpl_required', 'No')
                    image_url = row.get('image_url', '/static/images/pm_kisan.jpg')
                    
                    conn.execute("""
                        INSERT INTO schemes (
                            name, department, category, type, state, min_age, max_age,
                            gender_target, max_income, occupation_target, disability_required, bpl_required,
                            benefits, required_documents, official_link, image_url, description
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row['name'], row['department'], row['category'], row['type'], row['state'],
                        min_age, max_age, gender_target, max_income, occupation_target, disability, bpl,
                        row['benefits'], row['required_documents'], row['official_link'], image_url, row['description']
                    ))
                    
                    # Ensure category category exists in categories table
                    conn.execute("INSERT OR IGNORE INTO categories (name, description, icon) VALUES (?, ?, ?)",
                                 (row['category'], f"{row['category']} welfare options.", "fa-folder-open"))
            
            conn.commit()
            conn.close()
            os.remove(filepath)
            
            flash("CSV bulk upload processed successfully.", "success")
        except Exception as e:
            flash(f"An error occurred while parsing CSV: {str(e)}", "error")
            if os.path.exists(filepath):
                os.remove(filepath)
                
    return redirect(url_for('admin'))

@app.route('/admin/broadcast', methods=['POST'])
def admin_broadcast():
    if 'admin_id' not in session:
        abort(403)
        
    title = request.form.get('title')
    message = request.form.get('message')
    
    conn = get_db_connection()
    # Insert system alert (user_id = NULL means broadcast to everyone)
    conn.execute("""
        INSERT INTO notifications (user_id, title, message)
        VALUES (NULL, ?, ?)
    """, (title, message))
    conn.commit()
    conn.close()
    
    flash("Broadcast notification sent successfully.", "success")
    return redirect(url_for('admin'))

# ==========================================================================
# Async API Endpoints
# ==========================================================================

@app.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    data = request.get_json() or {}
    query = data.get('query', '')
    reply = respond_to_query(query)
    return jsonify({"reply": reply})

@app.route('/api/bookmark/<int:scheme_id>', methods=['POST'])
def api_bookmark(scheme_id):
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}, 401)
        
    user_id = session['user_id']
    conn = get_db_connection()
    
    # Check if exists
    bookmark = conn.execute("SELECT id FROM bookmarks WHERE user_id = ? AND scheme_id = ?",
                            (user_id, scheme_id)).fetchone()
                            
    if bookmark:
        conn.execute("DELETE FROM bookmarks WHERE user_id = ? AND scheme_id = ?", (user_id, scheme_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "removed", "message": "Scheme removed from bookmarks."})
    else:
        conn.execute("INSERT INTO bookmarks (user_id, scheme_id) VALUES (?, ?)", (user_id, scheme_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "added", "message": "Scheme bookmarked successfully."})

@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    data = request.get_json() or {}
    
    # Load ML pipeline
    model_path = os.path.join("models", "recommendation_model.joblib")
    if not os.path.exists(model_path):
        return jsonify({"message": "Recommendation engine not active. Train the model first."}, 500)
        
    try:
        # Load pipeline
        pipeline = joblib.load(model_path)
        
        # Prepare inputs
        age = int(data.get('age', 25))
        income = float(data.get('income', 150000))
        family_size = int(data.get('family_size', 4))
        
        profile = {
            "age": age,
            "gender": data.get('gender', 'Male'),
            "state": data.get('state', 'Maharashtra'),
            "occupation": data.get('occupation', 'Student'),
            "income": income,
            "education": data.get('education', 'Graduate'),
            "category": data.get('category', 'General'),
            "disability_status": data.get('disability_status', 'No'),
            "bpl_status": data.get('bpl_status', 'No'),
            "employment_status": data.get('employment_status', 'Student'),
            "family_size": family_size
        }
        
        df_new = pd.DataFrame([profile])
        
        # Get predict probabilities
        probas = pipeline.predict_proba(df_new)
        
        # Fetch schemes from database
        conn = get_db_connection()
        schemes = conn.execute("SELECT * FROM schemes ORDER BY id ASC").fetchall()
        
        matched_recs = []
        
        # Classifiers estimators mapping order matches DB order (sorted by id)
        for idx, p in enumerate(probas):
            if idx >= len(schemes):
                break
                
            scheme = schemes[idx]
            confidence = float(p[0][1]) # Class 1 (eligible) probability
            
            # Evaluate strict rules filters to override model anomalies
            strict_check = check_strict_eligibility(profile, scheme)
            
            if strict_check['status'] != "Not Eligible":
                # Only output matches where strict rules permit
                # Generate matching reason explanation
                reason = f"Fits your occupation profile as {profile['occupation']} and age bracket of {profile['age']} years."
                if scheme['id'] == 1:
                    reason = f"Excellent match for your profile as a Farmer earning ₹{int(profile['income'])} annually."
                elif scheme['id'] == 2:
                    reason = f"Tailored matching benefits for a girl child profile (Female under age 10)."
                elif scheme['id'] == 3:
                    reason = f"Recommended based on your BPL housing status and annual income."
                elif scheme['id'] == 4:
                    reason = f"Designed for student education support with family income under limits."
                elif scheme['id'] == 12:
                    reason = f"Matches state specific welfare criteria for disabled/destitutes in Maharashtra."
                    
                matched_recs.append({
                    "id": scheme['id'],
                    "name": scheme['name'],
                    "department": scheme['department'],
                    "category": scheme['category'],
                    "description": scheme['description'],
                    "benefits": scheme['benefits'],
                    "required_documents": scheme['required_documents'],
                    "official_link": scheme['official_link'],
                    "confidence": int(confidence * 100),
                    "reason": reason
                })
                
        # Sort recommendations by confidence score descending
        matched_recs = sorted(matched_recs, key=lambda x: x['confidence'], reverse=True)
        
        # Save recommendations to database if user logged in
        if 'user_id' in session:
            recommended_ids_str = ",".join([str(item['id']) for item in matched_recs])
            conn.execute("""
                INSERT INTO recommendations (user_id, inputs, recommended_scheme_ids)
                VALUES (?, ?, ?)
            """, (
                session['user_id'],
                json.dumps(profile),
                recommended_ids_str
            ))
            conn.commit()
            
        conn.close()
        return jsonify({"recommendations": matched_recs})
        
    except Exception as e:
        return jsonify({"message": f"AI evaluation error: {str(e)}"}, 500)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
