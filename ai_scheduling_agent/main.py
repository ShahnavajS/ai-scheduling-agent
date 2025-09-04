import sqlite3
import os
import sys

DB_PATH = "data/clinic.db"

def init_db(force_reset=False):
    """Create database and seed sample data."""
    os.makedirs("data", exist_ok=True)

    # If DB exists and we didn't ask to reset, just return
    if os.path.exists(DB_PATH) and not force_reset:
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Drop old tables if resetting
    c.execute("DROP TABLE IF EXISTS patients")
    c.execute("DROP TABLE IF EXISTS doctors")
    c.execute("DROP TABLE IF EXISTS schedules")
    c.execute("DROP TABLE IF EXISTS appointments")

    # Tables
    c.execute("""
    CREATE TABLE patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        dob TEXT,
        doctor TEXT,
        patient_type TEXT,
        insurance TEXT
    )""")

    c.execute("""
    CREATE TABLE doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )""")

    c.execute("""
    CREATE TABLE schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor TEXT,
        date TEXT,
        time TEXT,
        available INTEGER
    )""")

    c.execute("""
    CREATE TABLE appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        doctor TEXT,
        date TEXT,
        time TEXT,
        patient_type TEXT
    )""")

    # Seed data
    c.executemany("INSERT INTO doctors (name) VALUES (?)",
                  [("Dr. Smith",), ("Dr. Lee",)])

    patients = [
        ("John Doe", "1990-05-14", "Dr. Smith", "returning", "Aetna"),
        ("Jane Smith", "1985-09-22", "Dr. Lee", "returning", "BlueCross"),
    ]
    c.executemany(
        "INSERT INTO patients (name, dob, doctor, patient_type, insurance) VALUES (?, ?, ?, ?, ?)",
        patients
    )

    schedules = [
        ("Dr. Smith", "2025-09-05", "09:00", 1),
        ("Dr. Smith", "2025-09-05", "10:00", 1),
        ("Dr. Lee",   "2025-09-05", "11:00", 1),
        ("Dr. Lee",   "2025-09-05", "14:00", 1),
    ]
    c.executemany(
        "INSERT INTO schedules (doctor, date, time, available) VALUES (?, ?, ?, ?)",
        schedules
    )

    conn.commit()
    conn.close()

def find_patient_type(name: str, dob: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT patient_type FROM patients WHERE name=? AND dob=?", (name, dob))
    row = c.fetchone()
    conn.close()
    return row[0] if row else "new"

def list_doctors():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM doctors ORDER BY name")
    docs = [r[0] for r in c.fetchall()]
    conn.close()
    return docs

def list_available_slots(doctor: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT id, date, time FROM schedules
        WHERE doctor=? AND available=1
        ORDER BY date, time
    """, (doctor,))
    rows = c.fetchall()
    conn.close()
    return rows  # (id, date, time)

def book_appointment(name, doctor, date, time, p_type):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO appointments (name, doctor, date, time, patient_type) VALUES (?, ?, ?, ?, ?)",
        (name, doctor, date, time, p_type)
    )
    c.execute(
        "UPDATE schedules SET available=0 WHERE doctor=? AND date=? AND time=?",
        (doctor, date, time)
    )
    conn.commit()
    conn.close()

def main():
    # Create DB on first run, or reset if --reset provided
    force_reset = ("--reset" in sys.argv)
    init_db(force_reset=force_reset)
    if force_reset:
        print("🔁 Database reset complete.\n")

    print("=== AI Scheduling Agent (Console) ===\n")

    # 1) Greet + identify patient
    name = input("Enter your full name: ").strip()
    dob  = input("Enter your DOB (YYYY-MM-DD): ").strip()
    p_type = find_patient_type(name, dob)
    duration = 60 if p_type == "new" else 30
    print(f"\nPatient Type: {p_type}  |  Recommended duration: {duration} minutes\n")

    # 2) Choose doctor
    doctors = list_doctors()
    if not doctors:
        print("No doctors found. Exiting.")
        return

    print("Available Doctors:")
    for i, d in enumerate(doctors, start=1):
        print(f"  {i}. {d}")
    while True:
        try:
            choice = int(input("Choose a doctor (number): "))
            if 1 <= choice <= len(doctors):
                doctor = doctors[choice - 1]
                break
        except ValueError:
            pass
        print("Invalid choice, try again.")

    # 3) See available slots for that doctor
    slots = list_available_slots(doctor)
    if not slots:
        print(f"\nNo available slots for {doctor}.")
        return

    print(f"\nAvailable slots for {doctor}:")
    for i, (_, date, time) in enumerate(slots, start=1):
        print(f"  {i}. {date} at {time}")

    while True:
        try:
            s_idx = int(input("Choose a slot (number): "))
            if 1 <= s_idx <= len(slots):
                _, date, time = slots[s_idx - 1]
                break
        except ValueError:
            pass
        print("Invalid choice, try again.")

    # 4) Book appointment
    book_appointment(name, doctor, date, time, p_type)
    print("\n✅ Appointment booked!")
    print(f"   Patient: {name}")
    print(f"   Doctor : {doctor}")
    print(f"   When   : {date} at {time}")
    print(f"   Type   : {p_type} ({duration} mins)\n")

    print("📄 Intake form: place 'New Patient Intake Form.pdf' in this folder and share it with the patient.")
    print("💾 Data saved to:", DB_PATH)

if __name__ == "__main__":
    main()
