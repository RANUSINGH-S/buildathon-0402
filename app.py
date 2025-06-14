import streamlit as st
import pandas as pd
from gtts import gTTS
import os
from datetime import datetime
import qrcode
from io import BytesIO
from fpdf import FPDF
import smtplib
from email.message import EmailMessage

import os

file_path = "contact_messages.csv"

if not os.path.exists(file_path):
    with open(file_path, "w") as f:
        f.write("name,email,message,timestamp\n")


# ✅ Must be the first Streamlit command
st.set_page_config(page_title="SmartCare", layout="centered")

# ✅ Custom CSS Styling
st.markdown("""
    <style>
    .main {
        background-color: #f8fbff;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 {
        color: #004080;
    }
    .stButton button {
        background-color: #0077cc;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stTextInput>div>div>input {
        border: 1px solid #ccc;
        border-radius: 6px;
    }
    [data-testid="stSidebar"] {
        background-color: #e7f1ff;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.title("SmartCare Navigation")
menu = st.sidebar.radio("Go to", ["🏠 Home", "📅 Book Appointment", "🧾 View Appointments", "📞 Contact Us"])

# --- Home Section ---
if menu == "🏠 Home":
    st.title("🏥 Welcome to SmartCare")
    st.image("images/image.png", use_container_width=True)
    st.markdown("""
        ## Your Digital Health Assistant
        **SmartCare** helps hospitals reduce wait times by allowing patients to book appointments online.

        🔹 Book appointments in seconds  
        🔹 Instant voice confirmation  
        🔹 Admin panel to view all bookings  
        🔹 PDF receipt with QR code

        ---
        👇 Use the sidebar to navigate
    """)

# --- Book Appointment Section ---
elif menu == "📅 Book Appointment":
    st.title("📅 Book Your Appointment")
    name = st.text_input("Patient Name", key="patient_name")
    email = st.text_input("Email", key="patient_email")
    doctor = st.selectbox("Select Doctor", ["Dr. Sharma", "Dr. Verma", "Dr. Aisha"], key="doctor_select")
    date = st.date_input("Appointment Date", key="appt_date")
    time_slot_map = {
        "Dr. Sharma": ["10:00 AM", "11:00 AM"],
        "Dr. Verma": ["12:00 PM", "3:00 PM"],
        "Dr. Aisha": ["1:00 PM", "4:00 PM"]
    }
    time = st.selectbox("Time Slot", time_slot_map[doctor], key="time_slot")

    if st.button("Book Appointment", key="book_button"):
        with st.spinner("Booking your appointment..."):
            new_data = pd.DataFrame([[name, email, doctor, date, time]],
                                    columns=["name", "email", "doctor", "date", "time"])

            if os.path.exists("appointments.csv"):
                df = pd.read_csv("appointments.csv")
                df = pd.concat([df, new_data], ignore_index=True)
            else:
                df = new_data

            df.to_csv("appointments.csv", index=False)

            # ✅ Voice Confirmation
            tts = gTTS(f"Appointment booked with {doctor} at {time} on {date}")
            tts.save("confirm.mp3")
            audio_file = open("confirm.mp3", "rb")
            st.audio(audio_file.read(), format="audio/mp3")

            # ✅ QR Code Generation
            import os
            if not os.path.exists("qrcodes"):
                os.makedirs("qrcodes")

            # 📦 Create QR content dataset
            qr_data = f"Patient: {name}\nDoctor: {doctor}\nDate: {date}\nTime: {time}"
            qr = qrcode.make(qr_data)

            # Save QR with a unique filename
            qr_path = f"qrcodes/{name}_{date}_{time}.png".replace(":", "-")
            qr.save(qr_path)
            st.success("✅ QR Code Generated!")
            st.image(qr_path, caption="Appointment QR Code", use_column_width=True)

            # ✅ PDF Receipt with QR from file
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="SmartCare Appointment Receipt", ln=True, align='C')
            pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
            pdf.cell(200, 10, txt=f"Doctor: {doctor}", ln=True)
            pdf.cell(200, 10, txt=f"Date: {date}", ln=True)
            pdf.cell(200, 10, txt=f"Time: {time}", ln=True)
            pdf.image(qr_path, x=80, y=60, w=50)
            pdf.output("receipt.pdf")

            # ✅ Email Notification
            try:
                msg = EmailMessage()
                msg['Subject'] = 'SmartCare Appointment Confirmation'
                msg['From'] = 'ctr_alt_algo@gmail.com'
                msg['To'] = email
                msg.set_content(f"Appointment booked with {doctor} at {time} on {date}")
                with open("receipt.pdf", 'rb') as f:
                    msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename="receipt.pdf")

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login('ctr_alt_algo@gmail.com', 'Raman2004@ok')  # Use app password here
                    smtp.send_message(msg)
                st.success("📧 Email sent!")
            except:
                st.warning("⚠️ Email failed to send.")

        st.success(f"✅ Appointment booked with {doctor} at {time} on {date}")


# ✅ Ensure folders exist
os.makedirs("temp", exist_ok=True)
os.makedirs("images", exist_ok=True)
