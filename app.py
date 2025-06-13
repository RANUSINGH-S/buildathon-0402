import streamlit as st
import pandas as pd
from gtts import gTTS
import os

# Title
st.title("SmartCare - Digital Appointment Scheduler")

# Collect user inputs
st.subheader("Book Your Appointment")
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

    st.success(f"Appointment booked with {doctor} at {time} on {date}")

    # gTTS Voice Confirmation
    tts = gTTS(f"Appointment booked with {doctor} at {time} on {date}")
    tts.save("confirm.mp3")
    audio_file = open("confirm.mp3", "rb")
    st.audio(audio_file.read(), format="audio/mp3")
with st.sidebar:
    st.subheader("Admin Panel")
    if st.button("View All Appointments"):
        if os.path.exists("appointments.csv"):
            data = pd.read_csv("appointments.csv")
            st.dataframe(data)
        else:
            st.info("No appointments yet.")
