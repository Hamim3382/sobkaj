"""
app.py — Main Flask application for Sobkaj service marketplace.

Routes:
    /                →  Landing (redirects to login)
    /register        →  Signup form + OTP email
    /verify_otp      →  OTP verification + user INSERT
    /login           →  Authentication via raw SQL SELECT
    /logout          →  Clear session
    /worker/dashboard→  Worker dashboard (profile + skills)
    /profile_setup   →  Worker profile creation + skill selection
    /remove_skill    →  Remove a skill from worker's list
    /admin_dashboard →  Admin analytics: top workers, revenue, commissions

CRITICAL: No ORM — all DB operations use raw SQL via mysql-connector-python.
"""

import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from db_config import get_db_connection
from email_utils import generate_otp, send_otp_email

app = Flask(__name__)
app.secret_key = "sobkaj_secret_key_change_me"  # Change in production

# ── Upload config ──
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ──────────────────────────────────────────────
#  LANDING
# ──────────────────────────────────────────────
@app.route("/")
def index():
    return redirect(url_for("login"))


# ──────────────────────────────────────────────
#  REGISTER
# ──────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email     = request.form.get("email", "").strip()
        phone     = request.form.get("phone", "").strip()
        password  = request.form.get("password", "")
        confirm   = request.form.get("confirm_password", "")
        role      = request.form.get("role", "customer")

        # ── Basic validation ──
        if not full_name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        # ── Check if email already exists ──
        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("register"))

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        existing = cursor.fetchone()
        cursor.close()
        conn.close()

        if existing:
            flash("An account with this email already exists.", "warning")
            return redirect(url_for("register"))

        # ── Generate OTP and send email ──
        otp = generate_otp()

        if not send_otp_email(email, otp):
            flash("Failed to send OTP email. Check your Gmail settings.", "danger")
            return redirect(url_for("register"))

        # ── Store data temporarily in session ──
        session["reg_full_name"] = full_name
        session["reg_email"]     = email
        session["reg_phone"]     = phone
        session["reg_password"]  = generate_password_hash(password)
        session["reg_role"]      = role
        session["reg_otp"]       = otp

        flash("A verification code has been sent to your email.", "info")
        return redirect(url_for("verify_otp"))

    return render_template("register.html")


# ──────────────────────────────────────────────
#  VERIFY OTP
# ──────────────────────────────────────────────
@app.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    # Guard: must come from /register
    if "reg_otp" not in session:
        flash("Please register first.", "warning")
        return redirect(url_for("register"))

    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()

        if entered_otp == session.get("reg_otp"):
            # ── OTP matches → INSERT user with raw SQL ──
            conn = get_db_connection()
            if conn is None:
                flash("Database connection failed.", "danger")
                return redirect(url_for("verify_otp"))

            try:
                cursor = conn.cursor()
                sql = """
                    INSERT INTO users (full_name, email, password_hash, role, phone)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    session["reg_full_name"],
                    session["reg_email"],
                    session["reg_password"],
                    session["reg_role"],
                    session["reg_phone"],
                ))
                conn.commit()
                cursor.close()
                conn.close()

                # Clear registration data from session
                for key in list(session.keys()):
                    if key.startswith("reg_"):
                        session.pop(key)

                flash("Account created successfully! Please log in.", "success")
                return redirect(url_for("login"))

            except Exception as e:
                conn.rollback()
                cursor.close()
                conn.close()
                flash(f"Registration failed: {e}", "danger")
                return redirect(url_for("verify_otp"))
        else:
            flash("Invalid OTP. Please try again.", "danger")
            return redirect(url_for("verify_otp"))

    return render_template("verify_otp.html")


# ──────────────────────────────────────────────
#  LOGIN
# ──────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("login"))

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("login"))

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, full_name, email, password_hash, role FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            # ── Set session ──
            session["user_id"]   = user["user_id"]
            session["full_name"] = user["full_name"]
            session["email"]     = user["email"]
            session["role"]      = user["role"]

            flash(f"Welcome back, {user['full_name']}!", "success")

            # ── Role-based redirect ──
            if user["role"] == "worker":
                return redirect(url_for("worker_dashboard"))
            elif user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("customer_dashboard"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


# ──────────────────────────────────────────────
#  LOGOUT
# ──────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ──────────────────────────────────────────────
#  WORKER DASHBOARD
# ──────────────────────────────────────────────
@app.route("/worker/dashboard")
def worker_dashboard():
    if "user_id" not in session or session.get("role") != "worker":
        flash("Please log in as a worker.", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for("login"))

    cursor = conn.cursor(dictionary=True)

    # ── Fetch worker profile ──
    cursor.execute("""
        SELECT wp.*, u.full_name, u.email, u.phone
        FROM worker_profiles wp
        JOIN users u ON u.user_id = wp.user_id
        WHERE wp.user_id = %s
    """, (user_id,))
    profile = cursor.fetchone()

    if not profile:
        cursor.close()
        conn.close()
        flash("Please complete your profile setup first.", "info")
        return redirect(url_for("profile_setup"))

    # ── Fetch worker's current skills ──
    cursor.execute("""
        SELECT s.skill_id, s.skill_name
        FROM worker_skills ws
        JOIN skills s ON s.skill_id = ws.skill_id
        WHERE ws.worker_id = %s
    """, (user_id,))
    my_skills = cursor.fetchall()

    # ── Fetch available skills (not yet added) ──
    cursor.execute("""
        SELECT s.skill_id, s.skill_name
        FROM skills s
        WHERE s.skill_id NOT IN (
            SELECT ws.skill_id FROM worker_skills ws WHERE ws.worker_id = %s
        )
    """, (user_id,))
    available_skills = cursor.fetchall()

    # ── Fetch incoming bookings for this worker ──
    cursor.execute("""
        SELECT b.booking_id, b.service_date, b.hours_requested,
               b.total_amount, b.platform_commission, b.status,
               u.full_name AS customer_name, u.phone AS customer_phone
        FROM bookings b
        INNER JOIN users u ON u.user_id = b.customer_id
        WHERE b.worker_id = %s
        ORDER BY
            FIELD(b.status, 'pending', 'confirmed', 'completed', 'cancelled'),
            b.service_date ASC
    """, (user_id,))
    bookings = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("worker_dashboard.html",
                           profile=profile,
                           my_skills=my_skills,
                           available_skills=available_skills,
                           bookings=bookings)


# ──────────────────────────────────────────────
#  UPDATE BOOKING STATUS  (Accept / Reject)
# ──────────────────────────────────────────────
@app.route("/update_booking_status", methods=["POST"])
def update_booking_status():
    if "user_id" not in session or session.get("role") != "worker":
        flash("Please log in as a worker.", "warning")
        return redirect(url_for("login"))

    booking_id = request.form.get("booking_id")
    new_status = request.form.get("new_status")  # 'confirmed' or 'cancelled'

    if new_status not in ("confirmed", "cancelled", "completed"):
        flash("Invalid status.", "danger")
        return redirect(url_for("worker_dashboard"))

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for("worker_dashboard"))

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bookings
            SET status = %s
            WHERE booking_id = %s AND worker_id = %s
        """, (new_status, int(booking_id), session["user_id"]))
        conn.commit()
        cursor.close()
        conn.close()

        labels = {"confirmed": "accepted", "cancelled": "rejected", "completed": "marked as completed"}
        flash(f"Booking #{booking_id} {labels.get(new_status, new_status)}.", "success")
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        flash(f"Failed to update booking: {e}", "danger")

    return redirect(url_for("worker_dashboard"))


# ──────────────────────────────────────────────
#  UPDATE AVAILABILITY STATUS
# ──────────────────────────────────────────────
@app.route("/update_availability", methods=["POST"])
def update_availability():
    if "user_id" not in session or session.get("role") != "worker":
        flash("Please log in as a worker.", "warning")
        return redirect(url_for("login"))

    new_status = request.form.get("availability_status")
    if new_status not in ("available", "busy", "offline"):
        flash("Invalid availability status.", "danger")
        return redirect(url_for("worker_dashboard"))

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for("worker_dashboard"))

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE worker_profiles
            SET availability_status = %s
            WHERE user_id = %s
        """, (new_status, session["user_id"]))
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"Availability updated to '{new_status}'.", "success")
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        flash(f"Failed to update availability: {e}", "danger")

    return redirect(url_for("worker_dashboard"))


# ──────────────────────────────────────────────
#  PROFILE SETUP  (new worker onboarding)
# ──────────────────────────────────────────────
@app.route("/profile_setup", methods=["GET", "POST"])
def profile_setup():
    if "user_id" not in session or session.get("role") != "worker":
        flash("Please log in as a worker.", "warning")
        return redirect(url_for("login"))

    user_id = session["user_id"]

    if request.method == "POST":
        nid_number          = request.form.get("nid_number", "").strip()
        hourly_rate         = request.form.get("hourly_rate", "0")
        availability_status = request.form.get("availability_status", "available")
        selected_skills     = request.form.getlist("skills")  # list of skill_id strings

        # ── Handle photo upload ──
        photo_url = None
        photo_file = request.files.get("photo")
        if photo_file and photo_file.filename and allowed_file(photo_file.filename):
            ext = photo_file.filename.rsplit(".", 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{ext}"
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
            photo_file.save(save_path)
            photo_url = f"/static/uploads/{unique_name}"

        conn = get_db_connection()
        if conn is None:
            flash("Database connection failed.", "danger")
            return redirect(url_for("profile_setup"))

        try:
            cursor = conn.cursor()

            # ── INSERT into worker_profiles ──
            cursor.execute("""
                INSERT INTO worker_profiles
                    (user_id, nid_number, hourly_rate, availability_status, photo_url)
                VALUES (%s, %s, %s, %s, %s)
            """, (user_id, nid_number, hourly_rate, availability_status, photo_url))

            # ── INSERT selected skills into worker_skills ──
            for skill_id in selected_skills:
                cursor.execute("""
                    INSERT INTO worker_skills (worker_id, skill_id) VALUES (%s, %s)
                """, (user_id, int(skill_id)))

            conn.commit()
            cursor.close()
            conn.close()

            flash("Profile created successfully!", "success")
            return redirect(url_for("worker_dashboard"))

        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"Profile setup failed: {e}", "danger")
            return redirect(url_for("profile_setup"))

    # ── GET: fetch all skills for the checkbox list ──
    conn = get_db_connection()
    skills = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT skill_id, skill_name FROM skills ORDER BY skill_name")
        skills = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template("profile_setup.html", skills=skills)


# ──────────────────────────────────────────────
#  ADD SKILL  (from worker dashboard)
# ──────────────────────────────────────────────
@app.route("/add_skill", methods=["POST"])
def add_skill():
    if "user_id" not in session or session.get("role") != "worker":
        flash("Please log in as a worker.", "warning")
        return redirect(url_for("login"))

    skill_id = request.form.get("skill_id")
    if not skill_id:
        flash("Please select a skill.", "warning")
        return redirect(url_for("worker_dashboard"))

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for("worker_dashboard"))

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO worker_skills (worker_id, skill_id) VALUES (%s, %s)
        """, (session["user_id"], int(skill_id)))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Skill added!", "success")
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        flash(f"Could not add skill: {e}", "danger")

    return redirect(url_for("worker_dashboard"))


# ──────────────────────────────────────────────
#  REMOVE SKILL  (from worker dashboard)
# ──────────────────────────────────────────────
@app.route("/remove_skill", methods=["POST"])
def remove_skill():
    if "user_id" not in session or session.get("role") != "worker":
        flash("Please log in as a worker.", "warning")
        return redirect(url_for("login"))

    skill_id = request.form.get("skill_id")
    if not skill_id:
        return redirect(url_for("worker_dashboard"))

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for("worker_dashboard"))

    try:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM worker_skills WHERE worker_id = %s AND skill_id = %s
        """, (session["user_id"], int(skill_id)))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Skill removed.", "info")
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        flash(f"Could not remove skill: {e}", "danger")

    return redirect(url_for("worker_dashboard"))


# ──────────────────────────────────────────────
#  CUSTOMER DASHBOARD  (search workers via JOIN)
# ──────────────────────────────────────────────
@app.route("/customer/dashboard")
def customer_dashboard():
    if "user_id" not in session or session.get("role") != "customer":
        flash("Please log in as a customer.", "warning")
        return redirect(url_for("login"))

    search_skill = request.args.get("skill", "").strip()

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for("login"))

    cursor = conn.cursor(dictionary=True)

    # ── Fetch all skills for the search dropdown ──
    cursor.execute("SELECT skill_id, skill_name FROM skills ORDER BY skill_name")
    all_skills = cursor.fetchall()

    # ── Complex INNER JOIN + LEFT JOIN ratings for AVG(stars) ──
    if search_skill:
        cursor.execute("""
            SELECT
                u.user_id,
                u.full_name,
                u.phone,
                wp.hourly_rate,
                wp.availability_status,
                wp.photo_url,
                wp.police_verified,
                wp.brac_trained,
                GROUP_CONCAT(DISTINCT s.skill_name SEPARATOR ', ') AS skills_list,
                ROUND(AVG(r.stars), 1) AS avg_rating,
                COUNT(DISTINCT r.rating_id) AS review_count
            FROM users u
            INNER JOIN worker_profiles wp ON wp.user_id = u.user_id
            INNER JOIN worker_skills  ws ON ws.worker_id = u.user_id
            INNER JOIN skills         s  ON s.skill_id   = ws.skill_id
            LEFT  JOIN ratings        r  ON r.worker_id  = u.user_id
            WHERE u.role = 'worker'
              AND u.user_id IN (
                  SELECT ws2.worker_id
                  FROM worker_skills ws2
                  INNER JOIN skills s2 ON s2.skill_id = ws2.skill_id
                  WHERE s2.skill_name = %s
              )
            GROUP BY u.user_id, u.full_name, u.phone,
                     wp.hourly_rate, wp.availability_status,
                     wp.photo_url, wp.police_verified, wp.brac_trained
            ORDER BY avg_rating DESC, wp.hourly_rate ASC
        """, (search_skill,))
    else:
        cursor.execute("""
            SELECT
                u.user_id,
                u.full_name,
                u.phone,
                wp.hourly_rate,
                wp.availability_status,
                wp.photo_url,
                wp.police_verified,
                wp.brac_trained,
                GROUP_CONCAT(DISTINCT s.skill_name SEPARATOR ', ') AS skills_list,
                ROUND(AVG(r.stars), 1) AS avg_rating,
                COUNT(DISTINCT r.rating_id) AS review_count
            FROM users u
            INNER JOIN worker_profiles wp ON wp.user_id = u.user_id
            INNER JOIN worker_skills  ws ON ws.worker_id = u.user_id
            INNER JOIN skills         s  ON s.skill_id   = ws.skill_id
            LEFT  JOIN ratings        r  ON r.worker_id  = u.user_id
            WHERE u.role = 'worker'
            GROUP BY u.user_id, u.full_name, u.phone,
                     wp.hourly_rate, wp.availability_status,
                     wp.photo_url, wp.police_verified, wp.brac_trained
            ORDER BY avg_rating DESC, wp.hourly_rate ASC
        """)

    workers = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("customer_dashboard.html",
                           workers=workers,
                           all_skills=all_skills,
                           search_skill=search_skill)


# ──────────────────────────────────────────────
#  BOOK A WORKER  (ACID transaction demo)
# ──────────────────────────────────────────────
@app.route("/book/<int:worker_id>", methods=["POST"])
def book_worker(worker_id):
    if "user_id" not in session or session.get("role") != "customer":
        flash("Please log in as a customer.", "warning")
        return redirect(url_for("login"))

    service_date    = request.form.get("service_date", "")
    hours_requested = request.form.get("hours_requested", "1")

    if not service_date:
        flash("Please select a service date.", "danger")
        return redirect(url_for("customer_dashboard"))

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for("customer_dashboard"))

    # ──────────────────────────────────────────
    #  ACID TRANSACTION — explicit demo
    # ──────────────────────────────────────────
    try:
        # 1. BEGIN TRANSACTION
        conn.start_transaction()

        cursor = conn.cursor(dictionary=True)

        # 2. READ the worker's hourly rate
        cursor.execute("""
            SELECT hourly_rate FROM worker_profiles WHERE user_id = %s
        """, (worker_id,))
        worker = cursor.fetchone()

        if not worker:
            conn.rollback()
            cursor.close()
            conn.close()
            flash("Worker profile not found.", "danger")
            return redirect(url_for("customer_dashboard"))

        # 3. CALCULATE totals
        hours  = float(hours_requested)
        rate   = float(worker["hourly_rate"])
        total_amount        = round(rate * hours, 2)
        platform_commission = round(total_amount * 0.10, 2)  # 10 % commission

        # 4. INSERT the booking
        cursor.execute("""
            INSERT INTO bookings
                (customer_id, worker_id, service_date, hours_requested,
                 total_amount, platform_commission, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
        """, (
            session["user_id"], worker_id, service_date,
            hours, total_amount, platform_commission
        ))

        # 5. COMMIT TRANSACTION
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Booking confirmed! Total: ৳{total_amount} (incl. ৳{platform_commission} commission)", "success")

    except Exception as e:
        # 6. ROLLBACK on any error — ACID Atomicity guarantee
        conn.rollback()
        cursor.close()
        conn.close()
        flash(f"Booking failed (rolled back): {e}", "danger")

    return redirect(url_for("customer_dashboard"))


# ──────────────────────────────────────────────
#  MY BOOKINGS  (customer view)
# ──────────────────────────────────────────────
@app.route("/my_bookings")
def my_bookings():
    if "user_id" not in session or session.get("role") != "customer":
        flash("Please log in as a customer.", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for("login"))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT b.*, u.full_name AS worker_name
        FROM bookings b
        INNER JOIN users u ON u.user_id = b.worker_id
        WHERE b.customer_id = %s
        ORDER BY b.service_date DESC
    """, (session["user_id"],))
    bookings = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("my_bookings.html", bookings=bookings)


# ──────────────────────────────────────────────
#  LEAVE REVIEW  (customer rates a completed booking)
# ──────────────────────────────────────────────
@app.route("/leave_review/<int:booking_id>", methods=["GET", "POST"])
def leave_review(booking_id):
    if "user_id" not in session or session.get("role") != "customer":
        flash("Please log in as a customer.", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for("my_bookings"))

    cursor = conn.cursor(dictionary=True)

    # ── Fetch the booking (must be completed + belong to this customer) ──
    cursor.execute("""
        SELECT b.*, u.full_name AS worker_name
        FROM bookings b
        INNER JOIN users u ON u.user_id = b.worker_id
        WHERE b.booking_id = %s AND b.customer_id = %s
    """, (booking_id, session["user_id"]))
    booking = cursor.fetchone()

    if not booking:
        cursor.close()
        conn.close()
        flash("Booking not found.", "danger")
        return redirect(url_for("my_bookings"))

    if booking["status"] != "completed":
        cursor.close()
        conn.close()
        flash("You can only review completed bookings.", "warning")
        return redirect(url_for("my_bookings"))

    # ── Check if already reviewed ──
    cursor.execute("""
        SELECT rating_id FROM ratings WHERE booking_id = %s
    """, (booking_id,))
    existing_review = cursor.fetchone()

    if existing_review:
        cursor.close()
        conn.close()
        flash("You have already reviewed this booking.", "info")
        return redirect(url_for("my_bookings"))

    if request.method == "POST":
        stars       = request.form.get("stars", "5")
        review_text = request.form.get("review_text", "").strip()

        try:
            cursor.execute("""
                INSERT INTO ratings (booking_id, customer_id, worker_id, stars, review_text)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                booking_id,
                session["user_id"],
                booking["worker_id"],
                int(stars),
                review_text or None
            ))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Thank you for your review!", "success")
            return redirect(url_for("my_bookings"))
        except Exception as e:
            conn.rollback()
            cursor.close()
            conn.close()
            flash(f"Failed to submit review: {e}", "danger")
            return redirect(url_for("my_bookings"))

    cursor.close()
    conn.close()
    return render_template("leave_review.html", booking=booking)


# ──────────────────────────────────────────────
#  ADMIN DASHBOARD  (analytics & reports)
#  Requires role = 'admin'
#  ⚠  Run migration_admin_role.sql first to add
#     'admin' to the users.role ENUM.
# ──────────────────────────────────────────────
@app.route("/admin_dashboard")
def admin_dashboard():
    if "user_id" not in session or session.get("role") != "admin":
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for("login"))

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "danger")
        return redirect(url_for("login"))

    cursor = conn.cursor(dictionary=True)

    # ── Query 1: Top Workers ──────────────────────────────────────────────
    # Workers ranked by average star rating (DESC), then by completed jobs
    # (DESC). Uses GROUP BY, AVG(), COUNT(), and a conditional COUNT via CASE.
    cursor.execute("""
        SELECT
            u.user_id,
            u.full_name,
            u.phone,
            wp.hourly_rate,
            wp.availability_status,
            GROUP_CONCAT(DISTINCT s.skill_name ORDER BY s.skill_name SEPARATOR ', ')
                AS skills_list,
            ROUND(AVG(r.stars), 2)                                    AS avg_rating,
            COUNT(DISTINCT r.rating_id)                               AS total_reviews,
            COUNT(DISTINCT CASE WHEN b.status = 'completed'
                                THEN b.booking_id END)                AS completed_jobs
        FROM users u
        INNER JOIN worker_profiles wp ON wp.user_id   = u.user_id
        LEFT  JOIN ratings         r  ON r.worker_id  = u.user_id
        LEFT  JOIN bookings        b  ON b.worker_id  = u.user_id
        LEFT  JOIN worker_skills   ws ON ws.worker_id = u.user_id
        LEFT  JOIN skills          s  ON s.skill_id   = ws.skill_id
        WHERE u.role = 'worker'
        GROUP BY
            u.user_id, u.full_name, u.phone,
            wp.hourly_rate, wp.availability_status
        ORDER BY avg_rating DESC, completed_jobs DESC
        LIMIT 10
    """)
    top_workers = cursor.fetchall()

    # ── Query 2: Revenue Summary ──────────────────────────────────────────
    # Total revenue, average booking value, and max booking value for all
    # bookings that have reached 'completed' status. Uses SUM(), AVG(), MAX().
    cursor.execute("""
        SELECT
            COUNT(*)                  AS total_completed_bookings,
            COALESCE(SUM(total_amount),         0.00) AS total_revenue,
            COALESCE(ROUND(AVG(total_amount), 2), 0.00) AS avg_booking_value,
            COALESCE(MAX(total_amount),         0.00) AS max_booking_value,
            COALESCE(MIN(total_amount),         0.00) AS min_booking_value
        FROM bookings
        WHERE status = 'completed'
    """)
    revenue_stats = cursor.fetchone()

    # ── Query 3: Platform Commission Breakdown ────────────────────────────
    # Total commission earned, split by booking status so the admin can see
    # pending/confirmed amounts that may still be at risk. Uses SUM() with
    # conditional CASE expressions and GROUP BY status.
    cursor.execute("""
        SELECT
            status,
            COUNT(*)                          AS booking_count,
            COALESCE(SUM(total_amount), 0.00)          AS status_revenue,
            COALESCE(SUM(platform_commission), 0.00)   AS status_commission
        FROM bookings
        GROUP BY status
        ORDER BY FIELD(status, 'completed', 'confirmed', 'pending', 'cancelled')
    """)
    commission_by_status = cursor.fetchall()

    # Aggregate totals for commission KPI cards
    cursor.execute("""
        SELECT
            COALESCE(SUM(platform_commission), 0.00)                              AS total_commission,
            COALESCE(SUM(CASE WHEN status = 'completed'
                         THEN platform_commission ELSE 0 END), 0.00)   AS earned_commission,
            COALESCE(SUM(CASE WHEN status IN ('pending','confirmed')
                         THEN platform_commission ELSE 0 END), 0.00)   AS pending_commission
        FROM bookings
    """)
    commission_totals = cursor.fetchone()

    # ── Bonus: Platform-wide user & booking summary ───────────────────────
    cursor.execute("""
        SELECT
            COUNT(*)                                                AS total_users,
            SUM(CASE WHEN role = 'customer' THEN 1 ELSE 0 END)     AS total_customers,
            SUM(CASE WHEN role = 'worker'   THEN 1 ELSE 0 END)     AS total_workers
        FROM users
        WHERE role IN ('customer', 'worker')
    """)
    user_stats = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        top_workers=top_workers,
        revenue_stats=revenue_stats,
        commission_by_status=commission_by_status,
        commission_totals=commission_totals,
        user_stats=user_stats,
    )


# ──────────────────────────────────────────────
#  RUN
# ──────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)


