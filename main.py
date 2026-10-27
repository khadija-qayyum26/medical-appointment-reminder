
import streamlit as st
import sqlite3
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# ---------------- CONFIGURATION ----------------
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

st.set_page_config(
    page_title="Medical Appointment Reminder",
    page_icon="🏥",
    layout="wide"
)

DB_PATH = BASE_DIR / "appointments.db"


# ---------------- API KEY SETUP ----------------
def get_api_key():
    # First, try the local .env file
    api_key = os.getenv("GROQ_API_KEY", "").strip()

    # If not found, try Streamlit Cloud Secrets
    if not api_key:
        try:
            api_key = str(
                st.secrets["GROQ_API_KEY"]
            ).strip()
        except (KeyError, FileNotFoundError):
            api_key = ""

    return api_key


# ---------------- DATABASE SETUP ----------------
def create_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            phone TEXT,
            doctor_name TEXT,
            appointment_datetime TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    conn.commit()
    conn.close()


create_db()


# ---------------- APP TITLE ----------------
st.title("🏥 Medical Appointment Reminder System")
st.write("Manage patient appointments and AI reminders.")


# ---------------- ADD APPOINTMENT ----------------
st.subheader("➕ Add New Appointment")

with st.form("appointment_form"):
    name = st.text_input("Patient Name")
    phone = st.text_input("Phone Number")
    doctor = st.text_input("Doctor Name")
    date_time = st.text_input(
        "Appointment Date & Time",
        placeholder="2026-10-25 10:30"
    )

    submitted = st.form_submit_button("Add Appointment")

    if submitted:
        if all([
            name.strip(),
            phone.strip(),
            doctor.strip(),
            date_time.strip()
        ]):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO appointments
                (patient_name, phone, doctor_name, appointment_datetime)
                VALUES (?, ?, ?, ?)
            """, (
                name.strip(),
                phone.strip(),
                doctor.strip(),
                date_time.strip()
            ))

            conn.commit()
            conn.close()

            st.success("Appointment added successfully!")
            st.rerun()
        else:
            st.error("Please fill in all fields.")


# ---------------- VIEW APPOINTMENTS ----------------
st.subheader("📋 Saved Appointments")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, patient_name, phone, doctor_name,
           appointment_datetime, status
    FROM appointments
    ORDER BY id DESC
""")

rows = cursor.fetchall()
conn.close()

if rows:
    st.dataframe(
        [
            {
                "ID": row[0],
                "Patient": row[1],
                "Phone": row[2],
                "Doctor": row[3],
                "Date & Time": row[4],
                "Status": row[5]
            }
            for row in rows
        ],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No appointments added yet.")


# ---------------- UPDATE STATUS ----------------
st.subheader("✏️ Update Appointment Status")

if rows:
    appointment_options = {
        f"ID {row[0]} - {row[1]} ({row[4]})": row[0]
        for row in rows
    }

    selected_appointment = st.selectbox(
        "Select Appointment",
        list(appointment_options.keys()),
        key="status_appointment"
    )

    new_status = st.selectbox(
        "Select New Status",
        ["Pending", "Confirmed", "Cancelled"],
        key="new_status"
    )

    if st.button("Update Status"):
        appointment_id = appointment_options[selected_appointment]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE appointments SET status = ? WHERE id = ?",
            (new_status, appointment_id)
        )

        conn.commit()
        conn.close()

        st.success("Appointment status updated!")
        st.rerun()
else:
    st.info("Please add an appointment first.")


# ---------------- AI APPOINTMENT REMINDER ----------------
st.subheader("🤖 AI Appointment Reminder")

if rows:
    reminder_options = {
        f"ID {row[0]} - {row[1]} ({row[4]})": row
        for row in rows
    }

    selected_reminder = st.selectbox(
        "Select patient for AI reminder",
        list(reminder_options.keys()),
        key="ai_reminder_select"
    )

    if st.button("Generate AI Reminder"):
        api_key = get_api_key()

        if not api_key:
            st.error(
                "API key not found. Please add GROQ_API_KEY "
                "in Streamlit Secrets or your local .env file."
            )
        else:
            appointment = reminder_options[selected_reminder]

            try:
                client = Groq(api_key=api_key)

                with st.spinner("AI is writing the reminder..."):
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "Write a short, polite appointment "
                                    "reminder in simple English. Do not "
                                    "give medical advice. Do not claim "
                                    "that the message has been sent."
                                )
                            },
                            {
                                "role": "user",
                                "content": (
                                    f"Patient: {appointment[1]}\n"
                                    f"Doctor: {appointment[3]}\n"
                                    f"Appointment date and time: "
                                    f"{appointment[4]}\n"
                                    f"Status: {appointment[5]}\n"
                                    "Write a reminder message for this appointment."
                                )
                            }
                        ],
                        temperature=0.5,
                        max_tokens=200
                    )

                reminder_message = response.choices[0].message.content

                st.success("AI reminder generated!")
                st.text_area(
                    "Generated Reminder Message",
                    value=reminder_message,
                    height=150
                )

                st.caption(
                    "This message has been generated for review. "
                    "It has not been sent to the patient."
                )

            except Exception as e:
                st.error("AI reminder could not be generated.")
                st.write("Error type:", type(e).__name__)

                error_message = str(e).replace(
                    api_key, "[HIDDEN API KEY]"
                )
                st.code(error_message)

else:
    st.info("Add an appointment first to generate an AI reminder.")
