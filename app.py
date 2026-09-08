from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

DATABASE = "patient_health.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_database():

    conn = get_db()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # PATIENTS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # VITALS TABLE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            blood_pressure TEXT NOT NULL,
            heart_rate REAL NOT NULL,
            oxygen_level REAL NOT NULL,
            temperature REAL NOT NULL,
            glucose REAL,
            thyroid REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)

    # --------------------------------------------------------
    # ADD DEFAULT PATIENT IF DATABASE IS EMPTY
    # --------------------------------------------------------

    cursor.execute("SELECT COUNT(*) FROM patients")
    count = cursor.fetchone()[0]

    if count == 0:

        cursor.execute("""
            INSERT INTO patients
            (name, age, gender, email, phone, password)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            "Swati",
            21,
            "Female",
            "swati@gmail.com",
            "9876543210",
            "123456"
        ))

        print("Default patient created.")
        print("Email: swati@gmail.com")
        print("Password: 123456")

    conn.commit()
    conn.close()


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# HEALTH CHECK API
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "success",
        "message": "Patient Health Monitoring API is running"
    })


# ============================================================
# LOGIN API
# ============================================================

@app.route("/api/login", methods=["POST"])
def login():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No data received"
            }), 400

        email = data.get("email", "").strip()
        password = data.get("password", "")

        if not email or not password:

            return jsonify({
                "status": "error",
                "message": "Email and password are required"
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, age, gender, email, phone
            FROM patients
            WHERE email = ? AND password = ?
        """, (email, password))

        patient = cursor.fetchone()

        conn.close()

        if patient is None:

            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401

        patient_data = {
            "id": patient["id"],
            "name": patient["name"],
            "age": patient["age"],
            "gender": patient["gender"],
            "email": patient["email"],
            "phone": patient["phone"]
        }

        return jsonify({
            "status": "success",
            "message": "Login successful",
            "patient": patient_data
        }), 200

    except Exception as e:

        print("LOGIN ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Server error during login"
        }), 500


# ============================================================
# GET PATIENT INFORMATION
# ============================================================

@app.route("/api/patient/<int:patient_id>", methods=["GET"])
def get_patient(patient_id):

    try:

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, age, gender, email, phone
            FROM patients
            WHERE id = ?
        """, (patient_id,))

        patient = cursor.fetchone()

        conn.close()

        if patient is None:

            return jsonify({
                "status": "error",
                "message": "Patient not found"
            }), 404

        return jsonify({
            "status": "success",
            "patient": {
                "id": patient["id"],
                "name": patient["name"],
                "age": patient["age"],
                "gender": patient["gender"],
                "email": patient["email"],
                "phone": patient["phone"]
            }
        })

    except Exception as e:

        print("PATIENT ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Unable to get patient information"
        }), 500


# ============================================================
# ADD VITAL RECORD
# ============================================================

@app.route("/api/vitals", methods=["POST"])
def add_vitals():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "status": "error",
                "message": "No data received"
            }), 400

        patient_id = data.get("patient_id")
        blood_pressure = data.get("blood_pressure")
        heart_rate = data.get("heart_rate")
        oxygen_level = data.get("oxygen_level")
        temperature = data.get("temperature")
        glucose = data.get("glucose")
        thyroid = data.get("thyroid")

        # Required fields
        if (
            patient_id is None
            or not blood_pressure
            or heart_rate is None
            or oxygen_level is None
            or temperature is None
        ):

            return jsonify({
                "status": "error",
                "message": "Required vital information is missing"
            }), 400

        # Convert numeric values
        try:

            patient_id = int(patient_id)
            heart_rate = float(heart_rate)
            oxygen_level = float(oxygen_level)
            temperature = float(temperature)

            if glucose is not None and glucose != "":
                glucose = float(glucose)
            else:
                glucose = None

            if thyroid is not None and thyroid != "":
                thyroid = float(thyroid)
            else:
                thyroid = None

        except ValueError:

            return jsonify({
                "status": "error",
                "message": "Invalid numeric value"
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # Check patient
        cursor.execute(
            "SELECT id FROM patients WHERE id = ?",
            (patient_id,)
        )

        patient = cursor.fetchone()

        if patient is None:

            conn.close()

            return jsonify({
                "status": "error",
                "message": "Patient not found"
            }), 404

        created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
            INSERT INTO vitals
            (
                patient_id,
                blood_pressure,
                heart_rate,
                oxygen_level,
                temperature,
                glucose,
                thyroid,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            patient_id,
            blood_pressure,
            heart_rate,
            oxygen_level,
            temperature,
            glucose,
            thyroid,
            created_at
        ))

        conn.commit()

        vital_id = cursor.lastrowid

        conn.close()

        return jsonify({
            "status": "success",
            "message": "Health record saved successfully",
            "vital_id": vital_id
        }), 201

    except Exception as e:

        print("ADD VITAL ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Unable to save health record"
        }), 500


# ============================================================
# GET ALL VITALS FOR PATIENT
# ============================================================

@app.route("/api/vitals/<int:patient_id>", methods=["GET"])
def get_vitals(patient_id):

    try:

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                blood_pressure,
                heart_rate,
                oxygen_level,
                temperature,
                glucose,
                thyroid,
                created_at
            FROM vitals
            WHERE patient_id = ?
            ORDER BY id DESC
        """, (patient_id,))

        rows = cursor.fetchall()

        conn.close()

        vitals = []

        for row in rows:

            vitals.append({
                "id": row["id"],
                "blood_pressure": row["blood_pressure"],
                "heart_rate": row["heart_rate"],
                "oxygen_level": row["oxygen_level"],
                "temperature": row["temperature"],
                "glucose": row["glucose"],
                "thyroid": row["thyroid"],
                "created_at": row["created_at"]
            })

        return jsonify({
            "status": "success",
            "vitals": vitals
        })

    except Exception as e:

        print("GET VITALS ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Unable to load vital records"
        }), 500


# ============================================================
# GET LATEST VITAL
# ============================================================

@app.route("/api/vitals/latest/<int:patient_id>", methods=["GET"])
def latest_vital(patient_id):

    try:

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                blood_pressure,
                heart_rate,
                oxygen_level,
                temperature,
                glucose,
                thyroid,
                created_at
            FROM vitals
            WHERE patient_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (patient_id,))

        row = cursor.fetchone()

        conn.close()

        if row is None:

            return jsonify({
                "status": "success",
                "vital": None,
                "message": "No health records available"
            })

        vital = {
            "id": row["id"],
            "blood_pressure": row["blood_pressure"],
            "heart_rate": row["heart_rate"],
            "oxygen_level": row["oxygen_level"],
            "temperature": row["temperature"],
            "glucose": row["glucose"],
            "thyroid": row["thyroid"],
            "created_at": row["created_at"]
        }

        return jsonify({
            "status": "success",
            "vital": vital
        })

    except Exception as e:

        print("LATEST VITAL ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Unable to load latest vital"
        }), 500


# ============================================================
# SIMPLE HEALTH STATUS
# ============================================================

@app.route("/api/status/<int:patient_id>", methods=["GET"])
def health_status(patient_id):

    try:

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                blood_pressure,
                heart_rate,
                oxygen_level,
                temperature,
                glucose,
                thyroid
            FROM vitals
            WHERE patient_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (patient_id,))

        row = cursor.fetchone()

        conn.close()

        if row is None:

            return jsonify({
                "status": "success",
                "health_status": "No data",
                "message": "No vital information available"
            })

        warnings = []

        # Heart rate
        if row["heart_rate"] < 60 or row["heart_rate"] > 100:
            warnings.append("Heart rate is outside the typical adult resting range")

        # Oxygen
        if row["oxygen_level"] < 95:
            warnings.append("Oxygen level is below the typical range")

        # Temperature
        if row["temperature"] < 36 or row["temperature"] > 37.5:
            warnings.append("Temperature is outside the typical range")

        # Blood pressure
        bp = row["blood_pressure"]

        try:

            systolic, diastolic = bp.split("/")

            systolic = float(systolic)
            diastolic = float(diastolic)

            if systolic >= 140 or diastolic >= 90:
                warnings.append("Blood pressure is high")

            elif systolic < 90 or diastolic < 60:
                warnings.append("Blood pressure is low")

        except Exception:
            pass

        if warnings:

            return jsonify({
                "status": "success",
                "health_status": "Attention",
                "message": " | ".join(warnings),
                "warnings": warnings
            })

        return jsonify({
            "status": "success",
            "health_status": "Normal",
            "message": "Vital information is within the typical range",
            "warnings": []
        })

    except Exception as e:

        print("STATUS ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Unable to calculate health status"
        }), 500


# ============================================================
# API 404 HANDLER
# ============================================================

@app.errorhandler(404)
def not_found(error):

    if request.path.startswith("/api/"):

        return jsonify({
            "status": "error",
            "message": "API endpoint not found"
        }), 404

    return "Page not found", 404


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    init_database()

    print("=" * 60)
    print("PATIENT HEALTH MONITORING SYSTEM")
    print("=" * 60)
    print("Server: http://127.0.0.1:5000")
    print("Health API: http://127.0.0.1:5000/api/health")
    print("")
    print("LOGIN DETAILS")
    print("Email: swati@gmail.com")
    print("Password: 123456")
    print("=" * 60)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )