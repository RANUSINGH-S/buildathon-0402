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
    name = st.text_input("Patient Name")
    email = st.text_input("Email")
    doctor = st.selectbox("Select Doctor", ["Dr. Sharma", "Dr. Verma", "Dr. Aisha"])
    date = st.date_input("Appointment Date")
    time_slot_map = {
        "Dr. Sharma": ["10:00 AM", "11:00 AM"],
        "Dr. Verma": ["12:00 PM", "3:00 PM"],
        "Dr. Aisha": ["1:00 PM", "4:00 PM"]
    }
    time = st.selectbox("Time Slot", time_slot_map[doctor])

    if st.button("Book Appointment"):
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
            qr = qrcode.make(f"{name}, {doctor}, {date}, {time}")
            qr_path = "qr_code.png"
            qr.save(qr_path)

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
                    smtp.login('ctr_alt_algo@gmail.com', 'Raman2004@ok')  # use app-specific password
                    smtp.send_message(msg)
                st.success("📧 Email sent!")
            except:
                st.warning("⚠️ Email failed to send.")

        st.success(f"✅ Appointment booked with {doctor} at {time} on {date}")

# --- Admin Panel Section ---
elif menu == "🧾 View Appointments":
    st.title("🔐 Admin Login")
    pwd = st.text_input("Enter admin password", type="password")

    # ✅ Initialize rerun flag once
    if "rerun_flag" not in st.session_state:
        st.session_state.rerun_flag = False

    if pwd == "smartcare123":
        st.success("Access granted ✅")

        if os.path.exists("appointments.csv"):
            df = pd.read_csv("appointments.csv")
            df["date"] = pd.to_datetime(df["date"])

            selected_date = st.date_input("📅 Filter appointments by date")
            filtered_df = df[df["date"].dt.date == selected_date]

            st.subheader("📋 Appointments")
            st.write(f"👥 Total appointments for {selected_date}: {len(filtered_df)}")

            for i, row in filtered_df.iterrows():
                st.write(f"👤 {row['name']} - {row['doctor']} - {row['date'].strftime('%Y-%m-%d')} at {row['time']}")
                if st.button(f"Cancel #{i}", key=f"cancel_{i}"):
                    df.drop(i, inplace=True)
                    df.to_csv("appointments.csv", index=False)
                    st.success("❌ Appointment cancelled.")
                    st.session_state.rerun_flag = True

            # ✅ Safe rerun trigger
            if st.session_state.rerun_flag:
                st.session_state.rerun_flag = False
                st.experimental_rerun()
        else:
            st.info("No appointments found.")
    else:
        st.warning("Access denied ❌")

# --- Contact Us Section ---
elif menu == "📞 Contact Us":
    st.title("📞 Contact Us")
    st.markdown("We’d love to hear from you. Please leave your message below.")

    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    message = st.text_area("Your Message")

    if st.button("Send Message"):
        contact = pd.DataFrame([[name, email, message]],
                               columns=["name", "email", "message"])

        if os.path.exists("contact_messages.csv"):
            df = pd.read_csv("contact_messages.csv")
            df = pd.concat([df, contact], ignore_index=True)
        else:
            df = contact

        df.to_csv("contact_messages.csv", index=False)
        st.success("✅ Thank you! Your message has been received.")

# ✅ Ensure folders exist
os.makedirs("temp", exist_ok=True)
os.makedirs("images", exist_ok=True)
