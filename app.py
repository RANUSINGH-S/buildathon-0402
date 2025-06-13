import streamlit as st
import pandas as pd
from gtts import gTTS
import os

# --- Basic Setup ---
st.set_page_config(page_title="SmartCare", layout="centered")

# --- Sidebar Navigation ---
st.sidebar.title("SmartCare Navigation")
menu = st.sidebar.radio("Go to", ["🏠 Home", "📅 Book Appointment", "🧾 View Appointments", "📞 Contact Us"])

# --- Home Section ---
if menu == "🏠 Home":
    st.title("🏥 Welcome to SmartCare")
    st.image("https://cdn.pixabay.com/photo/2017/01/31/13/14/medical-2027777_1280.png", use_column_width=True)
    st.markdown("""
        ## Your Digital Health Assistant
        **SmartCare** helps hospitals reduce wait times by allowing patients to book appointments online.
        
        🔹 Book appointments in seconds  
        🔹 Instant voice confirmation  
        🔹 Admin panel to view all bookings  

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
    time = st.selectbox("Time Slot", ["10:00 AM", "11:00 AM", "12:00 PM", "3:00 PM"])

    if st.button("Book Appointment"):
        new_data = pd.DataFrame([[name, email, doctor, date, time]],
                                columns=["name", "email", "doctor", "date", "time"])
        
        if os.path.exists("appointments.csv"):
            df = pd.read_csv("appointments.csv")
            df = pd.concat([df, new_data], ignore_index=True)
        else:
            df = new_data

        df.to_csv("appointments.csv", index=False)
        st.success(f"✅ Appointment booked with {doctor} at {time} on {date}")

        # Voice Confirmation
        tts = gTTS(f"Appointment booked with {doctor} at {time} on {date}")
        tts.save("confirm.mp3")
        audio_file = open("confirm.mp3", "rb")
        st.audio(audio_file.read(), format="audio/mp3")

# --- Admin Panel Section ---
elif menu == "🧾 View Appointments":
    st.title("🧾 All Booked Appointments")
    if os.path.exists("appointments.csv"):
        df = pd.read_csv("appointments.csv")
        st.dataframe(df)
    else:
        st.info("No appointments found.")
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


